from __future__ import annotations

from .base_watcher import BaseWatcher, RegulatoryUpdate

SOURCES = [
    {"name": "NDPC",              "url": "https://ndpc.gov.ng/news",                          "type": "scrape"},
    {"name": "NDPC Press Releases","url": "https://ndpc.gov.ng/media",                         "type": "scrape"},
    {"name": "CBN Circulars",     "url": "https://www.cbn.gov.ng/supervision/Inst-DM.asp",     "type": "scrape"},
    {"name": "NCC Consumer",      "url": "https://www.ncc.gov.ng/news-and-publications",       "type": "scrape"},
]

_HARDCODED = [
    {
        "authority":      "NDPC",
        "title":          "2025 Data Protection Compliance Audit Returns Due",
        "summary":        "NDPC extended deadline for filing 2025 DPCAR to 30 May 2026. "
                          "All data controllers and processors must file or face sanctions under NDPA.",
        "source_url":     "https://ndpc.gov.ng",
        "category":       "DEADLINE",
        "severity":       "HIGH",
        "published_date": "2026-04-01",
        "tags":           ["audit", "DPCAR", "deadline", "NDPA"],
    },
    {
        "authority":      "NDPC",
        "title":          "1,368 Organizations Issued Compliance Notices",
        "summary":        "NDPC issued compliance notices to 1,368 orgs including 795 financial institutions. "
                          "Evidence of DPO appointment and audit returns required within 21 days of notice.",
        "source_url":     "https://ndpc.gov.ng",
        "category":       "ENFORCEMENT",
        "severity":       "HIGH",
        "published_date": "2025-08-01",
        "tags":           ["enforcement", "compliance notice", "DPO", "financial"],
    },
    {
        "authority":      "NDPC",
        "title":          "NDPC Investigating Temu for NDPA Violations",
        "summary":        "NDPC launched investigation into Temu's data processing of ~12.7 million "
                          "Nigerian data subjects. Cross-border transfer and data minimisation concerns.",
        "source_url":     "https://ndpc.gov.ng",
        "category":       "INVESTIGATION",
        "severity":       "HIGH",
        "published_date": "2026-02-16",
        "tags":           ["investigation", "Temu", "cross-border", "enforcement"],
    },
]


class NigeriaWatcher(BaseWatcher):
    country = "nigeria"

    def fetch(self) -> list[RegulatoryUpdate]:
        updates: list[RegulatoryUpdate] = []
        updates.extend(self._hardcoded(_HARDCODED))
        updates.extend(self._scrape(SOURCES))
        return self._dedup(updates)
