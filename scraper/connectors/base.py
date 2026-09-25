"""
Base Connector for BIS Source Connectors
Provides shared HTTP networking, rate-limiting, retries, and persistence
to the Raw Document Store.
"""

import time
import logging
import requests
import urllib3
from typing import Optional, Dict, Any
from storage.raw_document_store import RawDocumentStore

# Suppress government self-signed/chain certificate warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


class BaseConnector:
    def __init__(self, store: Optional[RawDocumentStore] = None, request_delay: float = 0.5):
        self.store = store or RawDocumentStore()
        self.delay = request_delay
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/json,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        })
        self.logger = logging.getLogger(self.__class__.__name__)

    def request(
        self,
        method: str,
        url: str,
        max_retries: int = 3,
        timeout: int = 30,
        **kwargs
    ) -> requests.Response:
        """Execute HTTP request with retries and delay."""
        kwargs.setdefault("verify", False)
        for attempt in range(1, max_retries + 1):
            try:
                time.sleep(self.delay)
                resp = self.session.request(method, url, timeout=timeout, **kwargs)
                resp.raise_for_status()
                return resp
            except Exception as e:
                self.logger.warning(f"Request failed ({attempt}/{max_retries}) for {url}: {e}")
                if attempt == max_retries:
                    raise
                time.sleep(attempt * 1.5)
        raise RuntimeError(f"Failed to fetch {url}")

    def fetch_and_store(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """Subclasses must implement this method to pull and store data."""
        raise NotImplementedError
