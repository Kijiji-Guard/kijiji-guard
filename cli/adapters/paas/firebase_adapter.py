"""
Firebase PaaS Adapter — scans Firebase projects for compliance (stub).

Credentials needed : FIREBASE_SERVICE_ACCOUNT (path to firebase-adminsdk JSON)
How to obtain      : https://console.firebase.google.com/project/_/settings/serviceaccounts/adminsdk
Regulations mapped : NDPA 2023, Ghana DPA 2012, Kenya DPA 2019,
                     Rwanda Law 058/2021, Loi 2013-450, Loi 2017-20, Egypt PDPL 2020

When implemented this adapter will check:
  - Firestore security rules (no open read/write)
  - Firebase Auth email verification enabled
  - Firebase Storage rules not public
  - App Check enabled to prevent abuse
  - Data residency (no Africa region — flag as INFO for all countries)
"""
from cli.core.base_paas_scanner import BasePaaSScanner

_NOT_IMPLEMENTED = (
    "Firebase PaaS scanner is not yet implemented. "
    "Track progress: https://github.com/Kijiji-Guard/kijiji-guard/issues"
)


class FirebaseAdapter(BasePaaSScanner):

    def authenticate(self, credentials: dict) -> bool:
        return False

    def get_config(self) -> dict:
        return {}

    def scan(self, country: str) -> list[dict]:
        return [{
            "check_id":    "FB_STUB",
            "check_name":  "Firebase PaaS Scanner (not yet implemented)",
            "result":      "WARN",
            "resource":    "firebase/project",
            "file_path":   "firebase/project",
            "regulation":  "N/A",
            "remediation": _NOT_IMPLEMENTED,
        }]
