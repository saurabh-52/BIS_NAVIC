"""
BIS LIMS Connector (lims.bis.gov.in)
Fetches laboratory network information, recognition details, and testing scopes
from the BIS Laboratory Information Management System.
"""

import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import Dict, Any, Optional
from .base import BaseConnector


class LimsConnector(BaseConnector):
    SOURCE_DOMAIN = "lims.bis.gov.in"
    BASE_URL = "https://lims.bis.gov.in"

    def fetch_and_store(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """Fetch and store LIMS portal data and lab network references."""
        self.logger.info("Fetching LIMS portal from lims.bis.gov.in...")
        resp = self.request("GET", self.BASE_URL)
        raw_html = resp.content

        # 1. Store the master raw LIMS landing page
        self.store.store_document(
            source_domain=self.SOURCE_DOMAIN,
            category="lims",
            source_url=self.BASE_URL,
            doc_name="lims_home.html",
            content=raw_html,
            doc_type="html",
            metadata={"title": "BIS Laboratory Information Management System (LIMS)"}
        )

        # 2. Extract links related to recognized labs, testing scopes, and guidelines
        soup = BeautifulSoup(raw_html, "html.parser")
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            text = a.get_text(strip=True)
            if href and not href.startswith("javascript") and not href.startswith("#"):
                links.append({
                    "title": text or "LIMS Resource",
                    "url": urljoin(self.BASE_URL, href)
                })

        self.store.store_document(
            source_domain=self.SOURCE_DOMAIN,
            category="lims",
            source_url=f"{self.BASE_URL}#navigation",
            doc_name="lims_portal_links.json",
            content=json.dumps(links, indent=2).encode("utf-8"),
            doc_type="json",
            metadata={"total_links": len(links)}
        )

        return {
            "source": self.SOURCE_DOMAIN,
            "category": "lims",
            "portal_html_stored": True,
            "links_catalogued": len(links)
        }
