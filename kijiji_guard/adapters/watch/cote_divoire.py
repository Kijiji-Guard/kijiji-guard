from __future__ import annotations

from .base_watcher import BaseWatcher, RegulatoryUpdate

SOURCES = [
    {"name": "ARTCI", "url": "https://www.artci.ci/index.php/actualites", "type": "scrape"},
]

_HARDCODED = [
    {
        "authority":      "ARTCI",
        "title":          "Côte d'Ivoire Loi 2013-450 — ARTCI Data Protection Enforcement Active",
        "summary":        "ARTCI actively enforces Loi 2013-450. Data controllers must declare processing "
                          "activities. Sensitive data requires prior authorisation from ARTCI.",
        "source_url":     "https://www.artci.ci",
        "category":       "GUIDANCE",
        "severity":       "MEDIUM",
        "published_date": "2026-01-01",
        "tags":           ["ARTCI", "declaration", "authorisation", "CIV"],
    },
]


class CoteDivoireWatcher(BaseWatcher):
    country = "cote-divoire"

    def fetch(self) -> list[RegulatoryUpdate]:
        updates: list[RegulatoryUpdate] = []
        updates.extend(self._hardcoded(_HARDCODED))
        updates.extend(self._scrape(SOURCES))
        return self._dedup(updates)
