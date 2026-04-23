"""
Kijiji-Guard Orchestrator — auto-detects infrastructure type and routes
to the correct adapter(s), then merges all findings into a unified result.
"""
import os


COUNTRY_POLICY_DIRS = {
    "nigeria":      "nigeria",
    "ghana":        "ghana",
    "kenya":        "kenya",
    "rwanda":       "rwanda",
    "cote-divoire": "cote-divoire",
    "benin":        "benin",
    "egypt":        "egypt",
}

IAC_EXTENSIONS = {".tf", ".yaml", ".yml", ".json"}
IAC_FILENAMES  = {"docker-compose.yml", "docker-compose.yaml"}


class KijijiOrchestrator:

    def detect_scan_type(self, target: str) -> list[str]:
        types = []

        if target in ("aws", "gcp", "azure", "digitalocean"):
            return [f"api:{target}"]

        if target in ("vercel", "supabase", "firebase", "render", "railway"):
            return [f"paas:{target}"]

        if target == "auto":
            target = "."

        # File-level detection
        if os.path.isfile(target):
            _, ext = os.path.splitext(target)
            name = os.path.basename(target)
            if ext in IAC_EXTENSIONS or name in IAC_FILENAMES:
                types.append("iac")
            return types

        # Directory-level detection
        if os.path.isdir(target):
            for root, _, files in os.walk(target):
                for f in files:
                    _, ext = os.path.splitext(f)
                    if ext in {".tf", ".yaml", ".yml"} or f in IAC_FILENAMES:
                        if "iac" not in types:
                            types.append("iac")
                    if f == "vercel.json":
                        if "paas:vercel" not in types:
                            types.append("paas:vercel")
                if os.path.join(root, "supabase", "config.toml"):
                    pass
            # supabase check at root
            if os.path.exists(os.path.join(target, "supabase", "config.toml")):
                types.append("paas:supabase")
            if "vercel" in target.lower():
                if "paas:vercel" not in types:
                    types.append("paas:vercel")
            if "supabase" in target.lower():
                if "paas:supabase" not in types:
                    types.append("paas:supabase")

        return types if types else ["iac"]

    def run(self, target: str, country: str, credentials: dict = {}) -> dict:
        scan_types = self.detect_scan_type(target)
        all_findings: list[dict] = []

        for scan_type in scan_types:
            findings = self._run_scanner(scan_type, target, country, credentials)
            all_findings.extend(findings)

        passed = sum(1 for f in all_findings if f["result"] == "PASSED")
        failed = sum(1 for f in all_findings if f["result"] == "FAILED")
        total  = len(all_findings)
        pass_rate = round((passed / total * 100), 2) if total else 0.0

        return {
            "target":     target,
            "country":    country,
            "scan_types": scan_types,
            "findings":   all_findings,
            "summary": {
                "total":     total,
                "passed":    passed,
                "failed":    failed,
                "pass_rate": pass_rate,
            },
        }

    # ------------------------------------------------------------------
    def _run_scanner(self, scan_type: str, target: str, country: str,
                     credentials: dict) -> list[dict]:
        try:
            if scan_type == "iac":
                from cli.adapters.iac.checkov_adapter import CheckovAdapter
                return CheckovAdapter().scan(target, country)

            if scan_type == "paas:vercel":
                from cli.adapters.paas.vercel_adapter import VercelAdapter
                adapter = VercelAdapter()
                adapter.authenticate(credentials)
                return adapter.scan(country)

            if scan_type == "paas:supabase":
                from cli.adapters.paas.supabase_adapter import SupabaseAdapter
                adapter = SupabaseAdapter()
                adapter.authenticate(credentials)
                return adapter.scan(country)

            if scan_type == "paas:firebase":
                from cli.adapters.paas.firebase_adapter import FirebaseAdapter
                adapter = FirebaseAdapter()
                adapter.authenticate(credentials)
                return adapter.scan(country)

            if scan_type == "paas:render":
                from cli.adapters.paas.render_adapter import RenderAdapter
                adapter = RenderAdapter()
                adapter.authenticate(credentials)
                return adapter.scan(country)

            if scan_type == "paas:railway":
                from cli.adapters.paas.railway_adapter import RailwayAdapter
                adapter = RailwayAdapter()
                adapter.authenticate(credentials)
                return adapter.scan(country)

            if scan_type == "api:aws":
                from cli.adapters.api.aws_adapter import AWSAdapter
                adapter = AWSAdapter()
                adapter.authenticate(credentials)
                return adapter.scan(country)

            if scan_type == "api:gcp":
                from cli.adapters.api.gcp_adapter import GCPAdapter
                adapter = GCPAdapter()
                adapter.authenticate(credentials)
                return adapter.scan(country)

            if scan_type == "api:azure":
                from cli.adapters.api.azure_adapter import AzureAdapter
                adapter = AzureAdapter()
                adapter.authenticate(credentials)
                return adapter.scan(country)

            if scan_type == "api:digitalocean":
                from cli.adapters.api.digitalocean_adapter import DigitalOceanAdapter
                adapter = DigitalOceanAdapter()
                adapter.authenticate(credentials)
                return adapter.scan(country)

        except Exception as e:
            return [{
                "check_id":    "KG_SCAN_ERROR",
                "check_name":  f"Scanner error ({scan_type})",
                "result":      "WARN",
                "resource":    target,
                "file_path":   target,
                "regulation":  "N/A",
                "remediation": str(e),
            }]

        return []
