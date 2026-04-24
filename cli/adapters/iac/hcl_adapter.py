"""
Lightweight IaC scanner using python-hcl2.

No Checkov dependency. Parses Terraform HCL files directly and runs
Kijiji-Guard custom policies as plain Python classes.

Install: pip install python-hcl2
"""
import os

from cli.core.base_iac_scanner import BaseIaCScanner

REGULATION_LABELS = {
    "nigeria":      "NDPA 2023",
    "ghana":        "Ghana DPA 2012",
    "kenya":        "Kenya DPA 2019",
    "rwanda":       "Rwanda Law No.058/2021",
    "cote-divoire": "Loi n°2013-450 (Côte d'Ivoire)",
    "benin":        "Loi n°2017-20 (Bénin)",
    "egypt":        "Egypt PDPL Law No.151/2020",
}

ALL_COUNTRIES = list(REGULATION_LABELS.keys())


class HCLAdapter(BaseIaCScanner):
    """
    Lightweight IaC scanner using python-hcl2.
    No Checkov dependency. Parses Terraform HCL files directly
    and runs Kijiji-Guard custom policies as Python functions.

    Install: pip install python-hcl2
    """

    def scan(self, path: str, country: str) -> list[dict]:
        countries = ALL_COUNTRIES if country == "all" else [country]
        tf_files  = self._find_tf_files(path)

        if not tf_files:
            return [{
                "check_id":    "KG_NO_TF_FILES",
                "check_name":  "No Terraform files found",
                "result":      "WARN",
                "resource":    path,
                "file_path":   path,
                "regulation":  "N/A",
                "remediation": f"No .tf files found at '{path}'. "
                               "Pass a .tf file path or a directory containing .tf files.",
            }]

        findings: list[dict] = []
        for filepath in tf_files:
            parsed = self._parse_tf_file(filepath)
            if not parsed:
                continue
            for c in countries:
                findings.extend(self._run_policies(parsed, filepath, c))

        return findings

    # ------------------------------------------------------------------ #

    def _find_tf_files(self, path: str) -> list[str]:
        if os.path.isfile(path):
            return [path] if path.endswith(".tf") else []
        if os.path.isdir(path):
            result = []
            for root, _, files in os.walk(path):
                for f in files:
                    if f.endswith(".tf"):
                        result.append(os.path.join(root, f))
            return sorted(result)
        return []

    def _parse_tf_file(self, filepath: str) -> dict:
        try:
            import hcl2
            with open(filepath, encoding="utf-8", errors="replace") as f:
                return hcl2.load(f)
        except ImportError:
            return {"__error__": "python-hcl2 not installed — run: pip install python-hcl2"}
        except Exception:
            return {}

    def _run_policies(self, parsed: dict, filepath: str, country: str) -> list[dict]:
        policy_class = _POLICY_MAP.get(country)
        if policy_class is None:
            return [{
                "check_id":    "KG_UNKNOWN_COUNTRY",
                "check_name":  f"Unknown country: {country}",
                "result":      "WARN",
                "resource":    filepath,
                "file_path":   filepath,
                "regulation":  "N/A",
                "remediation": f"Supported countries: {', '.join(ALL_COUNTRIES)}",
            }]
        return policy_class(parsed, filepath).run()


# ------------------------------------------------------------------ #
# Lazy import map — avoids top-level import of every policy module    #
# ------------------------------------------------------------------ #

def _load_policy_map() -> dict:
    from cli.adapters.iac.policies.nigeria      import NigeriaPolicies
    from cli.adapters.iac.policies.ghana        import GhanaPolicies
    from cli.adapters.iac.policies.kenya        import KenyaPolicies
    from cli.adapters.iac.policies.rwanda       import RwandaPolicies
    from cli.adapters.iac.policies.cote_divoire import CoteDivoirePolicies
    from cli.adapters.iac.policies.benin        import BeninPolicies
    from cli.adapters.iac.policies.egypt        import EgyptPolicies
    return {
        "nigeria":      NigeriaPolicies,
        "ghana":        GhanaPolicies,
        "kenya":        KenyaPolicies,
        "rwanda":       RwandaPolicies,
        "cote-divoire": CoteDivoirePolicies,
        "benin":        BeninPolicies,
        "egypt":        EgyptPolicies,
    }

_POLICY_MAP: dict = _load_policy_map()
