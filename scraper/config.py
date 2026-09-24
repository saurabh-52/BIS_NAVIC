"""
BIS Standards Scraper — Configuration
"""

# ── API Base URLs ────────────────────────────────────────────
REVIEW_SERVICE = "https://standardsadmin.bis.gov.in/review-service/"
PROJECT_SERVICE = "https://standardsadmin.bis.gov.in/project-service/"
PROPOSAL_SERVICE = "https://standardsadmin.bis.gov.in/proposal-service/"
MASTER_SERVICE = "https://standardsadmin.bis.gov.in/master-service/"

# ── BIS file CDN base (for PDF downloads, gazette docs, etc.) ──
BIS_FILE_BASE = "https://standardsadmin.bis.gov.in"

# ── Common request payload fields ────────────────────────────
# These fields are sent with every API request (mimicking the Angular app)
COMMON_PAYLOAD = {
    "token": None,
    "refreshToken": None,
    "clientId": None,
    "clientSecret": None,
    "sub": None,
}

# ── Database ─────────────────────────────────────────────────
import os
DB_PATH = os.path.join(os.path.dirname(__file__), "bis_standards.db")

REQUEST_DELAY_SECONDS = 0.5  # delay between API calls to avoid hammering

# ── HTTP Headers ─────────────────────────────────────────────
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
}
