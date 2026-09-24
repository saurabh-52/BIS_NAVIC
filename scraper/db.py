"""
BIS Standards Scraper — Database helper functions.
Handles connecting to SQLite, applying schema, and inserting parsed JSON.
"""

import sqlite3
from typing import Dict, Any
from config import DB_PATH
import os


def get_db_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database with the schema."""
    schema_path = os.path.join(os.path.dirname(__file__), "db_schema.sql")
    with open(schema_path, "r") as f:
        schema = f.read()

    conn = get_db_connection()
    conn.executescript(schema)
    conn.commit()
    conn.close()


def insert_standard(data: Dict[str, Any]) -> int:
    """
    Insert a fully parsed standard dictionary into the database.
    Updates existing records based on raw_standard_id/encrypted_id.
    Returns the internal primary key (id) of the inserted/updated standard.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # ── 1. UPSERT into main `standards` table ──
        b = data["basic_details"]
        c = data["classification_details"]
        m = data["_meta"]

        cursor.execute("""
            INSERT INTO standards (
                raw_standard_id, encrypted_id, is_number, title, published_on,
                type_of_standard, no_of_revisions, no_of_amendments, language,
                pdf_document, hindi_document, life_cycle_status,
                department_name, department_id, technical_committee_name, technical_committee_id,
                group_name, sub_group_name, sub_sub_group_name, sector_name, sub_sector_name, sub_sub_sector_name,
                certification, relevant_ministry, sustainable_development_goals, short_title, ics_code,
                degree_of_equivalence, equivalent_international_standard, risk_level, reaffirmation_year,
                source_url
            ) VALUES (
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?
            )
            ON CONFLICT(raw_standard_id) DO UPDATE SET
                encrypted_id=excluded.encrypted_id, is_number=excluded.is_number, title=excluded.title, published_on=excluded.published_on,
                type_of_standard=excluded.type_of_standard, no_of_revisions=excluded.no_of_revisions, no_of_amendments=excluded.no_of_amendments, language=excluded.language,
                pdf_document=excluded.pdf_document, hindi_document=excluded.hindi_document, life_cycle_status=excluded.life_cycle_status,
                department_name=excluded.department_name, department_id=excluded.department_id, technical_committee_name=excluded.technical_committee_name, technical_committee_id=excluded.technical_committee_id,
                group_name=excluded.group_name, sub_group_name=excluded.sub_group_name, sub_sub_group_name=excluded.sub_sub_group_name, sector_name=excluded.sector_name, sub_sector_name=excluded.sub_sector_name, sub_sub_sector_name=excluded.sub_sub_sector_name,
                certification=excluded.certification, relevant_ministry=excluded.relevant_ministry, sustainable_development_goals=excluded.sustainable_development_goals, short_title=excluded.short_title, ics_code=excluded.ics_code,
                degree_of_equivalence=excluded.degree_of_equivalence, equivalent_international_standard=excluded.equivalent_international_standard, risk_level=excluded.risk_level, reaffirmation_year=excluded.reaffirmation_year,
                source_url=excluded.source_url, scraped_at=CURRENT_TIMESTAMP
        """, (
            m.get("raw_standard_id"), m.get("encrypted_id"), b.get("is_number"), b.get("title"), b.get("published_on"),
            b.get("type_of_standard"), b.get("no_of_revisions"), b.get("no_of_amendments"), b.get("language"),
            b.get("pdf_document"), b.get("hindi_document"), b.get("life_cycle_status"),
            b.get("department", {}).get("name"), b.get("department", {}).get("id"), b.get("technical_committee", {}).get("name"), b.get("technical_committee", {}).get("id"),
            c.get("group"), c.get("sub_group"), c.get("sub_sub_group"), c.get("sector"), c.get("sub_sector"), c.get("sub_sub_sector"),
            c.get("certification"), c.get("relevant_ministry"), c.get("sustainable_development_goals"), c.get("short_title"), c.get("ics_code"),
            c.get("degree_of_equivalence"), c.get("equivalent_international_standard"), c.get("risk_level"), c.get("reaffirmation_year"),
            m.get("source_url")
        ))
        
        # Get the internal ID (works for insert and update because of sqlite3 behavior)
        cursor.execute("SELECT id FROM standards WHERE raw_standard_id = ?", (m.get("raw_standard_id"),))
        standard_id = cursor.fetchone()[0]

        # ── Clear existing related records for this standard (clean wipe for updates) ──
        cursor.execute("DELETE FROM standards_referred WHERE standard_id = ?", (standard_id,))
        cursor.execute("DELETE FROM amendments WHERE standard_id = ?", (standard_id,))
        cursor.execute("DELETE FROM gazette_documents WHERE standard_id = ?", (standard_id,))
        cursor.execute("DELETE FROM licences WHERE standard_id = ?", (standard_id,))
        cursor.execute("DELETE FROM product_manuals WHERE standard_id = ?", (standard_id,))
        cursor.execute("DELETE FROM laboratories WHERE standard_id = ?", (standard_id,))
        cursor.execute("DELETE FROM corrigendums WHERE standard_id = ?", (standard_id,))

        # ── 2. Insert related records ──
        
        # Standards Referred
        for ref in data.get("standards_referred", {}).get("indian_standards", []):
            cursor.execute("""
                INSERT INTO standards_referred (standard_id, is_type, referred_standard_number, referred_standard_name, referred_encrypted_id)
                VALUES (?, 1, ?, ?, ?)
            """, (standard_id, ref.get("standard_number"), ref.get("standard_name"), ref.get("encrypted_id")))
        
        for ref in data.get("standards_referred", {}).get("international_standards", []):
            cursor.execute("""
                INSERT INTO standards_referred (standard_id, is_type, referred_standard_number, referred_standard_name, referred_encrypted_id)
                VALUES (?, 2, ?, ?, ?)
            """, (standard_id, ref.get("standard_number"), ref.get("standard_name"), ref.get("encrypted_id")))

        # Amendments
        for amd in data.get("amendments", {}).get("items", []):
            cursor.execute("""
                INSERT INTO amendments (standard_id, amendment_number, document, published_on)
                VALUES (?, ?, ?, ?)
            """, (standard_id, amd.get("amendment_number"), amd.get("document"), amd.get("published_on")))

        # Gazette Documents
        for gaz in data.get("gazette_documents", []):
            cursor.execute("""
                INSERT INTO gazette_documents (standard_id, so_number, amendment_number, document)
                VALUES (?, ?, ?, ?)
            """, (standard_id, gaz.get("so_number"), gaz.get("amendment_number"), gaz.get("document")))

        # Licences
        for lic in data.get("licences", {}).get("items", []):
            cursor.execute("""
                INSERT INTO licences (standard_id, licence_number, firm_name, address, status)
                VALUES (?, ?, ?, ?, ?)
            """, (standard_id, lic.get("licence_number"), lic.get("firm_name"), lic.get("address"), lic.get("status")))

        # Product Manuals
        for pm in data.get("product_manuals", []):
            cursor.execute("""
                INSERT INTO product_manuals (standard_id, title, document)
                VALUES (?, ?, ?)
            """, (standard_id, pm.get("title"), pm.get("document")))

        # Laboratories
        for lab in data.get("laboratories", {}).get("items", []):
            cursor.execute("""
                INSERT INTO laboratories (standard_id, lab_name, address, scope)
                VALUES (?, ?, ?, ?)
            """, (standard_id, lab.get("lab_name"), lab.get("address"), lab.get("scope")))

        # Corrigendums
        for cor in data.get("corrigendums", []):
            cursor.execute("""
                INSERT INTO corrigendums (standard_id, title, document)
                VALUES (?, ?, ?)
            """, (standard_id, cor.get("title"), cor.get("document")))

        conn.commit()
        return standard_id

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
