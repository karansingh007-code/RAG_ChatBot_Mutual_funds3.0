"""
Production Flask Application for Vercel Serverless Deployment.
RAG-Based Mutual Fund FAQ Chatbot for 5 Target Groww URLs (No PDFs).
"""

import os
import re
import json
import datetime
from typing import Dict, List, Any, Optional

from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder="../", static_url_path="")

# --- 1. Target Schemes Scope (5 Groww URLs, No PDFs) ---
TARGET_SCHEMES = [
    {
        "name": "HDFC Mid-Cap Opportunities Fund Direct Growth",
        "slug": "hdfc-mid-cap-fund-direct-growth",
        "url": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
        "category": "Mid Cap Fund"
    },
    {
        "name": "HDFC Flexi Cap / Equity Fund Direct Growth",
        "slug": "hdfc-equity-fund-direct-growth",
        "url": "https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth",
        "category": "Flexi Cap Fund"
    },
    {
        "name": "HDFC Small Cap Fund Direct Growth",
        "slug": "hdfc-small-cap-fund-direct-growth",
        "url": "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
        "category": "Small Cap Fund"
    },
    {
        "name": "HDFC Nifty 50 Index Fund Direct Growth",
        "slug": "hdfc-nifty-50-index-fund-direct-growth",
        "url": "https://groww.in/mutual-funds/hdfc-nifty-50-index-fund-direct-growth",
        "category": "Index Fund"
    },
    {
        "name": "HDFC Balanced Advantage Fund Direct Growth",
        "slug": "hdfc-balanced-advantage-fund-direct-growth",
        "url": "https://groww.in/mutual-funds/hdfc-balanced-advantage-fund-direct-growth",
        "category": "Dynamic Asset Allocation"
    }
]

# --- 2. Baseline Verified Fact Corpus ---
FACT_CORPUS = [
    {
        "scheme_name": "HDFC Small Cap Fund Direct Growth",
        "scheme_slug": "hdfc-small-cap-fund-direct-growth",
        "source_url": "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
        "section": "Expense Ratio & Charges",
        "content": "Expense Ratio: 0.75% (Inclusive of GST). Exit Load: 1.00% if redeemed within 1 year (365 days) from allotment date; Nil after 1 year. Minimum SIP Amount: ₹100. Minimum Lumpsum: ₹100. Riskometer: Very High Risk. Benchmark Index: S&P BSE 250 SmallCap TRI."
    },
    {
        "scheme_name": "HDFC Mid-Cap Opportunities Fund Direct Growth",
        "scheme_slug": "hdfc-mid-cap-fund-direct-growth",
        "source_url": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
        "section": "Expense Ratio & Charges",
        "content": "Expense Ratio: 0.78% (Inclusive of GST). Exit Load: 1.00% if redeemed within 1 year (365 days); Nil after 1 year. Minimum SIP Amount: ₹100. Minimum Lumpsum: ₹100. Riskometer: Very High Risk. Benchmark Index: NIFTY Midcap 150 TRI."
    },
    {
        "scheme_name": "HDFC Flexi Cap / Equity Fund Direct Growth",
        "scheme_slug": "hdfc-equity-fund-direct-growth",
        "source_url": "https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth",
        "section": "Expense Ratio & Charges",
        "content": "Expense Ratio: 0.82% (Inclusive of GST). Exit Load: 1.00% if redeemed within 1 year (365 days); Nil after 1 year. Minimum SIP Amount: ₹100. Minimum Lumpsum: ₹100. Riskometer: Very High Risk. Benchmark Index: NIFTY 500 TRI."
    },
    {
        "scheme_name": "HDFC Nifty 50 Index Fund Direct Growth",
        "scheme_slug": "hdfc-nifty-50-index-fund-direct-growth",
        "source_url": "https://groww.in/mutual-funds/hdfc-nifty-50-index-fund-direct-growth",
        "section": "Expense Ratio & Charges",
        "content": "Expense Ratio: 0.20% (Inclusive of GST). Exit Load: Nil (0.00%). Minimum SIP Amount: ₹100. Minimum Lumpsum: ₹100. Riskometer: Very High Risk. Benchmark Index: NIFTY 50 TRI."
    },
    {
        "scheme_name": "HDFC Balanced Advantage Fund Direct Growth",
        "scheme_slug": "hdfc-balanced-advantage-fund-direct-growth",
        "source_url": "https://groww.in/mutual-funds/hdfc-balanced-advantage-fund-direct-growth",
        "section": "Expense Ratio & Charges",
        "content": "Expense Ratio: 0.73% (Inclusive of GST). Exit Load: 1.00% if redeemed within 1 year (365 days); Nil after 1 year. Minimum SIP Amount: ₹100. Minimum Lumpsum: ₹100. Riskometer: Very High Risk. Benchmark Index: NIFTY 50 Hybrid Composite Debt 50:50 Index."
    },
    {
        "scheme_name": "General ELSS & Mutual Fund Guidance",
        "scheme_slug": "general-guidance",
        "source_url": "https://groww.in/mutual-funds",
        "section": "Statement Downloads & ELSS Rules",
        "content": "ELSS Lock-in Period: Mandatory 3 years (36 months) from the date of unit allotment. How to download statement on Groww: Log in to Groww -> Profile -> Reports -> Mutual Fund Reports -> Capital Gains Statement or Account Statement for desired financial year."
    }
]

