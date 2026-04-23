"""
Azure Live API Adapter — scans live Azure subscriptions for compliance (stub).

Credentials needed : AZURE_SUBSCRIPTION_ID, AZURE_TENANT_ID,
                     AZURE_CLIENT_ID, AZURE_CLIENT_SECRET
How to obtain      : https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps
Regulations mapped : NDPA 2023, Ghana DPA 2012, Kenya DPA 2019,
                     Rwanda Law 058/2021, Loi 2013-450, Loi 2017-20, Egypt PDPL 2020

When implemented this adapter will check:
  - Storage Account encryption and HTTPS-only traffic
  - Azure SQL transparent data encryption
  - Azure Monitor / Diagnostic Settings enabled
  - Data residency (South Africa North preferred)
  - RBAC over-permissive role assignments
"""
from cli.core.base_api_scanner import BaseAPIScanner

_NOT_IMPLEMENTED = (
    "Azure Live API scanner is not yet implemented. "
    "Track progress: https://github.com/Kijiji-Guard/kijiji-guard/issues"
)


class AzureAdapter(BaseAPIScanner):

    def authenticate(self, credentials: dict) -> bool:
        return False

    def scan(self, country: str) -> list[dict]:
        return [{
            "check_id":    "AZ_STUB",
            "check_name":  "Azure Live API Scanner (not yet implemented)",
            "result":      "WARN",
            "resource":    "azure/subscription",
            "file_path":   "azure/subscription",
            "regulation":  "N/A",
            "remediation": _NOT_IMPLEMENTED,
        }]
