from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class RegulatoryUpdate:
    """A single regulatory update from a data protection authority."""

    id:             str
    country:        str
    authority:      str
    title:          str
    summary:        str
    source_url:     str
    category:       str   # DEADLINE|ENFORCEMENT|FINE|INVESTIGATION|NEW_REGULATION|CIRCULAR|GUIDANCE|OTHER
    severity:       str   # HIGH|MEDIUM|LOW
    published_date: str
    fetched_at:     str
    tags:           list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id":             self.id,
            "country":        self.country,
            "authority":      self.authority,
            "title":          self.title,
            "summary":        self.summary,
            "source_url":     self.source_url,
            "category":       self.category,
            "severity":       self.severity,
            "published_date": self.published_date,
            "fetched_at":     self.fetched_at,
            "tags":           self.tags,
        }

    @staticmethod
    def make_id(title: str, url: str) -> str:
        return hashlib.sha256(f"{title}{url}".encode()).hexdigest()[:16]


class BaseWatcher(ABC):
    """
    Base class for all country regulatory watchers.
    Each country subclass monitors its own set of regulator websites.
    """

    country:     str       = ""
    authorities: list[dict] = []

    def __init__(self) -> None:
        self.updates: list[RegulatoryUpdate] = []

    @abstractmethod
    def fetch(self) -> list[RegulatoryUpdate]:
        """
        Fetch latest updates from all authority sources.
        Must handle connection errors gracefully — never crash.
        """

    # ------------------------------------------------------------------ #
    # Shared helpers                                                       #
    # ------------------------------------------------------------------ #

    def classify(self, title: str, summary: str) -> tuple[str, str]:
        """Classify an update by (category, severity) using keyword rules."""
        text = (title + " " + summary).lower()

        if any(w in text for w in [
            "deadline", "due date", "extension", "returns due",
            "filing", "30 may", "march 15", "audit return",
        ]):
            return "DEADLINE", "HIGH"

        if any(w in text for w in [
            "fine", "penalty", "sanction", "₦", "million naira", "billion",
        ]):
            return "FINE", "HIGH"

        if any(w in text for w in [
            "investigat", "probe", "inquiry", "temu", "meta", "multichoice",
        ]):
            return "INVESTIGATION", "HIGH"

        if any(w in text for w in [
            "enforcement", "compliance notice", "show cause",
            "violation", "breach",
        ]):
            return "ENFORCEMENT", "HIGH"

        if any(w in text for w in [
            "regulation", "act", "law", "gazette", "framework",
            "guidelines issued", "new policy", "executive regulations",
        ]):
            return "NEW_REGULATION", "MEDIUM"

        if any(w in text for w in [
            "circular", "directive", "press release", "advisory",
        ]):
            return "CIRCULAR", "MEDIUM"

        if any(w in text for w in ["guidance", "clarification", "faq", "q&a"]):
            return "GUIDANCE", "LOW"

        return "OTHER", "LOW"

    def _scrape(self, sources: list[dict]) -> list[RegulatoryUpdate]:
        """
        Generic scraper: GET each source URL, parse links with bs4.
        Returns whatever can be found; skips silently on errors.
        """
        import warnings
        from urllib.parse import urljoin

        import httpx
        from bs4 import BeautifulSoup

        results: list[RegulatoryUpdate] = []
        now = datetime.now(timezone.utc).isoformat()

        for source in sources:
            try:
                resp = httpx.get(
                    source["url"],
                    headers={"User-Agent": "KijijiWatch/1.0"},
                    timeout=15,
                    follow_redirects=True,
                )
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")

                for a in soup.find_all("a", href=True):
                    text = a.get_text(strip=True)
                    if len(text) < 20:
                        continue
                    href = a["href"]
                    if href.startswith("/"):
                        href = urljoin(source["url"], href)
                    elif not href.startswith("http"):
                        continue

                    category, severity = self.classify(text, "")
                    uid = RegulatoryUpdate.make_id(text, href)

                    results.append(RegulatoryUpdate(
                        id=uid,
                        country=self.country,
                        authority=source["name"],
                        title=text,
                        summary=text,
                        source_url=href,
                        category=category,
                        severity=severity,
                        published_date="2026-01-01",
                        fetched_at=now,
                    ))
            except Exception:
                pass  # Site unreachable — silently skip

        return results

    @staticmethod
    def _dedup(updates: list[RegulatoryUpdate]) -> list[RegulatoryUpdate]:
        seen: set[str] = set()
        out: list[RegulatoryUpdate] = []
        for u in updates:
            if u.id not in seen:
                seen.add(u.id)
                out.append(u)
        return out

    def _hardcoded(self, items: list[dict]) -> list[RegulatoryUpdate]:
        """Convert a list of dicts into RegulatoryUpdate objects."""
        now = datetime.now(timezone.utc).isoformat()
        results = []
        for d in items:
            uid = RegulatoryUpdate.make_id(d["title"], d.get("source_url", ""))
            results.append(RegulatoryUpdate(
                id=uid,
                country=self.country,
                authority=d["authority"],
                title=d["title"],
                summary=d["summary"],
                source_url=d.get("source_url", ""),
                category=d["category"],
                severity=d["severity"],
                published_date=d.get("published_date", "2026-01-01"),
                fetched_at=now,
                tags=d.get("tags", []),
            ))
        return results
