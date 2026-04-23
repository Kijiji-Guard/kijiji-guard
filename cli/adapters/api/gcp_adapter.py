"""
GCP Live API Adapter — scans live GCP projects for compliance (stub).

Credentials needed : GOOGLE_APPLICATION_CREDENTIALS (path to service account JSON)
How to obtain      : https://console.cloud.google.com/iam-admin/serviceaccounts
Regulations mapped : NDPA 2023, Ghana DPA 2012, Kenya DPA 2019,
                     Rwanda Law 058/2021, Loi 2013-450, Loi 2017-20, Egypt PDPL 2020

When implemented this adapter will check:
  - GCS bucket encryption and public access
  - Cloud SQL encryption at rest
  - Cloud Audit Logs enabled
  - Data residency (africa-south1 preferred)
  - IAM over-permissive bindings
"""
from cli.core.base_api_scanner import BaseAPIScanner

_NOT_IMPLEMENTED = (
    "GCP Live API scanner is not yet implemented. "
    "Track progress: https://github.com/Kijiji-Guard/kijiji-guard/issues"
)


class GCPAdapter(BaseAPIScanner):

    def authenticate(self, credentials: dict) -> bool:
        return False

    def scan(self, country: str) -> list[dict]:
        return [{
            "check_id":    "GCP_STUB",
            "check_name":  "GCP Live API Scanner (not yet implemented)",
            "result":      "WARN",
            "resource":    "gcp/project",
            "file_path":   "gcp/project",
            "regulation":  "N/A",
            "remediation": _NOT_IMPLEMENTED,
        }]
