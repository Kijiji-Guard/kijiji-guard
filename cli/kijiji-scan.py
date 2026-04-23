#!/usr/bin/env python3
"""
kijiji-scan.py — lightweight entry point that delegates to the orchestrator.
Usage: python kijiji-scan.py [directory] [country]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli.core.orchestrator import KijijiOrchestrator
from cli.core.report import KijijiReport


def run_kijiji_scan(directory: str = "terraform", country: str = "nigeria"):
    print("--- Kijiji-Guard: Protecting Africa's Next Unicorn ---")
    print(f"Scanning: {directory}  |  Country: {country}\n")

    orchestrator = KijijiOrchestrator()
    result = orchestrator.run(target=directory, country=country)

    report = KijijiReport(result)
    report.to_console()


if __name__ == "__main__":
    scan_dir = sys.argv[1] if len(sys.argv) > 1 else "terraform"
    scan_country = sys.argv[2] if len(sys.argv) > 2 else "nigeria"
    run_kijiji_scan(scan_dir, scan_country)
