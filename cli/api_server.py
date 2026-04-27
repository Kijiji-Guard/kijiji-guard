"""
Kijiji-Guard FastAPI server — wraps KijijiOrchestrator for the web dashboard.

Run with:
  py -m uvicorn cli.api_server:app --reload --port 8000
"""
import json
import os
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from cli.core.orchestrator import KijijiOrchestrator
from cli.core.report import KijijiReport

app = FastAPI(title="Kijiji-Guard API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".scan_history.json")

REGULATIONS = [
    {
        "country": "Nigeria",
        "code": "nigeria",
        "regulation_name": "Nigeria Data Protection Act (NDPA) 2023",
        "governing_body": "Nigeria Data Protection Commission (NDPC)",
        "penalty_summary": "Up to 2% of annual gross revenue or ₦10 million for first offence; 4% or ₦20 million for repeat",
        "supported_adapters": ["IaC (Checkov)", "AWS (stub)", "GCP (stub)", "Azure (stub)"],
    },
    {
        "country": "Ghana",
        "code": "ghana",
        "regulation_name": "Data Protection Act 2012 (Act 843)",
        "governing_body": "Data Protection Commission (DPC) Ghana",
        "penalty_summary": "Fines up to GH₵150,000 and/or imprisonment up to 5 years for serious violations",
        "supported_adapters": ["IaC (Checkov)"],
    },
    {
        "country": "Kenya",
        "code": "kenya",
        "regulation_name": "Data Protection Act 2019",
        "governing_body": "Office of the Data Protection Commissioner (ODPC)",
        "penalty_summary": "Fines up to KSh5 million or 1% of annual turnover; criminal penalties for officers",
        "supported_adapters": ["IaC (Checkov)"],
    },
    {
        "country": "Rwanda",
        "code": "rwanda",
        "regulation_name": "Law No.058/2021 on Personal Data Protection",
        "governing_body": "Rwanda Utilities Regulatory Authority (RURA)",
        "penalty_summary": "Fines RWF 1 million – RWF 50 million; mandatory strict data localisation (af-south-1)",
        "supported_adapters": ["IaC (Checkov)", "Supabase (SB_003)", "Vercel (VCL_005)"],
    },
    {
        "country": "Côte d'Ivoire",
        "code": "cote-divoire",
        "regulation_name": "Loi n°2013-450 relative à la protection des données à caractère personnel",
        "governing_body": "Autorité de Régulation des Télécommunications (ARTCI)",
        "penalty_summary": "Fines up to XOF 50 million and/or imprisonment 1–5 years",
        "supported_adapters": ["IaC (Checkov)"],
    },
    {
        "country": "Bénin",
        "code": "benin",
        "regulation_name": "Loi n°2017-20 portant code du numérique en République du Bénin",
        "governing_body": "Autorité de Protection des Données Personnelles (APDP)",
        "penalty_summary": "Fines up to XOF 25 million; criminal liability for data controllers",
        "supported_adapters": ["IaC (Checkov)"],
    },
    {
        "country": "Egypt",
        "code": "egypt",
        "regulation_name": "Personal Data Protection Law (PDPL) No.151 of 2020",
        "governing_body": "Personal Data Protection Centre (PDPC)",
        "penalty_summary": "Fines EGP 100,000 – EGP 1 million; up to EGP 5 million for sensitive data breaches",
        "supported_adapters": ["IaC (Checkov)"],
    },
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_history() -> list[dict[str, Any]]:
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def _save_history(history: list[dict[str, Any]]) -> None:
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class ScanRequest(BaseModel):
    target: str
    country: str
    credentials: dict[str, str] = {}


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": "0.1.0"}


@app.get("/regulations")
def regulations() -> list[dict[str, Any]]:
    return REGULATIONS


@app.post("/scan")
def run_scan(req: ScanRequest) -> dict[str, Any]:
    orchestrator = KijijiOrchestrator()
    result: dict[str, Any] = orchestrator.run(
        target=req.target,
        country=req.country,
        credentials=req.credentials,
    )
    result["id"] = str(uuid.uuid4())
    result["timestamp"] = datetime.now(timezone.utc).isoformat()

    history = _load_history()
    history.insert(0, result)
    _save_history(history[:100])

    return result


@app.get("/scan/history")
def scan_history() -> list[dict[str, Any]]:
    history = _load_history()
    return [
        {
            "id":         s.get("id", ""),
            "timestamp":  s.get("timestamp", ""),
            "target":     s.get("target", ""),
            "country":    s.get("country", ""),
            "scan_types": s.get("scan_types", []),
            "summary":    s.get("summary", {}),
        }
        for s in history[:20]
    ]


@app.get("/scan/history/{scan_id}")
def scan_history_by_id(scan_id: str) -> dict[str, Any]:
    for scan in _load_history():
        if scan.get("id") == scan_id:
            return scan
    raise HTTPException(status_code=404, detail="Scan not found")


@app.post("/report/html", response_class=HTMLResponse)
def html_report(scan_result: dict[str, Any]) -> str:
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w") as f:
        tmppath = f.name
    try:
        KijijiReport(scan_result).to_html(tmppath)
        with open(tmppath, encoding="utf-8") as f:
            return f.read()
    finally:
        if os.path.exists(tmppath):
            os.unlink(tmppath)


# ---------------------------------------------------------------------------
# KijijiWatch endpoints
# ---------------------------------------------------------------------------

@app.get("/watch/{country}")
def watch_country(country: str) -> dict[str, Any]:
    """Fetch new regulatory updates for a country (or 'all')."""
    from cli.core.watcher import KijijiWatcher
    return KijijiWatcher().run(country=country, show_all=False)


@app.get("/watch/{country}/all")
def watch_country_all(country: str) -> dict[str, Any]:
    """Fetch all regulatory updates including previously seen ones."""
    from cli.core.watcher import KijijiWatcher
    return KijijiWatcher().run(country=country, show_all=True)
