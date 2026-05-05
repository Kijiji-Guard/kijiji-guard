"""
Kijiji-Guard Report Engine — renders scan results as console, JSON, or HTML.
"""
import json
import os
from datetime import datetime, timezone

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

RESULT_STYLE = {
    "PASSED": "[bold green]PASSED[/bold green]",
    "FAILED": "[bold red]FAILED[/bold red]",
    "WARN":   "[bold yellow]WARN[/bold yellow]",
    "INFO":   "[bold blue]INFO[/bold blue]",
}

COUNTRY_LABELS = {
    "nigeria":      "Nigeria — NDPA 2023",
    "ghana":        "Ghana — DPA 2012",
    "kenya":        "Kenya — DPA 2019",
    "rwanda":       "Rwanda — Law No.058/2021",
    "cote-divoire": "Côte d'Ivoire — Loi n°2013-450",
    "benin":        "Bénin — Loi n°2017-20",
    "egypt":        "Egypt — PDPL 2020",
    "all":          "All Countries",
}


class KijijiReport:

    def __init__(self, scan_result: dict):
        self.result = scan_result

    # ------------------------------------------------------------------
    def to_console(self) -> None:
        country = self.result.get("country", "unknown")
        target  = self.result.get("target", ".")
        types   = ", ".join(self.result.get("scan_types", []))
        summary = self.result.get("summary", {})
        findings = self.result.get("findings", [])

        console.print(Panel(
            f"[bold]Kijiji-Guard Compliance Scan[/bold]\n"
            f"Target: {target}  |  Country: {COUNTRY_LABELS.get(country, country)}  |  Scanners: {types}",
            style="bold blue",
        ))

        table = Table(show_header=True, header_style="bold cyan", expand=True)
        table.add_column("Check ID",    style="cyan",  no_wrap=True)
        table.add_column("Name",        style="white", ratio=3)
        table.add_column("Result",      justify="center", no_wrap=True)
        table.add_column("Resource",    style="white", ratio=2)
        table.add_column("Regulation",  style="magenta", ratio=2)
        table.add_column("Remediation", style="yellow", ratio=4)

        for f in findings:
            result_str = RESULT_STYLE.get(f["result"], f["result"])
            table.add_row(
                f.get("check_id", ""),
                f.get("check_name", ""),
                result_str,
                f.get("resource", ""),
                f.get("regulation", ""),
                f.get("remediation", ""),
            )

        console.print(table)

        passed    = summary.get("passed", 0)
        failed    = summary.get("failed", 0)
        total     = summary.get("total", 0)
        pass_rate = summary.get("pass_rate", 0.0)

        color = "green" if failed == 0 else ("yellow" if pass_rate >= 70 else "red")
        console.print(Panel(
            f"[bold {color}]Total: {total}  |  Passed: {passed}  |  Failed: {failed}  |  Pass rate: {pass_rate}%[/bold {color}]",
            title="Summary",
        ))

        if failed == 0 and total > 0:
            console.print("[bold green]All checks passed — your infrastructure is Sovereign-Ready![/bold green]")
        elif failed > 0:
            console.print("[yellow]Fix violations before your next compliance audit cycle.[/yellow]")

    # ------------------------------------------------------------------
    def to_json(self, output_path: str) -> None:
        with open(output_path, "w", encoding="utf-8") as fh:
            json.dump(self.result, fh, indent=2)
        console.print(f"[green]JSON report written to {output_path}[/green]")

    # ------------------------------------------------------------------
    def to_html(self, output_path: str) -> None:
        country  = self.result.get("country", "unknown")
        target   = self.result.get("target", ".")
        summary  = self.result.get("summary", {})
        findings = self.result.get("findings", [])
        scan_date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        rows_html = ""
        for f in findings:
            cls = {"PASSED": "pass", "FAILED": "fail", "WARN": "warn", "INFO": "info"}.get(f["result"], "info")
            rows_html += f"""
            <tr class="{cls}">
              <td>{f.get('check_id','')}</td>
              <td>{f.get('check_name','')}</td>
              <td class="badge {cls}">{f.get('result','')}</td>
              <td>{f.get('resource','')}</td>
              <td>{f.get('regulation','')}</td>
              <td>{f.get('remediation','')}</td>
            </tr>"""

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Kijiji-Guard Compliance Report</title>
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #0f172a; color: #e2e8f0; margin: 0; padding: 24px; }}
  h1   {{ color: #38bdf8; }} h2 {{ color: #94a3b8; font-size: 1rem; font-weight: normal; }}
  .meta {{ display: flex; gap: 24px; margin: 16px 0 24px; }}
  .meta span {{ background: #1e293b; padding: 8px 16px; border-radius: 8px; font-size: 0.85rem; }}
  .summary {{ display: flex; gap: 16px; margin-bottom: 24px; }}
  .card {{ background: #1e293b; border-radius: 10px; padding: 20px 28px; text-align: center; flex: 1; }}
  .card .num {{ font-size: 2rem; font-weight: bold; }}
  .pass .num {{ color: #4ade80; }} .fail .num {{ color: #f87171; }}
  .warn .num {{ color: #fbbf24; }} .total .num {{ color: #38bdf8; }}
  table {{ width: 100%; border-collapse: collapse; background: #1e293b; border-radius: 10px; overflow: hidden; }}
  th {{ background: #0f172a; padding: 12px 14px; text-align: left; font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; }}
  td {{ padding: 11px 14px; border-bottom: 1px solid #0f172a; font-size: 0.875rem; vertical-align: top; }}
  tr.pass {{ background: #052e16; }} tr.fail {{ background: #2d0a0a; }}
  tr.warn {{ background: #2d1f00; }} tr.info {{ background: #0c1a2e; }}
  .badge {{ font-weight: bold; border-radius: 4px; padding: 2px 8px; font-size: 0.75rem; }}
  .badge.pass {{ color: #4ade80; }} .badge.fail {{ color: #f87171; }}
  .badge.warn {{ color: #fbbf24; }} .badge.info {{ color: #38bdf8; }}
  footer {{ margin-top: 32px; color: #475569; font-size: 0.75rem; text-align: center; }}
</style>
</head>
<body>
<h1>Kijiji-Guard Compliance Report</h1>
<h2>Securing Africa's Next Unicorns — without the Dollar-Denominated Security Tax</h2>
<div class="meta">
  <span>Project / Target: <strong>{target}</strong></span>
  <span>Country: <strong>{COUNTRY_LABELS.get(country, country)}</strong></span>
  <span>Scan Date: <strong>{scan_date}</strong></span>
</div>
<div class="summary">
  <div class="card total"><div class="num">{summary.get('total',0)}</div><div>Total Checks</div></div>
  <div class="card pass"><div class="num">{summary.get('passed',0)}</div><div>Passed</div></div>
  <div class="card fail"><div class="num">{summary.get('failed',0)}</div><div>Failed</div></div>
  <div class="card warn"><div class="num">{summary.get('pass_rate',0)}%</div><div>Pass Rate</div></div>
</div>
<table>
<thead><tr>
  <th>Check ID</th><th>Name</th><th>Result</th>
  <th>Resource</th><th>Regulation</th><th>Remediation</th>
</tr></thead>
<tbody>{rows_html}</tbody>
</table>
<footer>Generated by Kijiji-Guard &mdash; <a href="https://github.com/Kijiji-Guard/kijiji-guard" style="color:#38bdf8">github.com/Kijiji-Guard/kijiji-guard</a></footer>
</body>
</html>"""

        with open(output_path, "w", encoding="utf-8") as fh:
            fh.write(html)
        console.print(f"[green]HTML report written to {output_path}[/green]")
