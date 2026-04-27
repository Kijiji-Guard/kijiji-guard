import json
import os
import sys
from typing import Optional

import typer
import yaml
from dotenv import load_dotenv
from rich.console import Console

# Allow running from any working directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli.core.orchestrator import KijijiOrchestrator
from cli.core.report import KijijiReport

load_dotenv()

app     = typer.Typer(help="Kijiji-Guard: African Security-as-Code Compliance Scanner")
console = Console()

VALID_COUNTRIES = [
    "nigeria", "ghana", "kenya", "rwanda",
    "cote-divoire", "benin", "egypt", "all",
]
VALID_OUTPUTS = ["console", "json", "html"]


@app.command()
def init():
    """Initialise Kijiji-Guard with a sample config and policies folder."""
    console.print("[bold green]Initializing Kijiji-Guard...[/bold green]")

    if not os.path.exists("policies"):
        os.makedirs("policies")
        console.print("Created /policies directory.")

    config = {
        "project_name":       "MyAfricanUnicorn",
        "compliance_standard": "NDPA-2023",
        "target_regions":     ["af-south-1", "eu-west-1"],
        "encryption_mandate": "AES256",
    }
    with open("kijiji-config.yaml", "w") as f:
        yaml.dump(config, f)

    console.print("Created kijiji-config.yaml.")
    console.print("[bold blue]Initialization complete![/bold blue]")


@app.command()
def scan(
    path: Optional[str] = typer.Argument(None, help="Path to IaC files (legacy positional arg)"),
    target: str = typer.Option(
        "auto",
        "--target", "-t",
        help="Scan target: file/dir path, 'aws','gcp','azure','digitalocean',"
             "'vercel','supabase','firebase','render','railway', or 'auto'",
    ),
    country: str = typer.Option(
        "nigeria",
        "--country", "-c",
        help=f"Regulation country: {', '.join(VALID_COUNTRIES)}",
    ),
    output: str = typer.Option(
        "console",
        "--output", "-o",
        help="Output format: console, json, html",
    ),
    output_file: Optional[str] = typer.Option(
        None,
        "--output-file", "-f",
        help="Output file path (for json/html formats)",
    ),
    credentials: Optional[str] = typer.Option(
        None,
        "--credentials",
        help="Path to JSON file with API tokens/keys",
    ),
):
    """Scan infrastructure for African data protection regulation compliance."""

    # Legacy positional arg support
    if path and target == "auto":
        target = path

    if country not in VALID_COUNTRIES:
        console.print(f"[red]Unknown country '{country}'. Choose from: {', '.join(VALID_COUNTRIES)}[/red]")
        raise typer.Exit(1)

    if output not in VALID_OUTPUTS:
        console.print(f"[red]Unknown output '{output}'. Choose from: {', '.join(VALID_OUTPUTS)}[/red]")
        raise typer.Exit(1)

    # Load credentials
    creds: dict = {}
    if credentials and os.path.isfile(credentials):
        with open(credentials) as f:
            creds = json.load(f)

    console.print(f"[bold]Kijiji-Guard scanning:[/bold] target=[cyan]{target}[/cyan]  country=[cyan]{country}[/cyan]")

    orchestrator = KijijiOrchestrator()
    result = orchestrator.run(target=target, country=country, credentials=creds)

    report = KijijiReport(result)

    if output == "console":
        report.to_console()
    elif output == "json":
        out_path = output_file or "kijiji-report.json"
        report.to_json(out_path)
    elif output == "html":
        out_path = output_file or "kijiji-report.html"
        report.to_html(out_path)


@app.command()
def watch(
    country: str = typer.Option(
        "nigeria",
        "--country", "-c",
        help="Country to monitor: nigeria, ghana, kenya, rwanda, egypt, benin, cote-divoire, or 'all'",
    ),
    all_updates: bool = typer.Option(
        False,
        "--all",
        help="Show all updates including previously seen ones",
    ),
    output: str = typer.Option(
        "console",
        "--output", "-o",
        help="Output format: console, json",
    ),
):
    """
    🔔 KijijiWatch — Monitor African regulatory updates.

    Track changes from NDPC, Ghana DPC, Kenya ODPC, Rwanda NCSA,
    Egypt PDPC and more. Get alerted to deadlines, enforcement
    actions, and new regulations before they affect your business.
    """
    from cli.core.watcher import KijijiWatcher

    watcher = KijijiWatcher()
    result  = watcher.run(country=country, show_all=all_updates)

    if output == "json":
        import json
        print(json.dumps(result, indent=2, default=str))
    else:
        watcher.display(result)


if __name__ == "__main__":
    app()
