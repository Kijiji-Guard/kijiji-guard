from __future__ import annotations

from .base_watcher import BaseWatcher, RegulatoryUpdate

SOURCES = [
    {"name": "Ghana DPC", "url": "https://www.dataprotection.org.gh/news", "type": "scrape"},
]

_HARDCODED = [
    {
        "authority":      "Ghana DPC",
        "title":          "Ghana Data Protection Act 2012 — Annual Registration Renewal Required",
        "summary":        "All data controllers must renew annual registration with Ghana DPC. "
                          "Non-registration is a criminal offence under Act 843.",
        "source_url":     "https://www.dataprotection.org.gh",
        "category":       "DEADLINE",
        "severity":       "HIGH",
        "published_date": "2026-01-01",
        "tags":           ["registration", "renewal", "Act843"],
    },
]


class GhanaWatcher(BaseWatcher):
    country = "ghana"

    def fetch(self) -> list[RegulatoryUpdate]:
        updates: list[RegulatoryUpdate] = []
        updates.extend(self._hardcoded(_HARDCODED))
        updates.extend(self._scrape(SOURCES))
        return self._dedup(updates)
