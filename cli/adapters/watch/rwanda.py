from __future__ import annotations

from .base_watcher import BaseWatcher, RegulatoryUpdate

SOURCES = [
    {"name": "Rwanda NCSA", "url": "https://ncsa.gov.rw/news", "type": "scrape"},
]

_HARDCODED = [
    {
        "authority":      "Rwanda NCSA",
        "title":          "Rwanda Law 058/2021 — 48-Hour Breach Notification Requirement Active",
        "summary":        "Rwanda has the strictest breach notification requirement in Africa — 48 hours to NCSA. "
                          "Data must be stored locally unless NCSA certificate obtained for offshore.",
        "source_url":     "https://ncsa.gov.rw",
        "category":       "GUIDANCE",
        "severity":       "HIGH",
        "published_date": "2026-01-01",
        "tags":           ["breach", "notification", "localisation", "48hr"],
    },
]


class RwandaWatcher(BaseWatcher):
    country = "rwanda"

    def fetch(self) -> list[RegulatoryUpdate]:
        updates: list[RegulatoryUpdate] = []
        updates.extend(self._hardcoded(_HARDCODED))
        updates.extend(self._scrape(SOURCES))
        return self._dedup(updates)
