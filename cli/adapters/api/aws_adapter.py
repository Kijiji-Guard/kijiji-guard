"""
AWS Live API Adapter — scans live AWS accounts for compliance (stub).

Credentials needed : AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION
How to obtain      : https://console.aws.amazon.com/iam/home#/security_credentials
Regulations mapped : NDPA 2023, Ghana DPA 2012, Kenya DPA 2019,
                     Rwanda Law 058/2021, Loi 2013-450, Loi 2017-20, Egypt PDPL 2020

When implemented this adapter will check:
  - S3 bucket encryption, public access block, versioning
  - RDS encryption at rest and in transit
  - CloudTrail enabled for audit logging
  - VPC flow logs enabled
  - Data residency (af-south-1 preferred)
"""
from cli.core.base_api_scanner import BaseAPIScanner

_NOT_IMPLEMENTED = (
    "AWS Live API scanner is not yet implemented. "
    "Use IaC scanning (checkov_adapter) against Terraform files for now. "
    "Track progress: https://github.com/Kijiji-Guard/kijiji-guard/issues"
)


class AWSAdapter(BaseAPIScanner):

    def authenticate(self, credentials: dict) -> bool:
        return False

    def scan(self, country: str) -> list[dict]:
        return [{
            "check_id":    "AWS_STUB",
            "check_name":  "AWS Live API Scanner (not yet implemented)",
            "result":      "WARN",
            "resource":    "aws/account",
            "file_path":   "aws/account",
            "regulation":  "N/A",
            "remediation": _NOT_IMPLEMENTED,
        }]
