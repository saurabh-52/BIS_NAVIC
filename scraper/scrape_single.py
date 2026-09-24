"""
BIS Standards Scraper — Scrape a single standard (all tabs).

Fetches Basic Details, Classification Details, Standards Referred,
Amendments, Gazette Documents, Licences, Product Manuals & SIT,
Laboratories, and Corrigendum for one standard.
"""

import json
import sys
from bis_api import (
    get_standard_details,
    get_cross_ref_details,
    get_standard_with_dept_committee,
    get_amendment_details,
    get_gazette_details,
    get_licence_details,
    get_product_manual_details,
    get_laboratory_details,
    get_corrigendum_details,
)

# The encrypted ID for IS 19901:2026 (AYUSH Dept — Homoeopathy)
DEFAULT_ENCRYPTED_ID = (
    "eyJpdiI6IkhFNngxTWpENVE2dXlsSkJROFhXU2c9PSIsInZhbHVlIjoiM1B5aHgyREZ0"
    "enJvQUl4TGtFdEc4QT09IiwibWFjIjoiMzM5MGY4YTk1OTZmOWFhZTBmODQyM2ExODZm"
    "YWQwMWVhMDk5NGRiMWY2NWU3Y2JiMTU3MzhmYzBkOWMxYzEyNiIsInRhZyI6IiJ9"
)


def scrape_single_standard(encrypted_id: str) -> dict:
    """
    Scrape ALL tab data for one standard.
    Returns a structured dict with every section.
    """
    print(f"[1/8] Fetching standard details...", file=sys.stderr)
    details = get_standard_details(encrypted_id)

    print(f"[2/8] Fetching department & committee info...", file=sys.stderr)
    dept_info = get_standard_with_dept_committee(encrypted_id)

    print(f"[3/8] Fetching cross-references (standards referred)...", file=sys.stderr)
    cross_refs = get_cross_ref_details(encrypted_id)

    print(f"[4/8] Fetching amendments...", file=sys.stderr)
    amendments = get_amendment_details(encrypted_id)

    print(f"[5/8] Fetching gazette documents...", file=sys.stderr)
    gazettes = get_gazette_details(encrypted_id)

    print(f"[6/8] Fetching licences...", file=sys.stderr)
    licences = get_licence_details(encrypted_id)

    print(f"[7/8] Fetching product manuals, laboratories, corrigendum...", file=sys.stderr)
    product_manuals = get_product_manual_details(encrypted_id)
    labs = get_laboratory_details(encrypted_id)
    corrigendums = get_corrigendum_details(encrypted_id)

    print(f"[8/8] Building structured output...", file=sys.stderr)

    # ── Build structured output ──────────────────────────────
    result = {
        "basic_details": {
            "is_number": details.get("standardNumber"),
            "title": details.get("standardName"),
            "published_on": details.get("publishedOn"),
            "type_of_standard": details.get("typeOfStandardId"),
            "no_of_revisions": details.get("noOfRevision"),
            "no_of_amendments": details.get("noOfAmendment"),
            "language": details.get("languageId"),
            "pdf_document": details.get("is_documents"),
            "hindi_document": details.get("is_hindi_document"),
            "life_cycle_status": (
                "Published" if details.get("isStatus") == 1
                else "Withdrawn" if details.get("withdrawStatus") == 1
                else "Unknown"
            ),
            "department": {
                "name": dept_info.get("deptPreparedName") or details.get("departmentName"),
                "id": details.get("departmentId"),
            },
            "technical_committee": {
                "name": dept_info.get("secCommitteePreparedName") or details.get("committeeName"),
                "id": details.get("committeeId"),
            },
        },
        "classification_details": {
            "group": details.get("groupName"),
            "sub_group": details.get("subGroupName"),
            "sub_sub_group": details.get("subSubGroupName"),
            "sector": details.get("sectorName"),
            "sub_sector": details.get("subSectorName"),
            "sub_sub_sector": details.get("subSubSectorName"),
            "certification": details.get("certificationName"),
            "relevant_ministry": details.get("ministryName"),
            "sustainable_development_goals": details.get("goalNames"),
            "short_title": details.get("shortTitle"),
            "ics_code": details.get("icsCode"),
            "degree_of_equivalence": details.get("equivalenceTypeName"),
            "equivalent_international_standard": details.get("equivalentIs") or details.get("identical_is"),
            "risk_level": details.get("riskNameName"),
            "reaffirmation_year": details.get("reAffirmationYear"),
        },
        "standards_referred": {
            "indian_standards": [
                {
                    "standard_number": ref.get("standardNumber"),
                    "standard_name": ref.get("standardName"),
                    "encrypted_id": ref.get("standardEncId"),
                }
                for ref in cross_refs.get("crossRefData", [])
                if ref.get("isType") == 1
            ],
            "international_standards": [
                {
                    "standard_number": ref.get("standardNumber"),
                    "standard_name": ref.get("standardName"),
                    "encrypted_id": ref.get("standardEncId"),
                }
                for ref in cross_refs.get("crossRefData", [])
                if ref.get("isType") == 2
            ],
        },
        "amendments": {
            "total": amendments.get("totalAmendments", 0),
            "items": [
                {
                    "amendment_number": a.get("amendmentNumber") or a.get("amdNo"),
                    "standard_number": a.get("standardNumber"),
                    "document": a.get("migratedFiles") or a.get("is_documents"),
                    "published_on": a.get("publishedOn"),
                }
                for a in amendments.get("amendments", [])
            ],
        },
        "gazette_documents": [
            {
                "so_number": g.get("So_No"),
                "standard_number": g.get("standardNumber"),
                "amendment_number": g.get("Amd_No"),
                "document": g.get("migratedFiles"),
            }
            for g in gazettes
        ],
        "licences": {
            "total": licences.get("pagination", {}).get("totalRecord", 0),
            "items": [
                {
                    "licence_number": lic.get("licenceNumber") or lic.get("licence_no"),
                    "firm_name": lic.get("firmName") or lic.get("firm_name"),
                    "address": lic.get("address"),
                    "status": lic.get("status"),
                }
                for lic in licences.get("licences", [])
            ],
        },
        "product_manuals": [
            {
                "document": pm.get("migratedFiles") or pm.get("document"),
                "title": pm.get("title") or pm.get("standardNumber"),
            }
            for pm in product_manuals
        ],
        "laboratories": {
            "total": labs.get("pagination", {}).get("totalRecord", 0),
            "items": [
                {
                    "lab_name": lab.get("labName") or lab.get("lab_name"),
                    "address": lab.get("address"),
                    "scope": lab.get("scope"),
                }
                for lab in labs.get("laboratories", [])
            ],
        },
        "corrigendums": [
            {
                "document": c.get("migratedFiles") or c.get("document"),
                "title": c.get("title") or c.get("standardNumber"),
            }
            for c in corrigendums
        ],
        "_meta": {
            "encrypted_id": encrypted_id,
            "raw_standard_id": details.get("rowStandardId") or details.get("pk_is_id"),
            "source_url": f"https://standards.bis.gov.in/website/standard-details?encryptedId={encrypted_id}",
        },
    }

    return result


