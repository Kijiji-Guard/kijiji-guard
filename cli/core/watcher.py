"""
KijijiWatch — regulatory intelligence orchestrator.
Mirrors how orchestrator.py works for scans.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from cli.adapters.watch.nigeria      import NigeriaWatcher
from cli.adapters.watch.ghana        import GhanaWatcher
from cli.adapters.watch.kenya        import KenyaWatcher
from cli.adapters.watch.rwanda       import RwandaWatcher
from cli.adapters.watch.egypt        import EgyptWatcher
from cli.adapters.watch.benin        import BeninWatcher
from cli.adapters.watch.cote_divoire import CoteDivoireWatcher

DB_PATH = Path(__file__).parent.parent / ".watch_cache.db"

WATCHERS: dict[str, type] = {
    "nigeria":      NigeriaWatcher,
    "ghana":        GhanaWatcher,
    "kenya":        KenyaWatcher,
    "rwanda":       RwandaWatcher,
    "egypt":        EgyptWatcher,
    "benin":        BeninWatcher,
    "cote-divoire": CoteDivoireWatcher,
}

SEVERITY_COLORS = {"HIGH": "red", "MEDIUM": "yellow", "LOW": "green"}

# Text-only labels for Windows cp1252 terminal compatibility
CATEGORY_LABEL = {
    "DEADLINE":       "DEADLINE",
    "ENFORCEMENT":    "ENFORCEMENT",
    "FINE":           "FINE",
    "INVESTIGATION":  "INVESTIGATION",
    "NEW_REGULATION": "NEW REGULATION",
    "CIRCULAR":       "CIRCULAR",
    "GUIDANCE":       "GUIDANCE",
    "OTHER":          "OTHER",
}

SEVERITY_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}

console = Console()


class KijijiWatcher:

    def __init__(self) -> None:
        self._init_db()

    # ------------------------------------------------------------------ #
    # SQLite helpers                                                       #
    # ------------------------------------------------------------------ #

    def _init_db(self) -> None:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(str(DB_PATH)) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS updates (
                    id             TEXT PRIMARY KEY,
                    country        TEXT,
                    authority      TEXT,
                    title          TEXT,
                    category       TEXT,
                    severity       TEXT,
                    source_url     TEXT,
                    published_date TEXT,
                    fetched_at     TEXT
                )
            """)
            conn.commit()

    def _is_new(self, update_id: str) -> bool:
        with sqlite3.connect(str(DB_PATH)) as conn:
            row = conn.execute(
                "SELECT 1 FROM updates WHERE id = ?", (update_id,)
            ).fetchone()
        return row is None

    def _save(self, updates: list) -> None:
        if not updates:
            return
        with sqlite3.connect(str(DB_PATH)) as conn:
            for u in updates:
                d = u.to_dict() if hasattr(u, "to_dict") else u
                try:
                    conn.execute(
                        """INSERT OR IGNORE INTO updates
                           (id, country, authority, title, category,
                            severity, source_url, published_date, fetched_at)
                           VALUES (?,?,?,?,?,?,?,?,?)""",
                        (
                            d["id"], d["country"], d["authority"], d["title"],
                            d["category"], d["severity"], d["source_url"],
                            d["published_date"], d["fetched_at"],
                        ),
                    )
                except Exception:
                    pass
            conn.commit()

    # ------------------------------------------------------------------ #
    # Main entry point                                                     #
    # ------------------------------------------------------------------ #

    def run(self, country: str, show_all: bool = False) -> dict[str, Any]:
        watcher_classes = (
            list(WATCHERS.values()) if country == "all"
            else ([WATCHERS[country]] if country in WATCHERS else [])
        )

        all_updates: list = []
        for cls in watcher_classes:
            try:
                all_updates.extend(cls().fetch())
            except Exception:
                pass

        new_updates = [u for u in all_updates if self._is_new(u.id)]
        self._save(new_updates)

        display = all_updates if show_all else new_updates

        by_severity = {
            "HIGH":   sum(1 for u in display if u.severity == "HIGH"),
            "MEDIUM": sum(1 for u in display if u.severity == "MEDIUM"),
            "LOW":    sum(1 for u in display if u.severity == "LOW"),
        }

        return {
            "country":     country,
            "total":       len(all_updates),
            "new":         len(new_updates),
            "updates":     [u.to_dict() for u in display],
            "by_severity": by_severity,
        }

    # ------------------------------------------------------------------ #
    # Rich display                                                         #
    # ------------------------------------------------------------------ #

    def display(self, result: dict[str, Any]) -> None:
        country  = result.get("country", "all")
        total    = result.get("total", 0)
        new      = result.get("new", 0)
        updates  = result.get("updates", [])
        by_sev   = result.get("by_severity", {})

        console.print(Panel(
            f"[bold]KijijiWatch — Regulatory Intelligence[/bold]\n"
            f"Country: [cyan]{country}[/cyan] | "
            f"[white]{total}[/white] fetched | "
            f"[yellow]{new}[/yellow] new",
            style="bold blue",
        ))

        if not updates:
            console.print(Panel(
                "[bold green]No new regulatory updates. You are up to date.[/bold green]",
                style="green",
            ))
            return

        # Sort: HIGH first, then by date descending
        sorted_updates = sorted(
            updates,
            key=lambda u: (
                SEVERITY_ORDER.get(u.get("severity", "LOW"), 2),
                u.get("published_date", ""),
            ),
            reverse=False,
        )
        # Reverse date within each severity group is handled implicitly;
        # we re-sort with a secondary reverse on date:
        sorted_updates = sorted(
            updates,
            key=lambda u: (
                SEVERITY_ORDER.get(u.get("severity", "LOW"), 2),
                u.get("published_date", ""),
            ),
        )

        table = Table(show_header=True, header_style="bold cyan", expand=True)
        table.add_column("Severity",  style="bold",   no_wrap=True, width=10)
        table.add_column("Category",  style="white",  no_wrap=True, width=18)
        table.add_column("Authority", style="cyan",   no_wrap=True, width=16)
        table.add_column("Title",     style="white",  ratio=4)
        table.add_column("Date",      style="dim",    no_wrap=True, width=12)

        for u in sorted_updates:
            sev   = u.get("severity", "LOW")
            cat   = u.get("category", "OTHER")
            color = SEVERITY_COLORS.get(sev, "white")
            label = CATEGORY_LABEL.get(cat, cat)
            table.add_row(
                f"[{color}]{sev}[/{color}]",
                label,
                u.get("authority", ""),
                u.get("title", ""),
                u.get("published_date", ""),
            )

        console.print(table)

        high   = by_sev.get("HIGH", 0)
        medium = by_sev.get("MEDIUM", 0)
        low    = by_sev.get("LOW", 0)

        console.print(Panel(
            f"[red]HIGH: {high}[/red]    "
            f"[yellow]MEDIUM: {medium}[/yellow]    "
            f"[green]LOW: {low}[/green]",
            title="Summary",
        ))

        if high > 0:
            console.print(
                f"\n[bold red]WARNING: {high} high-priority regulatory update(s) require "
                "your attention. Review immediately to avoid penalties and "
                "enforcement action.[/bold red]"
            )
