"""
Railway PaaS Adapter — scans Railway projects for compliance (stub).

Credentials needed : RAILWAY_TOKEN (account token)
How to obtain      : https://railway.app/account/tokens
Regulations mapped : NDPA 2023, Ghana DPA 2012, Kenya DPA 2019,
                     Rwanda Law 058/2021, Loi 2013-450, Loi 2017-20, Egypt PDPL 2020

When implemented this adapter will check:
  - Environment variable secrets exposure
  - Private networking enabled (not public ports)
  - Custom domain with TLS
  - Database volume encryption
  - Region awareness (no Africa region — flag as INFO)
"""
from cli.core.base_paas_scanner import BasePaaSScanner

_NOT_IMPLEMENTED = (
    "Railway PaaS scanner is not yet implemented. "
    "Track progress: https://github.com/Kijiji-Guard/kijiji-guard/issues"
)


class RailwayAdapter(BasePaaSScanner):

    def authenticate(self, credentials: dict) -> bool:
        return False

    def get_config(self) -> dict:
        return {}

    def scan(self, country: str) -> list[dict]:
        return [{
            "check_id":    "RLW_STUB",
            "check_name":  "Railway PaaS Scanner (not yet implemented)",
            "result":      "WARN",
            "resource":    "railway/project",
            "file_path":   "railway/project",
            "regulation":  "N/A",
            "remediation": _NOT_IMPLEMENTED,
        }]
