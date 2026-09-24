"""
BIS Standards Scraper — API wrapper functions.

Each function calls a specific BIS backend endpoint and returns parsed JSON.
All endpoints are POST with JSON payloads.
"""

import requests
import time
from config import (
    REVIEW_SERVICE,
    PROJECT_SERVICE,
    PROPOSAL_SERVICE,
    MASTER_SERVICE,
    COMMON_PAYLOAD,
    HEADERS,
    REQUEST_DELAY_SECONDS,
)


def _post(url: str, payload: dict) -> dict:
    """Make a POST request to a BIS API endpoint and return parsed JSON."""
    resp = requests.post(url, json=payload, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    time.sleep(REQUEST_DELAY_SECONDS)
    return resp.json()


# ── Standard Detail APIs ─────────────────────────────────────

def get_standard_details(encrypted_id: str) -> dict:
    """
    Fetch Basic + Classification details for a single standard.
    Returns the full 'data' object from getWebsiteStandardDetails.
    """
    payload = {
        "encId": encrypted_id,
        "fromPage": "guestUserPage",
        **COMMON_PAYLOAD,
    }
    result = _post(f"{REVIEW_SERVICE}/getWebsiteStandardDetails", payload)
    return result.get("data", {})


def get_cross_ref_details(encrypted_id: str) -> dict:
    """
    Fetch Standards Referred (cross-references) for a standard.
    Returns { crossRefData: [...], crossFollowRefData: [...] }
    """
    payload = {
        "encId": encrypted_id,
        "fromPage": "guestUserPage",
        **COMMON_PAYLOAD,
    }
    result = _post(f"{REVIEW_SERVICE}/getCrossRefDetails", payload)
    return result.get("data", {})


def get_amendment_details(encrypted_id: str) -> dict:
    """Fetch amendment list for a standard."""
    payload = {
        "standardId": encrypted_id,
        **COMMON_PAYLOAD,
    }
    result = _post(f"{REVIEW_SERVICE}/getAmendmentDetails", payload)
    return {
        "totalAmendments": result.get("totalAmendments", 0),
        "amendments": result.get("data", []),
    }


def get_gazette_details(encrypted_id: str) -> list:
    """Fetch gazette documents for a standard."""
    payload = {
        "standardId": {"standardId": encrypted_id},
        "fromPage": "guestUserPage",
        **COMMON_PAYLOAD,
    }
    result = _post(f"{REVIEW_SERVICE}/getGazettedetails", payload)
    return result.get("data", [])


def get_licence_details(encrypted_id: str, page: int = 1, limit: int = 100) -> dict:
    """Fetch licence details for a standard."""
    payload = {
        "standardId": encrypted_id,
        "status": "Operative",
        "page": page,
        "limit": limit,
        "searchText": "",
        **COMMON_PAYLOAD,
    }
    result = _post(f"{REVIEW_SERVICE}/getStandardLicenseDetails", payload)
    return {
        "licences": result.get("data", []),
        "pagination": result.get("pagination", {}),
    }


def get_product_manual_details(encrypted_id: str) -> list:
    """Fetch product manual & SIT details."""
    payload = {
        "standardId": encrypted_id,
        **COMMON_PAYLOAD,
    }
    result = _post(f"{REVIEW_SERVICE}/getProductManualDetails", payload)
    inner = result.get("data", {})
    if isinstance(inner, dict):
        return inner.get("product_manuals_details", [])
    return []


def get_laboratory_details(encrypted_id: str, page: int = 1, limit: int = 100) -> dict:
    """Fetch laboratory details for a standard."""
    payload = {
        "standardId": encrypted_id,
        "page": page,
        "limit": limit,
        "searchText": "",
        **COMMON_PAYLOAD,
    }
    result = _post(f"{REVIEW_SERVICE}/getStandardLaboratoryDetails", payload)
    return {
        "laboratories": result.get("data", []),
        "pagination": result.get("pagination", {}),
    }


def get_corrigendum_details(encrypted_id: str) -> list:
    """Fetch corrigendum details."""
    payload = {
        "standardId": encrypted_id,
        **COMMON_PAYLOAD,
    }
    result = _post(f"{REVIEW_SERVICE}/getCorrigendumDetails", payload)
    return result.get("data", [])


# ── Listing / Department APIs ────────────────────────────────

def get_departments() -> list:
    """Fetch the list of technical departments."""
    result = _post(f"{PROJECT_SERVICE}/getWebsiteTechnicalDepartments", {})
    return result.get("data", [])


def get_department_standards_count() -> list:
    """Fetch standards count per department."""
    result = _post(f"{REVIEW_SERVICE}/getWebitePSCountDepartmentwise", {})
    return result.get("data", [])


def get_standards_list(encrypted_dept_id: str, page: int = 1, limit: int = 10, selected_type: int = 7) -> dict:
    """
    Fetch the list of standards for a given department.
    selectedType=7 means 'Total' (both new + revised).
    """
    payload = {
        "encDepartmentId": encrypted_dept_id,
        "typeSelected": selected_type,
        "offset": (page - 1) * limit,
        "limit": limit,
        "ministryIds": [],
        "sdgIds": [],
        "techCommitteeId": 0,
        **COMMON_PAYLOAD,
    }
    result = _post(f"{REVIEW_SERVICE}/getWebsitePSTechDepartmentWise", payload)
    import math
    total_record = result.get("totalRecord", 0)
    return {
        "standards": result.get("data", []),
        "pagination": {
            "totalRecord": total_record,
            "totalPages": math.ceil(total_record / limit) if total_record else 1
        },
    }


def get_standard_with_dept_committee(encrypted_id: str) -> dict:
    """
    Fetch department + committee info for a standard.
    """
    payload = {
        "StandardId": encrypted_id,
        **COMMON_PAYLOAD,
    }
    result = _post(f"{PROPOSAL_SERVICE}/getStandardsWithDeptAndCommittee", payload)
    data_list = result.get("data", [])
    return data_list[0] if data_list else {}
