"""
Checkov IaC Adapter — runs Checkov with Kijiji-Guard custom policy directories.

Credentials needed : none (reads local IaC files)
How to install     : pip install checkov
Regulations mapped : NDPA 2023, Ghana DPA 2012, Kenya DPA 2019,
                     Rwanda Law 058/2021, Loi 2013-450, Loi 2017-20, Egypt PDPL 2020
"""
import json
import os
import subprocess

from cli.core.base_iac_scanner import BaseIaCScanner

# Map country slug → policies sub-directory name
COUNTRY_DIRS = {
    "nigeria":      "nigeria",  # flat root policies/ folder for Nigeria
    "ghana":        "ghana",
    "kenya":        "kenya",
    "rwanda":       "rwanda",
    "cote-divoire": "cote-divoire",
    "benin":        "benin",
    "egypt":        "egypt",
}

# Regulation label for each country
REGULATION_LABELS = {
    "nigeria":      "NDPA 2023",
    "ghana":        "Ghana DPA 2012",
    "kenya":        "Kenya DPA 2019",
    "rwanda":       "Rwanda Law No.058/2021",
    "cote-divoire": "Loi n°2013-450",
    "benin":        "Loi n°2017-20",
    "egypt":        "Egypt PDPL 2020",
}


def _policies_root() -> str:
    """Return absolute path to the top-level policies/ directory."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", "..", "..", "policies"))


class CheckovAdapter(BaseIaCScanner):

    def scan(self, path: str, country: str) -> list[dict]:
        countries = list(COUNTRY_DIRS.keys()) if country == "all" else [country]
        findings: list[dict] = []

        for c in countries:
            findings.extend(self._scan_country(path, c))

        return findings

    # ------------------------------------------------------------------
    def _scan_country(self, path: str, country: str) -> list[dict]:
        policies_root = _policies_root()

        if country == "nigeria":
            # Nigeria policies live flat in policies/ root
            checks_dir = policies_root
        else:
            checks_dir = os.path.join(policies_root, COUNTRY_DIRS.get(country, country))

        if not os.path.isdir(checks_dir):
            return [{
                "check_id":    "KG_MISSING_POLICY",
                "check_name":  f"No policy directory for country: {country}",
                "result":      "WARN",
                "resource":    path,
                "file_path":   checks_dir,
                "regulation":  REGULATION_LABELS.get(country, country),
                "remediation": f"Create policies/{COUNTRY_DIRS.get(country, country)}/ and add policy files.",
            }]

        cmd = [
            "checkov",
            "-d", path,
            "--external-checks-dir", checks_dir,
            "--output", "json",
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        except FileNotFoundError:
            return [{
                "check_id":    "KG_CHECKOV_MISSING",
                "check_name":  "Checkov not installed",
                "result":      "WARN",
                "resource":    path,
                "file_path":   path,
                "regulation":  REGULATION_LABELS.get(country, country),
                "remediation": "pip install checkov",
            }]
        except subprocess.TimeoutExpired:
            return [{
                "check_id":    "KG_CHECKOV_TIMEOUT",
                "check_name":  "Checkov scan timed out",
                "result":      "WARN",
                "resource":    path,
                "file_path":   path,
                "regulation":  REGULATION_LABELS.get(country, country),
                "remediation": "Reduce scan scope or increase timeout.",
            }]

        if not result.stdout:
            return [{
                "check_id":    "KG_CHECKOV_NO_OUTPUT",
                "check_name":  "Checkov produced no output",
                "result":      "WARN",
                "resource":    path,
                "file_path":   path,
                "regulation":  REGULATION_LABELS.get(country, country),
                "remediation": result.stderr or "Check that the path contains IaC files.",
            }]

        try:
            raw = json.loads(result.stdout)
        except json.JSONDecodeError:
            return [{
                "check_id":    "KG_CHECKOV_PARSE_ERR",
                "check_name":  "Could not parse Checkov JSON output",
                "result":      "WARN",
                "resource":    path,
                "file_path":   path,
                "regulation":  REGULATION_LABELS.get(country, country),
                "remediation": "Ensure checkov version >= 3.x",
            }]

        if isinstance(raw, list):
            results = raw[0].get("results", {}) if raw else {}
        else:
            results = raw.get("results", {})

        findings: list[dict] = []
        regulation = REGULATION_LABELS.get(country, country)

        for check in results.get("passed_checks", []):
            findings.append(self._normalise(check, "PASSED", regulation))

        for check in results.get("failed_checks", []):
            findings.append(self._normalise(check, "FAILED", regulation))

        return findings

    @staticmethod
    def _normalise(check: dict, result: str, regulation: str) -> dict:
        return {
            "check_id":    check.get("check_id", "UNKNOWN"),
            "check_name":  check.get("check_name", ""),
            "result":      result,
            "resource":    check.get("resource", ""),
            "file_path":   check.get("file_path", ""),
            "regulation":  regulation,
            "remediation": check.get("description") or check.get("check_name", ""),
        }