def main():
    import db
    
    # Initialize DB (creates tables if they don't exist)
    db.init_db()
    
    enc_id = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ENCRYPTED_ID
    print(f"Scraping standard with encrypted ID: {enc_id[:40]}...", file=sys.stderr)

    data = scrape_single_standard(enc_id)

    # Insert into database
    print(f"\n[9/9] Saving to database...", file=sys.stderr)
    internal_id = db.insert_standard(data)
    print(f"      -> Inserted/Updated as standard internal ID: {internal_id}", file=sys.stderr)

    # Summary
    is_num = data['basic_details']['is_number']
    title = data['basic_details']['title']
    n_refs = len(data['standards_referred']['indian_standards']) + len(data['standards_referred']['international_standards'])
    n_amd = data['amendments']['total']
    n_gaz = len(data['gazette_documents'])
    n_lic = data['licences']['total']
    n_pm = len(data['product_manuals'])
    n_lab = data['laboratories']['total']
    n_cor = len(data['corrigendums'])
    print(f"\n✅ Done! {is_num}: {title}", file=sys.stderr)
    print(f"   Refs={n_refs} Amendments={n_amd} Gazettes={n_gaz} Licences={n_lic} Manuals={n_pm} Labs={n_lab} Corrigendums={n_cor}", file=sys.stderr)


if __name__ == "__main__":
    main()

