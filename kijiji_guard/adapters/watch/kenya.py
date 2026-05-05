from __future__ import annotations

from .base_watcher import BaseWatcher, RegulatoryUpdate

SOURCES = [
    {"name": "Kenya ODPC", "url": "https://www.odpc.go.ke/news-events/", "type": "scrape"},
]

_HARDCODED = [
    {
        "authority":      "Kenya ODPC",
        "title":          "Kenya ODPC — Annual Data Audit Submission Required",
        "summary":        "Data controllers must submit annual data audit to ODPC under Kenya DPA 2019 Section 14. "
                          "Penalty up to KSh 5 million or 1% of turnover.",
        "source_url":     "https://www.odpc.go.ke",
        "category":       "DEADLINE",
        "severity":       "HIGH",
        "published_date": "2026-01-01",
        "tags":           ["audit", "annual", "KenyaDPA"],
    },
]


class KenyaWatcher(BaseWatcher):
    country = "kenya"

    def fetch(self) -> list[RegulatoryUpdate]:
        updates: list[RegulatoryUpdate] = []
        updates.extend(self._hardcoded(_HARDCODED))
        updates.extend(self._scrape(SOURCES))
        return self._dedup(updates)
