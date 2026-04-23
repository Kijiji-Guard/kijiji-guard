"""
Supabase PaaS Adapter — scans Supabase projects via the Supabase Management API v1.

Credentials needed : SUPABASE_ACCESS_TOKEN (personal access token)
How to obtain      : https://supabase.com/dashboard/account/tokens
Regulations mapped : NDPA 2023, Ghana DPA 2012, Kenya DPA 2019,
                     Rwanda Law 058/2021, Loi 2013-450, Loi 2017-20, Egypt PDPL 2020
"""
import os

import requests

from cli.core.base_paas_scanner import BasePaaSScanner

BASE_URL = "https://api.supabase.com"

AFRICA_REGIONS   = {"af-south-1"}
STRICT_COUNTRIES = {"rwanda"}
WARN_COUNTRIES   = {"kenya", "ghana", "egypt"}

REGULATION_MAP = {
    "nigeria":      "NDPA 2023, Section 39",
    "ghana":        "Ghana DPA 2012, Section 28",
    "kenya":        "Kenya DPA 2019, Section 41",
    "rwanda":       "Rwanda Law 058/2021, Article 50",
    "cote-divoire": "Loi n°2013-450, Article 36",
    "benin":        "Loi n°2017-20, Article 550",
    "egypt":        "Egypt PDPL 2020, Article 19",
}


