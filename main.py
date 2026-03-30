import typer
import yaml
import os
import subprocess
import json
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import Optional

app = typer.Typer(help="Kijiji-Guard: Indigenous NDPA 2023 Compliance Scanner")
console = Console()

@app.command()
def init():
    """
    Initializes Kijiji-Guard with a sample config and policies folder.
    """
    console.print("[bold green]Initializing Kijiji-Guard...[/bold green]")
    
    # Create policies folder
    if not os.path.exists("policies"):
        os.makedirs("policies")
        console.print("Created /policies directory.")
    
    # Create sample config
    config = {
        "project_name": "MyAfricanUnicorn",
        "compliance_standard": "NDPA-2023",
        "target_regions": ["af-south-1", "eu-west-1"],
        "encryption_mandate": "AES256"
    }
    
    with open("kijiji-config.yaml", "w") as f:
        yaml.dump(config, f)
    
    console.print("Created kijiji-config.yaml.")
    console.print("[bold blue]Initialization complete! 🛡️[/bold blue]")

@app.command()
def scan(path: str = typer.Argument(".", help="Path to Terraform files")):
    """
    Scans Terraform files for NDPA 2023 violations.
    """
    console.print(f"[bold]Scanning path: {path}[/bold]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Running Kijiji-Guard Security Engine...", total=None)
        
        # Run Checkov via subprocess
        # We point it to our custom policies folder
        try:
            cmd = [
                "checkov",
                "-d", path,
                "--external-checks-dir", "policies",
                "--check", "CKV_NGR",
                "--output", "json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Checkov returns non-zero if violations found, so we check stdout
            if not result.stdout:
                console.print("[red]Error: Checkov failed to run. Ensure it is installed.[/red]")
                return

            scan_data = json.loads(result.stdout)
            
            # Extract results
            # Checkov returns a list if multiple frameworks are scanned, or a single object
            if isinstance(scan_data, list):
                results = scan_data[0].get("results", {})
            else:
                results = scan_data.get("results", {})
                
            passed_checks = results.get("passed_checks", [])
            failed_checks = results.get("failed_checks", [])
            
            # Build Table
            table = Table(title="Kijiji-Guard NDPA Compliance Report")
            table.add_column("ID", style="cyan")
            table.add_column("NDPA Section", style="magenta")
            table.add_column("Resource", style="white")
            table.add_column("Status", justify="center")

            # Mapping IDs to Sections
            section_map = {
                "CKV_NGR_001": "Section 41 (Residency)",
                "CKV_NGR_002": "Section 24 (Retention)",
                "CKV_NGR_003": "Section 34 (Encryption)"
            }

            for check in passed_checks:
                table.add_row(
                    check['check_id'],
                    section_map.get(check['check_id'], "N/A"),
                    check['resource'],
                    "[green]PASS[/green]"
                )

            for check in failed_checks:
                table.add_row(
                    check['check_id'],
                    section_map.get(check['check_id'], "N/A"),
                    check['resource'],
                    "[red]FAIL[/red]"
                )

            console.print(table)
            
            # Summary
            total = len(passed_checks) + len(failed_checks)
            if total > 0:
                score = (len(passed_checks) / total) * 100
                console.print(f"\n[bold]Compliance Score: {score:.2f}%[/bold]")
                if score < 100:
                    console.print("[yellow]Action required: Fix violations before the March 2026 Audit cycle.[/yellow]")
                else:
                    console.print("[green]Excellent! Your infrastructure is Sovereign-Ready. 🇳🇬[/green]")
            else:
                console.print("[yellow]No NDPA checks were executed. Check your policy directory.[/yellow]")

        except Exception as e:
            console.print(f"[red]Scan failed: {str(e)}[/red]")

if __name__ == "__main__":
    app()
