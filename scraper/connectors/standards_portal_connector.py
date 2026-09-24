"""
Standards Portal Connector
Fetches Indian Standards catalog, specifications, classifications, and gazette
references from the official BIS Standards Portal (standards.bis.gov.in / standardsadmin.bis.gov.in).
"""

import json
from typing import Dict, Any, Optional, List
from .base import BaseConnector

BASE_ADMIN = "https://standardsadmin.bis.gov.in"
PROJECT_SERVICE = f"{BASE_ADMIN}/project-service"
REVIEW_SERVICE = f"{BASE_ADMIN}/review-service"
COMMON_PAYLOAD = {
    "token": None,
    "refreshToken": None,
    "clientId": None,
    "clientSecret": None,
    "sub": None,
}


class StandardsPortalConnector(BaseConnector):
    SOURCE_DOMAIN = "standards.bis.gov.in"
    CATEGORY = "standards_portal"

    def get_departments(self) -> List[Dict[str, Any]]:
        """Fetch list of all technical departments."""
        url = f"{PROJECT_SERVICE}/getWebsiteTechnicalDepartments"
        resp = self.request("POST", url, json={})
        return resp.json().get("data", [])

    def get_standards_list(
        self,
        enc_dept_id: str,
        page: int = 1,
        limit: int = 12,
        offset: Optional[int] = None
    ) -> Dict[str, Any]:
        """Fetch standards catalog page for a given department."""
        url = f"{REVIEW_SERVICE}/getWebsitePSTechDepartmentWise"
        actual_offset = offset if offset is not None else (page - 1) * limit
        payload = {
            "encDepartmentId": enc_dept_id,
            "typeSelected": 7,
            "offset": actual_offset,
            "limit": limit,
            "ministryIds": [],
            "sdgIds": [],
            "techCommitteeId": 0,
            **COMMON_PAYLOAD,
        }
        resp = self.request("POST", url, json=payload)
        return resp.json()

    def get_standard_details(self, enc_standard_id: str) -> Dict[str, Any]:
        """Fetch basic and classification details for a standard."""
        url = f"{REVIEW_SERVICE}/getWebsiteStandardDetails"
        payload = {
            "encId": enc_standard_id,
            "fromPage": "guestUserPage",
            **COMMON_PAYLOAD,
        }
        resp = self.request("POST", url, json=payload)
        return resp.json().get("data", {})

    def fetch_and_store(
        self,
        department_filter: Optional[str] = None,
        limit_per_dept: Optional[int] = 10,
        max_depts: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Fetch departments and standards, persisting each raw payload to RawDocumentStore.
        """
        self.logger.info("Fetching technical departments from Standards Portal...")
        depts = self.get_departments()
        
        # Store departments catalog raw JSON
        self.store.store_document(
            source_domain=self.SOURCE_DOMAIN,
            category=self.CATEGORY,
            source_url=f"{PROJECT_SERVICE}/getWebsiteTechnicalDepartments",
            doc_name="technical_departments_catalog.json",
            content=json.dumps(depts, indent=2).encode("utf-8"),
            doc_type="json",
            metadata={"count": len(depts)}
        )

        if department_filter:
            depts = [d for d in depts if department_filter.upper() in d.get("deptName", "").upper()]

        if max_depts:
            depts = depts[:max_depts]

        total_standards_stored = 0
        details_stored = 0

        for dept in depts:
            dept_name = dept.get("deptName", "Unknown")
            enc_id = dept.get("encryptedDepartmentId")
            if not enc_id:
                continue

            self.logger.info(f"Ingesting department catalog: {dept_name}")
            page_size = 100
            target_limit = limit_per_dept or 12
            standards = []
            page_num = 1

            while len(standards) < target_limit:
                current_fetch_limit = min(page_size, target_limit - len(standards))
                page_data = self.get_standards_list(
                    enc_id,
                    page=page_num,
                    limit=current_fetch_limit,
                    offset=len(standards)
                )
                page_standards = page_data.get("data", [])
                if not page_standards:
                    break
                standards.extend(page_standards)
                total_records = page_data.get("totalRecord", 0)
                if len(standards) >= total_records or len(page_standards) < current_fetch_limit:
                    break
                page_num += 1

            # Store department list raw
            safe_dept = "".join(c if c.isalnum() else "_" for c in dept_name)[:30]
            self.store.store_document(
                source_domain=self.SOURCE_DOMAIN,
                category=self.CATEGORY,
                source_url=f"{REVIEW_SERVICE}/getWebsitePSTechDepartmentWise?dept={safe_dept}",
                doc_name=f"dept_list_{safe_dept}.json",
                content=json.dumps({"data": standards, "totalRecord": len(standards)}, indent=2).encode("utf-8"),
                doc_type="json",
                metadata={"department": dept_name, "count": len(standards)}
            )
            total_standards_stored += len(standards)

            # Ingest individual standard details
            for std in standards[: (limit_per_dept or len(standards))]:
                std_enc_id = std.get("standardId")
                std_num = std.get("standardNumber", "IS_UNKNOWN")
                if not std_enc_id:
                    continue
                safe_std = "".join(c if c.isalnum() else "_" for c in std_num)
                std_url = f"{REVIEW_SERVICE}/getWebsiteStandardDetails?stdId={safe_std}"
                if self.store.has_document(std_url):
                    continue
                try:
                    std_details = self.get_standard_details(std_enc_id)
                    self.store.store_document(
                        source_domain=self.SOURCE_DOMAIN,
                        category=self.CATEGORY,
                        source_url=std_url,
                        doc_name=f"standard_{safe_std}.json",
                        content=json.dumps(std_details, indent=2).encode("utf-8"),
                        doc_type="json",
                        metadata={
                            "is_number": std_num,
                            "department": dept_name,
                            "title": std.get("standardTitle"),
                            "encrypted_id": std_enc_id
                        }
                    )
                    details_stored += 1
                except Exception as e:
                    self.logger.warning(f"Failed to fetch details for {std_num}: {e}")

        return {
            "departments_processed": len(depts),
            "department_lists_stored": total_standards_stored,
            "standard_details_stored": details_stored
        }
