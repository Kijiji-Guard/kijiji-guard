"""
DigitalOcean Live API Adapter — scans live DO accounts for compliance (stub).

Credentials needed : DIGITALOCEAN_TOKEN (personal access token)
How to obtain      : https://cloud.digitalocean.com/account/api/tokens
Regulations mapped : NDPA 2023, Ghana DPA 2012, Kenya DPA 2019,
                     Rwanda Law 058/2021, Loi 2013-450, Loi 2017-20, Egypt PDPL 2020

When implemented this adapter will check:
  - Spaces (object storage) encryption
  - Managed Database encryption at rest
  - Firewall rules — overly permissive inbound rules
  - Volume encryption
  - Region selection (no AF region currently — flag as INFO)
"""
from cli.core.base_api_scanner import BaseAPIScanner

_NOT_IMPLEMENTED = (
    "DigitalOcean Live API scanner is not yet implemented. "
    "Track progress: https://github.com/Kijiji-Guard/kijiji-guard/issues"
)


class DigitalOceanAdapter(BaseAPIScanner):

    def authenticate(self, credentials: dict) -> bool:
        return False

    def scan(self, country: str) -> list[dict]:
        return [{
            "check_id":    "DO_STUB",
            "check_name":  "DigitalOcean Live API Scanner (not yet implemented)",
            "result":      "WARN",
            "resource":    "digitalocean/account",
            "file_path":   "digitalocean/account",
            "regulation":  "N/A",
            "remediation": _NOT_IMPLEMENTED,
        }]
