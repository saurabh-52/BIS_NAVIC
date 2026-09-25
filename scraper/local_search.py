"""
BIS NAVIC — Local Standards Search Engine
Provides full-text search over locally stored standard detail JSON files
from the Raw Document Store. No external vector DB dependency.
"""

import os
import json
import sqlite3
import re
from typing import List, Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_STORE_DIR = os.path.join(BASE_DIR, "raw_store", "standards_portal")
LOCAL_SEARCH_DB = os.path.join(BASE_DIR, "local_search.db")


class LocalStandardsSearch:
    """
    Indexes all locally stored standard detail JSONs into an FTS5 
    (Full-Text Search) SQLite table for fast, accurate keyword search.
    """

    def __init__(self, db_path: str = LOCAL_SEARCH_DB, raw_store_dir: str = RAW_STORE_DIR):
        self.db_path = db_path
        self.raw_store_dir = raw_store_dir
        self._conn = None

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def build_index(self) -> Dict[str, Any]:
        """
        Scan all standard_IS_*.json files in raw_store/standards_portal/,
        parse them, and insert into a local FTS5-enabled SQLite table.
        Returns stats about what was indexed.
        """
        conn = self._get_conn()

        # Drop and recreate for clean rebuild
        conn.execute("DROP TABLE IF EXISTS standards_fts")
        conn.execute("DROP TABLE IF EXISTS standards_data")

        # Main data table
        conn.execute("""
            CREATE TABLE standards_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                standard_number TEXT NOT NULL UNIQUE,
                standard_name TEXT,
                department_name TEXT,
                committee_name TEXT,
                group_name TEXT,
                sub_group_name TEXT,
                sub_sub_group_name TEXT,
                ministry_name TEXT,
                published_on TEXT,
                type_of_standard TEXT,
                language TEXT,
                pdf_path TEXT,
                source_file TEXT,
                raw_json TEXT
            )
        """)

        # FTS5 virtual table for full-text search
        conn.execute("""
            CREATE VIRTUAL TABLE standards_fts USING fts5(
                standard_number,
                standard_name,
                department_name,
                committee_name,
                group_name,
                sub_group_name,
                sub_sub_group_name,
                ministry_name,
                type_of_standard,
                content=standards_data,
                content_rowid=id,
                tokenize='porter unicode61'
            )
        """)

        indexed = 0
        errors = 0
        departments = set()

        # Scan all standard_IS_*.json files
        if not os.path.exists(self.raw_store_dir):
            return {"indexed": 0, "errors": 0, "error": f"Directory not found: {self.raw_store_dir}"}

        for fname in os.listdir(self.raw_store_dir):
            if not fname.endswith(".json"):
                continue
            if "standard_IS_" not in fname and "standard_is_" not in fname.lower():
                continue

            fpath = os.path.join(self.raw_store_dir, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                std_num = data.get("standardNumber", "")
                std_name = data.get("standardName", "")
                dept_name = data.get("departmentName", "")
                committee_name = data.get("committeeName", "")
                group_name = data.get("groupName", "")
                sub_group = data.get("subGroupName", "")
                sub_sub_group = data.get("subSubGroupName", "")
                ministry = data.get("ministryName", "")
                published = data.get("publishedOn", "")
                type_std = data.get("typeOfStandardId", "")
                language = data.get("languageId", "")
                pdf_path = data.get("is_documents", "")

                departments.add(dept_name)

                conn.execute("""
                    INSERT OR IGNORE INTO standards_data (
                        standard_number, standard_name, department_name, committee_name,
                        group_name, sub_group_name, sub_sub_group_name, ministry_name,
                        published_on, type_of_standard, language, pdf_path, source_file, raw_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    std_num, std_name, dept_name, committee_name,
                    group_name, sub_group, sub_sub_group, ministry,
                    published, type_std, language, pdf_path, fname,
                    json.dumps(data, ensure_ascii=False)
                ))
                indexed += 1

            except Exception as e:
                errors += 1

        # Populate FTS index
        conn.execute("""
            INSERT INTO standards_fts(rowid, standard_number, standard_name, department_name,
                committee_name, group_name, sub_group_name, sub_sub_group_name, ministry_name, type_of_standard)
            SELECT id, standard_number, standard_name, department_name,
                committee_name, group_name, sub_group_name, sub_sub_group_name, ministry_name, type_of_standard
            FROM standards_data
        """)

        conn.commit()

        return {
            "indexed": indexed,
            "errors": errors,
            "departments": sorted(list(departments)),
            "db_path": self.db_path
        }

    def search(
        self,
        query: str,
        department: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Full-text search over indexed standards.
        Returns matched standards with relevance ranking.
        """
        conn = self._get_conn()

        # Check if index exists
        try:
            conn.execute("SELECT COUNT(*) FROM standards_data").fetchone()
        except sqlite3.OperationalError:
            # Index doesn't exist, build it
            self.build_index()

        # Tokenize query for FTS5
        # Clean the query: remove special characters, keep alphanumeric and spaces
        clean_q = re.sub(r'[^\w\s]', ' ', query)
        tokens = clean_q.split()

        if not tokens:
            return []

        # Build FTS5 match expression with OR for broader matching
        # Each token gets a wildcard suffix for partial matching
        fts_terms = " OR ".join(f'"{t}"*' for t in tokens if len(t) > 1)

        if not fts_terms:
            return []

        try:
            if department:
                rows = conn.execute("""
                    SELECT sd.*, rank
                    FROM standards_fts
                    JOIN standards_data sd ON standards_fts.rowid = sd.id
                    WHERE standards_fts MATCH ?
                    AND sd.department_name LIKE ?
                    ORDER BY rank
                    LIMIT ?
                """, (fts_terms, f"%{department}%", limit)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT sd.*, rank
                    FROM standards_fts
                    JOIN standards_data sd ON standards_fts.rowid = sd.id
                    WHERE standards_fts MATCH ?
                    ORDER BY rank
                    LIMIT ?
                """, (fts_terms, limit)).fetchall()
        except Exception:
            # Fallback to LIKE-based search if FTS fails
            like_clauses = " OR ".join(
                f"(sd.standard_name LIKE ? OR sd.standard_number LIKE ? OR sd.group_name LIKE ? OR sd.sub_sub_group_name LIKE ?)"
                for _ in tokens
            )
            params = []
            for t in tokens:
                pat = f"%{t}%"
                params.extend([pat, pat, pat, pat])

            if department:
                like_clauses = f"({like_clauses}) AND sd.department_name LIKE ?"
                params.append(f"%{department}%")

            params.append(limit)
            rows = conn.execute(f"""
                SELECT sd.*, 0 as rank
                FROM standards_data sd
                WHERE {like_clauses}
                LIMIT ?
            """, params).fetchall()

        results = []
        for row in rows:
            raw = json.loads(row["raw_json"]) if row["raw_json"] else {}
            results.append({
                "standard_number": row["standard_number"],
                "standard_name": row["standard_name"],
                "department_name": row["department_name"],
                "committee_name": row["committee_name"],
                "group_name": row["group_name"],
                "sub_group_name": row["sub_group_name"],
                "sub_sub_group_name": row["sub_sub_group_name"],
                "ministry_name": row["ministry_name"],
                "published_on": row["published_on"],
                "type_of_standard": row["type_of_standard"],
                "pdf_path": row["pdf_path"],
                "relevance_rank": float(row["rank"]) if row["rank"] else 0.0,
                "raw_data": raw
            })

        return results

    def get_all_by_department(self, department: str, limit: int = 500) -> List[Dict[str, Any]]:
        """Get all standards for a specific department."""
        conn = self._get_conn()
        try:
            rows = conn.execute("""
                SELECT * FROM standards_data
                WHERE department_name LIKE ?
                ORDER BY published_on DESC
                LIMIT ?
            """, (f"%{department}%", limit)).fetchall()
        except sqlite3.OperationalError:
            self.build_index()
            rows = conn.execute("""
                SELECT * FROM standards_data
                WHERE department_name LIKE ?
                ORDER BY published_on DESC
                LIMIT ?
            """, (f"%{department}%", limit)).fetchall()

        results = []
        for row in rows:
            raw = json.loads(row["raw_json"]) if row["raw_json"] else {}
            results.append({
                "standard_number": row["standard_number"],
                "standard_name": row["standard_name"],
                "department_name": row["department_name"],
                "committee_name": row["committee_name"],
                "group_name": row["group_name"],
                "sub_group_name": row["sub_group_name"],
                "sub_sub_group_name": row["sub_sub_group_name"],
                "ministry_name": row["ministry_name"],
                "published_on": row["published_on"],
                "type_of_standard": row["type_of_standard"],
                "pdf_path": row["pdf_path"],
                "raw_data": raw
            })
        return results

    def get_stats(self) -> Dict[str, Any]:
        """Return index statistics."""
        conn = self._get_conn()
        try:
            total = conn.execute("SELECT COUNT(*) FROM standards_data").fetchone()[0]
            depts = conn.execute("""
                SELECT department_name, COUNT(*) as cnt
                FROM standards_data
                GROUP BY department_name
                ORDER BY cnt DESC
            """).fetchall()
            return {
                "total_indexed": total,
                "departments": {r["department_name"]: r["cnt"] for r in depts}
            }
        except sqlite3.OperationalError:
            return {"total_indexed": 0, "departments": {}, "note": "Index not built yet"}

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None


if __name__ == "__main__":
    import sys

    engine = LocalStandardsSearch()

    if len(sys.argv) > 1 and sys.argv[1] == "build":
        print("Building local search index...")
        result = engine.build_index()
        print(json.dumps(result, indent=2))
    elif len(sys.argv) > 1 and sys.argv[1] == "stats":
        stats = engine.get_stats()
        print(json.dumps(stats, indent=2))
    elif len(sys.argv) > 1 and sys.argv[1] == "search":
        query = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "ayurveda"
        print(f"Searching for: '{query}'")
        results = engine.search(query, limit=5)
        for r in results:
            print(f"  [{r['standard_number']}] {r['standard_name'][:80]}")
            print(f"    Dept: {r['department_name']} | Committee: {r['committee_name']}")
            print(f"    Group: {r['group_name']} > {r['sub_sub_group_name']}")
            print()
    elif len(sys.argv) > 1 and sys.argv[1] == "dept":
        dept = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "AYUSH"
        results = engine.get_all_by_department(dept, limit=10)
        print(f"Standards for department '{dept}': {len(results)} results")
        for r in results:
            print(f"  [{r['standard_number']}] {r['standard_name'][:80]}")
    else:
        print("Usage: python local_search.py [build|stats|search <query>|dept <name>]")

    engine.close()
