"""
Raw Document Store
Implements the persistent Raw Document Store component for the BIS NAVIC pipeline.
Stores raw artifacts (JSON, HTML, PDF) to blob/filesystem storage while cataloging
full metadata and SHA-256 hashes into a structured SQLite/PostgreSQL database
for downstream Change Detection and RAG processing.
"""

import os
import json
import sqlite3
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_STORAGE_DIR = os.path.join(BASE_DIR, "raw_store")
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "raw_documents.db")


class RawDocumentStore:
    def __init__(self, storage_dir: str = DEFAULT_STORAGE_DIR, db_path: str = DEFAULT_DB_PATH):
        self.storage_dir = storage_dir
        self.db_path = db_path
        os.makedirs(self.storage_dir, exist_ok=True)
        self.init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Create the raw_documents table and indexes if they do not exist."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS raw_documents (
                    doc_id TEXT PRIMARY KEY,
                    source_domain TEXT NOT NULL,
                    category TEXT NOT NULL,
                    source_url TEXT NOT NULL,
                    doc_name TEXT NOT NULL,
                    doc_type TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    metadata_json TEXT,
                    status TEXT DEFAULT 'stored',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_source_url ON raw_documents(source_url);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON raw_documents(category);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_content_hash ON raw_documents(content_hash);")
            conn.commit()

    @staticmethod
    def compute_hash(data: bytes) -> str:
        """Compute SHA-256 hash of raw bytes."""
        return hashlib.sha256(data).hexdigest()

    def has_document(self, source_url: str) -> bool:
        """Check if a document with this source URL already exists in the store."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT 1 FROM raw_documents WHERE source_url = ?",
                (source_url,)
            ).fetchone()
            return row is not None

    def check_change(self, source_url: str, new_content: bytes) -> Tuple[bool, Optional[str]]:
        """
        Check if the incoming document content has changed relative to stored version.
        Returns:
            (is_changed, previous_hash)
            - If new document: (True, None)
            - If existing and identical: (False, existing_hash)
            - If existing and modified: (True, existing_hash)
        """
        new_hash = self.compute_hash(new_content)
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT content_hash FROM raw_documents WHERE source_url = ?",
                (source_url,)
            ).fetchone()
            if not row:
                return True, None
            prev_hash = row["content_hash"]
            return (prev_hash != new_hash), prev_hash

    def store_document(
        self,
        source_domain: str,
        category: str,
        source_url: str,
        doc_name: str,
        content: bytes,
        doc_type: str = "json",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Save raw document to disk and record metadata in database.
        """
        content_hash = self.compute_hash(content)
        now = datetime.utcnow().isoformat()
        
        # Subdirectory per category
        category_dir = os.path.join(self.storage_dir, category)
        os.makedirs(category_dir, exist_ok=True)
        
        # Generate safe unique filename using hash prefix
        safe_name = "".join(c if c.isalnum() or c in ("-", "_", ".") else "_" for c in doc_name)
        if not safe_name.endswith(f".{doc_type}"):
            safe_name += f".{doc_type}"
        file_name = f"{content_hash[:12]}_{safe_name}"
        rel_file_path = os.path.join(category, file_name)
        abs_file_path = os.path.join(self.storage_dir, rel_file_path)

        # Write blob
        with open(abs_file_path, "wb") as f:
            f.write(content)

        doc_id = hashlib.sha256(f"{source_url}:{category}".encode("utf-8")).hexdigest()
        meta_str = json.dumps(metadata or {}, ensure_ascii=False)

        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO raw_documents (
                    doc_id, source_domain, category, source_url, doc_name,
                    doc_type, content_hash, file_path, file_size, metadata_json,
                    status, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'stored', ?)
                ON CONFLICT(doc_id) DO UPDATE SET
                    content_hash = excluded.content_hash,
                    file_path = excluded.file_path,
                    file_size = excluded.file_size,
                    metadata_json = excluded.metadata_json,
                    status = CASE 
                        WHEN raw_documents.content_hash != excluded.content_hash THEN 'changed'
                        ELSE 'unchanged'
                    END,
                    updated_at = excluded.updated_at
            """, (
                doc_id, source_domain, category, source_url, doc_name,
                doc_type, content_hash, rel_file_path, len(content),
                meta_str, now
            ))
            conn.commit()

        return {
            "doc_id": doc_id,
            "category": category,
            "source_url": source_url,
            "content_hash": content_hash,
            "file_size": len(content),
            "file_path": rel_file_path
        }

    def get_stats(self) -> Dict[str, Any]:
        """Return counts and aggregate storage statistics."""
        with self._get_connection() as conn:
            total_docs = conn.execute("SELECT COUNT(*) FROM raw_documents").fetchone()[0]
            total_size = conn.execute("SELECT COALESCE(SUM(file_size), 0) FROM raw_documents").fetchone()[0]
            
            by_category = {}
            for r in conn.execute("SELECT category, COUNT(*) as c, SUM(file_size) as s FROM raw_documents GROUP BY category"):
                by_category[r["category"]] = {"count": r["c"], "total_bytes": r["s"]}
                
            by_source = {}
            for r in conn.execute("SELECT source_domain, COUNT(*) as c FROM raw_documents GROUP BY source_domain"):
                by_source[r["source_domain"]] = r["c"]

            return {
                "total_documents": total_docs,
                "total_storage_bytes": total_size,
                "total_storage_mb": round(total_size / (1024 * 1024), 2),
                "by_category": by_category,
                "by_source": by_source,
                "storage_directory": self.storage_dir,
                "db_path": self.db_path
            }