class SupabaseAdapter(BasePaaSScanner):

    def __init__(self):
        self._token: str = ""
        self._headers: dict = {}

    # ------------------------------------------------------------------
    def authenticate(self, credentials: dict) -> bool:
        self._token = (
            credentials.get("supabase_token")
            or os.environ.get("SUPABASE_ACCESS_TOKEN", "")
        )
        if not self._token:
            return False
        self._headers = {"Authorization": f"Bearer {self._token}"}
        try:
            r = requests.get(f"{BASE_URL}/v1/projects", headers=self._headers, timeout=10)
            return r.status_code == 200
        except requests.RequestException:
            return False

    # ------------------------------------------------------------------
    def get_config(self) -> dict:
        projects = []
        try:
            r = requests.get(f"{BASE_URL}/v1/projects", headers=self._headers, timeout=10)
            r.raise_for_status()
            for proj in r.json():
                try:
                    detail = requests.get(
                        f"{BASE_URL}/v1/projects/{proj['id']}",
                        headers=self._headers, timeout=10,
                    )
                    detail.raise_for_status()
                    projects.append(detail.json())
                except requests.RequestException:
                    projects.append(proj)
        except requests.RequestException as e:
            return {"error": str(e), "projects": []}
        return {"projects": projects}

    # ------------------------------------------------------------------
    def scan(self, country: str) -> list[dict]:
        if not self._token:
            return [self._warn("SB_AUTH", "Supabase authentication not configured",
                               "N/A", "Set SUPABASE_ACCESS_TOKEN environment variable.")]

        config = self.get_config()
        if "error" in config:
            return [self._warn("SB_API_ERR", "Could not reach Supabase API",
                               "supabase/api", config["error"])]

        findings: list[dict] = []
        regulation = REGULATION_MAP.get(country, "Data protection regulations")

        for project in config.get("projects", []):
            ref  = project.get("id", project.get("ref", "unknown"))
            name = project.get("name", ref)
            resource = f"supabase/{name}"

            findings += self._check_sb001(project, name, resource, regulation)
            findings += self._check_sb002(ref, name, resource, regulation)
            findings += self._check_sb003(project, name, resource, country)
            findings += self._check_sb004(ref, name, resource, regulation)
            findings += self._check_sb005(ref, name, resource, regulation)
            findings += self._check_sb006(project, name, resource, country, regulation)

        return findings

    # ------ SB_001 — Encryption at rest -----------------------------------
    def _check_sb001(self, project, name, resource, regulation) -> list[dict]:
        # Supabase managed Postgres is encrypted at rest on all plans.
        # We verify the region is set (confirms managed hosting) and flag accordingly.
        region = project.get("region", "")
        result = "PASSED" if region else "WARN"
        remediation = (
            "Supabase managed Postgres is encrypted at rest by default."
            if region
            else "Could not confirm region — verify project is on Supabase managed hosting."
        )
        return [self._finding("SB_001", "Encryption at rest",
                              result, resource, f"supabase/{name}", regulation, remediation)]

    # ------ SB_002 — Row Level Security -----------------------------------
    def _check_sb002(self, ref, name, resource, regulation) -> list[dict]:
        try:
            r = requests.get(
                f"{BASE_URL}/v1/projects/{ref}/database/tables",
                headers=self._headers, timeout=10,
            )
            r.raise_for_status()
            tables = r.json()
        except requests.RequestException as e:
            return [self._warn("SB_002", "Could not fetch tables for RLS check",
                               resource, str(e))]

        no_rls = [t.get("name", "") for t in tables if not t.get("rls_enabled", False)]
        result = "FAILED" if no_rls else "PASSED"
        remediation = (
            f"Enable RLS on these tables: {', '.join(no_rls)}. "
            "Without RLS any authenticated user can read all rows."
            if no_rls
            else "RLS is enabled on all tables."
        )
        return [self._finding("SB_002", "Row Level Security (RLS) enabled",
                              result, resource, f"supabase/{name}", regulation, remediation)]

    # ------ SB_003 — Data region compliance --------------------------------
    def _check_sb003(self, project, name, resource, country) -> list[dict]:
        region     = project.get("region", "unknown")
        regulation = REGULATION_MAP.get(country, "Data protection regulations")
        file_path  = f"supabase/{name}"

        if country in STRICT_COUNTRIES and region not in AFRICA_REGIONS:
            return [self._finding(
                "SB_003", "Data region compliance", "FAILED",
                resource, file_path, regulation,
                f"Rwanda Law 058/2021 Article 50 requires data in af-south-1. Current region: {region}.",
            )]

        if country in WARN_COUNTRIES and region not in AFRICA_REGIONS:
            return [self._finding(
                "SB_003", "Data region compliance", "WARN",
                resource, file_path, regulation,
                f"{country.title()} recommends af-south-1 for data residency. Current region: {region}.",
            )]

        return [self._finding(
            "SB_003", "Data region compliance", "INFO",
            resource, file_path, regulation,
            f"Project region: {region}.",
        )]

    # ------ SB_004 — Auth email confirmation -------------------------------
    def _check_sb004(self, ref, name, resource, regulation) -> list[dict]:
        try:
            r = requests.get(
                f"{BASE_URL}/v1/projects/{ref}/config/auth",
                headers=self._headers, timeout=10,
            )
            r.raise_for_status()
            auth_config = r.json()
        except requests.RequestException as e:
            return [self._warn("SB_004", "Could not fetch auth config", resource, str(e))]

        email_enabled   = auth_config.get("external", {}).get("email", {}).get("enabled", False)
        autoconfirm     = auth_config.get("mailer_autoconfirm", True)
        result = "PASSED" if (email_enabled and not autoconfirm) else "FAILED"
        remediation = (
            "Email auth is enabled and confirmation is required — good."
            if result == "PASSED"
            else "Disable mailer_autoconfirm in Supabase Auth settings to require email verification."
        )
        return [self._finding("SB_004", "Auth email confirmation enabled",
                              result, resource, f"supabase/{name}", regulation, remediation)]

    # ------ SB_005 — JWT expiry / anon key exposure ------------------------
    def _check_sb005(self, ref, name, resource, regulation) -> list[dict]:
        try:
            r = requests.get(
                f"{BASE_URL}/v1/projects/{ref}/config/auth",
                headers=self._headers, timeout=10,
            )
            r.raise_for_status()
            auth_config = r.json()
        except requests.RequestException as e:
            return [self._warn("SB_005", "Could not fetch auth config for JWT check",
                               resource, str(e))]

        jwt_expiry = auth_config.get("jwt_expiry", 3600)
        result = "PASSED" if jwt_expiry <= 3600 else "FAILED"
        remediation = (
            f"JWT expiry is {jwt_expiry}s (> 3600s). Set jwt_expiry ≤ 3600 to limit token lifetime."
            if result == "FAILED"
            else f"JWT expiry is {jwt_expiry}s — within the recommended 1-hour limit."
        )
        return [self._finding("SB_005", "JWT expiry / anon key exposure",
                              result, resource, f"supabase/{name}", regulation, remediation)]

    # ------ SB_006 — Point-in-time recovery / backups ----------------------
    def _check_sb006(self, project, name, resource, country, regulation) -> list[dict]:
        tier = project.get("subscription_tier", "free").lower()
        has_pitr = tier not in ("free",)

        if has_pitr:
            result = "PASSED"
            remediation = f"Project is on '{tier}' plan — PITR enabled."
        else:
            result = "WARN"
            remediation = (
                "Project is on Free plan — no PITR, only daily backups. "
                "Upgrade to Pro for point-in-time recovery."
            )

        return [self._finding("SB_006", "Point-in-time recovery / backups",
                              result, resource, f"supabase/{name}",
                              REGULATION_MAP.get(country, regulation), remediation)]

    # ------ helpers -------------------------------------------------------
    @staticmethod
    def _finding(check_id, check_name, result, resource,
                 file_path, regulation, remediation) -> dict:
        return {
            "check_id":    check_id,
            "check_name":  check_name,
            "result":      result,
            "resource":    resource,
            "file_path":   file_path,
            "regulation":  regulation,
            "remediation": remediation,
        }

    def _warn(self, check_id, check_name, resource, remediation) -> dict:
        return self._finding(check_id, check_name, "WARN", resource,
                             resource, "N/A", remediation)
