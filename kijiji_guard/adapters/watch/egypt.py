from __future__ import annotations

from .base_watcher import BaseWatcher, RegulatoryUpdate

SOURCES = [
    {"name": "Egypt PDPC", "url": "https://pdpc.gov.eg", "type": "scrape"},
]

_HARDCODED = [
    {
        "authority":      "Egypt PDPC",
        "title":          "Egypt PDPL Executive Regulations — November 2025",
        "summary":        "Egypt PDPL Executive Regulations came into force November 2025. "
                          "DPO appointment, 72-hour breach notification, and PDPC approval required "
                          "for cross-border transfers now enforceable.",
        "source_url":     "https://pdpc.gov.eg",
        "category":       "NEW_REGULATION",
        "severity":       "HIGH",
        "published_date": "2025-11-01",
        "tags":           ["PDPL", "executive regulations", "DPO", "2025"],
    },
]


class EgyptWatcher(BaseWatcher):
    country = "egypt"

    def fetch(self) -> list[RegulatoryUpdate]:
        updates: list[RegulatoryUpdate] = []
        updates.extend(self._hardcoded(_HARDCODED))
        updates.extend(self._scrape(SOURCES))
        return self._dedup(updates)
