"""
BIS Main Website Connector (bis.gov.in)
Fetches regulatory artifacts from the official BIS main site:
- QCOs (Quality Control Orders - Compulsory Certification)
- Product Manuals (Testing & Inspection Guidelines)
- Hallmarking (Assaying guidelines, HUID rules)
"""

import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import Dict, Any, Optional, List
from .base import BaseConnector


class BisMainConnector(BaseConnector):
    SOURCE_DOMAIN = "bis.gov.in"
    BASE_URL = "https://www.bis.gov.in"

    QCO_URL = f"{BASE_URL}/product-certification/products-under-compulsory-certification/"
    MANUALS_URL = f"{BASE_URL}/product-certification/product-specific-information-2/product-manuals/"
    HALLMARKING_URL = f"{BASE_URL}/hallmarking-overview/"

    def fetch_qcos(self, download_sample_pdfs: int = 5) -> Dict[str, Any]:
        """Fetch and store QCO compulsory certification orders."""
        self.logger.info("Fetching QCOs from BIS main website...")
        resp = self.request("GET", self.QCO_URL)
        raw_html = resp.content

        # 1. Store the master raw HTML document
        self.store.store_document(
            source_domain=self.SOURCE_DOMAIN,
            category="qco",
            source_url=self.QCO_URL,
            doc_name="qco_master_index.html",
            content=raw_html,
            doc_type="html",
            metadata={"title": "Products Under Compulsory Certification (QCOs)"}
        )

        # 2. Extract structured list of orders and PDF links
        soup = BeautifulSoup(raw_html, "html.parser")
        orders = []
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            text = a.get_text(strip=True)
            if href.lower().endswith(".pdf") or "qco" in href.lower() or "order" in text.lower():
                full_url = urljoin(self.BASE_URL, href)
                orders.append({
                    "title": text or "QCO Notification",
                    "url": full_url
                })

        # Store metadata catalog
        catalog_bytes = json.dumps(orders, indent=2).encode("utf-8")
        self.store.store_document(
            source_domain=self.SOURCE_DOMAIN,
            category="qco",
            source_url=f"{self.QCO_URL}#catalog",
            doc_name="qco_extracted_catalog.json",
            content=catalog_bytes,
            doc_type="json",
            metadata={"total_orders_identified": len(orders)}
        )

        # Download sample QCO PDFs if requested
        downloaded = 0
        for item in orders[:download_sample_pdfs]:
            try:
                pdf_resp = self.request("GET", item["url"], timeout=20)
                safe_name = "".join(c if c.isalnum() else "_" for c in item["title"][:40]) + ".pdf"
                self.store.store_document(
                    source_domain=self.SOURCE_DOMAIN,
                    category="qco",
                    source_url=item["url"],
                    doc_name=safe_name,
                    content=pdf_resp.content,
                    doc_type="pdf",
                    metadata={"title": item["title"]}
                )
                downloaded += 1
            except Exception as e:
                self.logger.warning(f"Failed to download QCO PDF {item['url']}: {e}")

        return {
            "category": "qco",
            "master_html_stored": True,
            "orders_catalogued": len(orders),
            "sample_pdfs_stored": downloaded
        }

    def fetch_product_manuals(self, download_sample_pdfs: int = 5) -> Dict[str, Any]:
        """Fetch and store Product Manuals / SIT information."""
        self.logger.info("Fetching Product Manuals from BIS main website...")
        resp = self.request("GET", self.MANUALS_URL)
        raw_html = resp.content

        # 1. Store master raw HTML
        self.store.store_document(
            source_domain=self.SOURCE_DOMAIN,
            category="manuals",
            source_url=self.MANUALS_URL,
            doc_name="product_manuals_index.html",
            content=raw_html,
            doc_type="html",
            metadata={"title": "Product Manuals & SIT"}
        )

        # 2. Extract manual links
        soup = BeautifulSoup(raw_html, "html.parser")
        manuals = []
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            text = a.get_text(strip=True)
            if href.lower().endswith(".pdf") and len(text) > 2:
                full_url = urljoin(self.BASE_URL, href)
                manuals.append({
                    "title": text,
                    "url": full_url
                })

        catalog_bytes = json.dumps(manuals, indent=2).encode("utf-8")
        self.store.store_document(
            source_domain=self.SOURCE_DOMAIN,
            category="manuals",
            source_url=f"{self.MANUALS_URL}#catalog",
            doc_name="product_manuals_catalog.json",
            content=catalog_bytes,
            doc_type="json",
            metadata={"total_manuals_identified": len(manuals)}
        )

        downloaded = 0
        for item in manuals[:download_sample_pdfs]:
            try:
                pdf_resp = self.request("GET", item["url"], timeout=20)
                safe_name = "".join(c if c.isalnum() else "_" for c in item["title"][:40]) + ".pdf"
                self.store.store_document(
                    source_domain=self.SOURCE_DOMAIN,
                    category="manuals",
                    source_url=item["url"],
                    doc_name=safe_name,
                    content=pdf_resp.content,
                    doc_type="pdf",
                    metadata={"title": item["title"]}
                )
                downloaded += 1
            except Exception as e:
                self.logger.warning(f"Failed to download Manual PDF {item['url']}: {e}")

        return {
            "category": "manuals",
            "master_html_stored": True,
            "manuals_catalogued": len(manuals),
            "sample_pdfs_stored": downloaded
        }

    def fetch_hallmarking(self) -> Dict[str, Any]:
        """Fetch and store Hallmarking guidelines and regulations."""
        self.logger.info("Fetching Hallmarking guidelines from BIS main website...")
        resp = self.request("GET", self.HALLMARKING_URL)
        raw_html = resp.content

        self.store.store_document(
            source_domain=self.SOURCE_DOMAIN,
            category="hallmarking",
            source_url=self.HALLMARKING_URL,
            doc_name="hallmarking_overview.html",
            content=raw_html,
            doc_type="html",
            metadata={"title": "Hallmarking Overview & Guidelines"}
        )

        soup = BeautifulSoup(raw_html, "html.parser")
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            text = a.get_text(strip=True)
            if any(k in text.lower() for k in ["huid", "jeweller", "assaying", "gold", "silver"]):
                links.append({"title": text, "url": urljoin(self.BASE_URL, href)})

        self.store.store_document(
            source_domain=self.SOURCE_DOMAIN,
            category="hallmarking",
            source_url=f"{self.HALLMARKING_URL}#links",
            doc_name="hallmarking_links.json",
            content=json.dumps(links, indent=2).encode("utf-8"),
            doc_type="json",
            metadata={"links_count": len(links)}
        )

        return {
            "category": "hallmarking",
            "master_html_stored": True,
            "relevant_links_catalogued": len(links)
        }

    def fetch_and_store(self, limit: Optional[int] = 5) -> Dict[str, Any]:
        """Run all BIS main site ingestion pipelines."""
        qco_res = self.fetch_qcos(download_sample_pdfs=limit or 5)
        manuals_res = self.fetch_product_manuals(download_sample_pdfs=limit or 5)
        hallmarking_res = self.fetch_hallmarking()
        return {
            "qco": qco_res,
            "manuals": manuals_res,
            "hallmarking": hallmarking_res
        }
