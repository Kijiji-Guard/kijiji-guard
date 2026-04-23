"""
Vercel PaaS Adapter — scans Vercel projects via the Vercel REST API v9.

Credentials needed : VERCEL_TOKEN (account-level token)
How to obtain      : https://vercel.com/account/tokens
Regulations mapped : NDPA 2023, Ghana DPA 2012, Kenya DPA 2019,
                     Rwanda Law 058/2021, Egypt PDPL 2020 (HTTPS + access control)
"""
import os

import requests

from cli.core.base_paas_scanner import BasePaaSScanner

BASE_URL = "https://api.vercel.com"

SENSITIVE_KEY_PATTERNS = (
    "SECRET", "KEY", "PASSWORD", "TOKEN",
    "DATABASE_URL", "SUPABASE", "FIREBASE", "API_KEY",
)

REGULATION_MAP = {
    "nigeria":      "NDPA 2023, Section 39",
    "ghana":        "Ghana DPA 2012, Section 28",
    "kenya":        "Kenya DPA 2019, Section 41",
    "rwanda":       "Rwanda Law 058/2021, Article 22",
    "cote-divoire": "Loi n°2013-450, Article 36",
    "benin":        "Loi n°2017-20, Article 550",
    "egypt":        "Egypt PDPL 2020, Article 19",
}

RESIDENCY_COUNTRIES = {"nigeria", "rwanda"}


class VercelAdapter(BasePaaSScanner):

    def __init__(self):
        self._token: str = ""
        self._headers: dict = {}

    # ------------------------------------------------------------------
    def authenticate(self, credentials: dict) -> bool:
        self._token = (
            credentials.get("vercel_token")
            or os.environ.get("VERCEL_TOKEN", "")
        )
        if not self._token:
            return False
        self._headers = {"Authorization": f"Bearer {self._token}"}
        try:
            r = requests.get(f"{BASE_URL}/v2/user", headers=self._headers, timeout=10)
            return r.status_code == 200
        except requests.RequestException:
            return False

    # ------------------------------------------------------------------
    def get_config(self) -> dict:
        projects = []
        try:
            r = requests.get(f"{BASE_URL}/v9/projects", headers=self._headers, timeout=10)
            r.raise_for_status()
            for proj in r.json().get("projects", []):
                try:
                    detail = requests.get(
                        f"{BASE_URL}/v9/projects/{proj['id']}",
                        headers=self._headers,
                        timeout=10,
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
            return [self._warn("VCL_AUTH", "Vercel authentication not configured",
                               "N/A", "Set VERCEL_TOKEN environment variable.")]

        config = self.get_config()
        if "error" in config:
            return [self._warn("VCL_API_ERR", "Could not reach Vercel API",
                               "vercel/api", config["error"])]

        findings: list[dict] = []
        regulation = REGULATION_MAP.get(country, "Data protection regulations")

        for project in config.get("projects", []):
            pid  = project.get("id", "unknown")
            name = project.get("name", pid)
            resource = f"vercel/{name}"

            findings += self._check_vcl001(project, name, resource, country, regulation)
            findings += self._check_vcl002(project, name, resource, regulation)
            findings += self._check_vcl003(project, name, resource, regulation)
            findings += self._check_vcl004(project, name, resource, regulation)
            findings += self._check_vcl005(project, name, resource, country, regulation)

        return findings

    # ------ VCL_001 — HTTPS enforcement -----------------------------------
    def _check_vcl001(self, project, name, resource, country, regulation) -> list[dict]:
        # Vercel enforces HTTPS on .vercel.app by default.
        # Check autoExposeSystemEnvs + framework config for explicit HTTP allowance.
        redirects_http = project.get("httpToHttpsRedirect", True)
        result = "PASSED" if redirects_http else "FAILED"
        return [self._finding(
            "VCL_001", "HTTPS enforcement", result, resource,
            f"vercel/{name}",
            REGULATION_MAP.get(country, regulation),
            "Enable HTTPS-only in Vercel project settings > Domains > Redirect HTTP to HTTPS.",
        )]

    # ------ VCL_002 — Env var secrets exposure ----------------------------
    def _check_vcl002(self, project, name, resource, regulation) -> list[dict]:
        findings = []
        pid = project.get("id", "")
        try:
            r = requests.get(
                f"{BASE_URL}/v9/projects/{pid}/env",
                headers=self._headers, timeout=10,
            )
            r.raise_for_status()
            envs = r.json().get("envs", [])
        except requests.RequestException as e:
            return [self._warn("VCL_002", "Could not fetch env vars", resource, str(e))]

        exposed = []
        for env in envs:
            key = env.get("key", "").upper()
            if any(p in key for p in SENSITIVE_KEY_PATTERNS):
                if env.get("type") != "encrypted":
                    exposed.append(env.get("key"))

        result = "FAILED" if exposed else "PASSED"
        remediation = (
            f"Convert these env vars to 'Encrypted' type in Vercel UI: {', '.join(exposed)}"
            if exposed
            else "All sensitive env vars are encrypted."
        )
        findings.append(self._finding(
            "VCL_002", "Environment variable secrets exposure",
            result, resource, f"vercel/{name}", regulation, remediation,
        ))
        return findings

    # ------ VCL_003 — Production deployment protection --------------------
    def _check_vcl003(self, project, name, resource, regulation) -> list[dict]:
        pwd_protection = project.get("passwordProtection") is not None
        sso_protection = project.get("ssoProtection") is not None
        dep_protection = project.get("protectionBypass") is not None
        protected = pwd_protection or sso_protection or dep_protection
        result = "PASSED" if protected else "FAILED"
        return [self._finding(
            "VCL_003", "Production deployment protection",
            result, resource, f"vercel/{name}", regulation,
            "Enable Deployment Protection in Vercel project Settings > Security.",
        )]

    # ------ VCL_004 — Custom domain configured ----------------------------
    def _check_vcl004(self, project, name, resource, regulation) -> list[dict]:
        aliases = project.get("alias", []) or []
        # also check targets.production
        prod = (project.get("targets") or {}).get("production", {})
        aliases += prod.get("alias", []) or []

        custom = [a for a in aliases if not str(a).endswith(".vercel.app")]
        result = "PASSED" if custom else "FAILED"
        return [self._finding(
            "VCL_004", "Custom domain configured (not *.vercel.app)",
            result, resource, f"vercel/{name}", regulation,
            "Add a custom domain in Vercel project Settings > Domains for full data routing control.",
        )]

    # ------ VCL_005 — Region awareness ------------------------------------
    def _check_vcl005(self, project, name, resource, country, regulation) -> list[dict]:
        if country not in RESIDENCY_COUNTRIES:
            return []

        framework = project.get("framework", "")
        regions   = project.get("regions", []) or []
        edge_only = framework in ("edge", "nextjs") and not regions

        if country == "rwanda" and "cdg1" not in regions and "af-south-1" not in str(regions):
            result = "FAILED"
            remediation = "Rwanda Law 058/2021 Article 50 requires data localisation. Pin region to af-south-1 in vercel.json."
        elif edge_only:
            result = "FAILED"
            remediation = "Edge Runtime with no region restrictions may route data outside Africa. Set explicit regions in vercel.json."
        else:
            result = "PASSED"
            remediation = f"Deployment regions documented: {regions or 'default'}."

        return [self._finding(
            "VCL_005", "Region awareness / data residency",
            result, resource, f"vercel/{name}",
            REGULATION_MAP.get(country, regulation), remediation,
        )]

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
