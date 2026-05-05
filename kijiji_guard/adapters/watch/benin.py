from __future__ import annotations

from .base_watcher import BaseWatcher, RegulatoryUpdate

SOURCES = [
    {"name": "Benin CRIET", "url": "https://www.criet.bj", "type": "scrape"},
]

_HARDCODED = [
    {
        "authority":      "CRIET",
        "title":          "Benin Loi n°2017-20 — Personal Data Processing Registration Required",
        "summary":        "All data processors in Benin must register with CRIET (Commission du Révélateur "
                          "de l'Information et des Technologies) before processing personal data.",
        "source_url":     "https://www.criet.bj",
        "category":       "GUIDANCE",
        "severity":       "MEDIUM",
        "published_date": "2026-01-01",
        "tags":           ["registration", "Benin", "Loi2017-20"],
    },
]


class BeninWatcher(BaseWatcher):
    country = "benin"

    def fetch(self) -> list[RegulatoryUpdate]:
        updates: list[RegulatoryUpdate] = []
        updates.extend(self._hardcoded(_HARDCODED))
        updates.extend(self._scrape(SOURCES))
        return self._dedup(updates)
