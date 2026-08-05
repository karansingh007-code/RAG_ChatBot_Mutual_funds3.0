"""
Configuration module for RAG-based Mutual Fund FAQ Chatbot (Groww)
Scope: Strictly 5 HDFC Mutual Fund Scheme URLs on Groww (No PDFs).
"""

import os
from typing import List, Dict, Any

TARGET_SCHEMES: List[Dict[str, str]] = [
    {
        "name": "HDFC Mid-Cap Opportunities Fund Direct Growth",
        "slug": "hdfc-mid-cap-fund-direct-growth",
        "url": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
        "category": "Mid Cap Fund",
        "amc": "HDFC Mutual Fund"
    },
    {
        "name": "HDFC Flexi Cap / Equity Fund Direct Growth",
        "slug": "hdfc-equity-fund-direct-growth",
        "url": "https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth",
        "category": "Flexi Cap Fund",
        "amc": "HDFC Mutual Fund"
    },
    {
        "name": "HDFC Small Cap Fund Direct Growth",
        "slug": "hdfc-small-cap-fund-direct-growth",
        "url": "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
        "category": "Small Cap Fund",
        "amc": "HDFC Mutual Fund"
    },
    {
        "name": "HDFC Nifty 50 Index Fund Direct Growth",
        "slug": "hdfc-nifty-50-index-fund-direct-growth",
        "url": "https://groww.in/mutual-funds/hdfc-nifty-50-index-fund-direct-growth",
        "category": "Index Fund",
        "amc": "HDFC Mutual Fund"
    },
    {
        "name": "HDFC Balanced Advantage Fund Direct Growth",
        "slug": "hdfc-balanced-advantage-fund-direct-growth",
        "url": "https://groww.in/mutual-funds/hdfc-balanced-advantage-fund-direct-growth",
        "category": "Dynamic Asset Allocation",
        "amc": "HDFC Mutual Fund"
    }
]

# HTTP Scraping Headers
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# Directories & Storage Config
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CHROMA_PERSIST_DIR = os.path.join(BASE_DIR, "chroma_db")
COLLECTION_NAME = "groww_mf_facts"