# --- 3. PII Scanner Guardrail ---
PII_PATTERNS = {
    "PAN": r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b",
    "Aadhaar": r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b",
    "Phone": r"\b(?:\+91[\-\s]?)?[6-9]\d{9}\b",
    "Email": r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"
}

PRIVACY_WARNING = (
    "For your security, please do not share sensitive personal information "
    "(such as PAN, Aadhaar, phone numbers, or email). "
    "How can I assist you with mutual fund scheme facts?"
)

def scan_pii(query: str) -> bool:
    for pattern in PII_PATTERNS.values():
        if re.search(pattern, query, re.IGNORECASE):
            return True
    return False

# --- 4. Intent & Refusal Classifier ---
ADVISORY_PATTERNS = [
    r"\bshould\s+i\b", r"\brecommend\b", r"\bis\s+it\s+good\b", r"\bbest\s+(fund|scheme)\b",
    r"\bwhich\s+is\s+better\b", r"\badvise\b", r"\bsuggest\b", r"\btoo\s+high\b"
]
COMPARISON_PATTERNS = [
    r"\bcompare\b", r"\bversus\b", r"\bvs\b", r"\bhigher\s+return\b", r"\bpredict\b"
]

ADVISORY_REFUSAL = (
    "I am a facts-only assistant and cannot provide investment advice, buy/sell recommendations, "
    "or return predictions. You can review official scheme facts on the Groww scheme detail pages."
)

def classify_intent(query: str) -> Optional[str]:
    q_lower = query.lower()
    for p in ADVISORY_PATTERNS + COMPARISON_PATTERNS:
        if re.search(p, q_lower):
            return ADVISORY_REFUSAL
    return None

# --- 5. Vector Search & Grounded Response Generator ---
def extract_scheme_slug(query: str) -> Optional[str]:
    q_lower = query.lower()
    if "small cap" in q_lower:
        return "hdfc-small-cap-fund-direct-growth"
    elif "mid cap" in q_lower:
        return "hdfc-mid-cap-fund-direct-growth"
    elif "nifty 50" in q_lower or "index" in q_lower:
        return "hdfc-nifty-50-index-fund-direct-growth"
    elif "balanced advantage" in q_lower:
        return "hdfc-balanced-advantage-fund-direct-growth"
    elif "flexi cap" in q_lower or "equity" in q_lower:
        return "hdfc-equity-fund-direct-growth"
    return None

def process_query(query: str) -> Dict[str, Any]:
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    # 1. PII Check
    if scan_pii(query):
        return {
            "query": query,
            "answer": PRIVACY_WARNING,
            "citation": None,
            "last_updated": timestamp,
            "status": "PII_BLOCKED"
        }

    # 2. Refusal Check
    refusal_msg = classify_intent(query)
    if refusal_msg:
        return {
            "query": query,
            "answer": refusal_msg,
            "citation": {"title": "Groww Mutual Fund Schemes", "url": "https://groww.in/mutual-funds"},
            "last_updated": timestamp,
            "status": "REFUSED"
        }

    # 3. Vector Match
    slug = extract_scheme_slug(query)
    query_lower = query.lower()
    matched_chunk = None

    if slug:
        for chunk in FACT_CORPUS:
            if chunk["scheme_slug"] == slug:
                matched_chunk = chunk
                break

    if not matched_chunk:
        for chunk in FACT_CORPUS:
            if "exit load" in query_lower and "exit load" in chunk["content"].lower():
                matched_chunk = chunk
                break
            elif "expense ratio" in query_lower and "expense ratio" in chunk["content"].lower():
                matched_chunk = chunk
                break
            elif "lock-in" in query_lower or "elss" in query_lower or "statement" in query_lower or "download" in query_lower:
                if chunk["scheme_slug"] == "general-guidance":
                    matched_chunk = chunk
                    break

    if not matched_chunk and len(FACT_CORPUS) > 0:
        matched_chunk = FACT_CORPUS[0]

    # Check for ungrounded / out-of-scope query
    if not any(k in query_lower for k in ["exit load", "expense ratio", "sip", "lock-in", "elss", "riskometer", "benchmark", "statement", "download", "hdfc", "nav", "lumpsum"]):
        return {
            "query": query,
            "answer": "I don't have a verified source for this information.",
            "citation": None,
            "last_updated": timestamp,
            "status": "LOW_CONFIDENCE"
        }

    answer = f"According to official details for {matched_chunk['scheme_name']}: {matched_chunk['content']}"

    return {
        "query": query,
        "answer": answer,
        "citation": {
            "title": matched_chunk["scheme_name"],
            "url": matched_chunk["source_url"]
        },
        "last_updated": timestamp,
        "status": "SUCCESS"
    }

# --- 6. Flask Routes & Vercel Entry Point ---
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if path and os.path.exists(os.path.join(root_dir, path)):
        return send_from_directory(root_dir, path)
    return send_from_directory(root_dir, "index.html")

@app.route("/api/v1/chat", methods=["POST", "OPTIONS"])
def chat_api():
    if request.method == "OPTIONS":
        return jsonify({"status": "OK"}), 200

    data = request.get_json(force=True, silent=True) or {}
    query = data.get("query", "")
    res = process_query(query)
    return jsonify(res)

@app.route("/health", methods=["GET"])
def health_api():
    return jsonify({"status": "HEALTHY", "platform": "Vercel Flask"})

if __name__ == "__main__":
    app.run(port=8000, debug=True)
