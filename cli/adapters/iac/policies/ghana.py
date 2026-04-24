"""Ghana Data Protection Act 2012 (Act 843) policies — 5 checks."""
from .base_policy import BasePolicy

AFRICAN_REGIONS = ("af-south-1", "af-")


class GhanaPolicies(BasePolicy):
    country    = "ghana"
    regulation = "Ghana Data Protection Act 2012 (Act 843)"

    # ------------------------------------------------------------------
    def check_gha_001_encryption(self):
        """CKV_GHA_001 — Encryption at Rest (DPA 2012, Section 22)."""
        for name, config in self.get_resources("aws_s3_bucket"):
            res = f"aws_s3_bucket.{name}"
            if (
                "server_side_encryption_configuration" in config
                or "server_side_encryption" in config
            ):
                self.passed("CKV_GHA_001", "S3 encryption at rest enabled", res)
            else:
                self.failed(
                    "CKV_GHA_001", "S3 encryption at rest not configured", res,
                    remediation="Enable server_side_encryption_configuration. "
                                "Ghana DPA 2012, Section 22.",
                )

        for name, config in self.get_resources("aws_db_instance"):
            res = f"aws_db_instance.{name}"
            if config.get("storage_encrypted") is True:
                self.passed("CKV_GHA_001", "RDS encryption at rest enabled", res)
            else:
                self.failed(
                    "CKV_GHA_001", "RDS encryption at rest disabled", res,
                    remediation="Set storage_encrypted = true. Ghana DPA 2012, Section 22.",
                )

    # ------------------------------------------------------------------
    def check_gha_002_iam_no_wildcard(self):
        """CKV_GHA_002 — No wildcard IAM actions (DPA 2012, Section 20)."""
        for rtype in ("aws_iam_role_policy", "aws_iam_policy"):
            for name, config in self.get_resources(rtype):
                res    = f"{rtype}.{name}"
                policy = str(config.get("policy", ""))
                if '"*"' in policy or "'*'" in policy or "Action: '*'" in policy:
                    self.failed(
                        "CKV_GHA_002", "IAM policy uses wildcard actions", res,
                        remediation="Replace Action: '*' with least-privilege permissions. "
                                    "Ghana DPA 2012, Section 20 requires access controls.",
                    )
                else:
                    self.passed("CKV_GHA_002", "IAM policy has no wildcard actions", res)

    # ------------------------------------------------------------------
    def check_gha_003_public_access(self):
        """CKV_GHA_003 — Block S3 Public Access (DPA 2012, Section 22)."""
        for name, config in self.get_resources("aws_s3_bucket"):
            res = f"aws_s3_bucket.{name}"
            bpa = config.get("block_public_acls") or config.get("block_public_access")
            if bpa is True or str(bpa).lower() == "true":
                self.passed("CKV_GHA_003", "S3 public access blocked", res)
            else:
                self.failed(
                    "CKV_GHA_003", "S3 bucket may allow public access", res,
                    remediation="Set block_public_acls = true. Ghana DPA 2012, Section 22.",
                )

        for name, _ in self.get_resources("aws_s3_bucket_public_access_block"):
            self.passed(
                "CKV_GHA_003", "S3 public access block resource exists",
                f"aws_s3_bucket_public_access_block.{name}",
            )

    # ------------------------------------------------------------------
    def check_gha_004_audit_logging(self):
        """CKV_GHA_004 — Audit logging via CloudTrail (DPA 2012, Section 34)."""
        trails = self.get_resources("aws_cloudtrail")
        if not trails:
            self.failed(
                "CKV_GHA_004", "No CloudTrail configured", "aws_cloudtrail",
                remediation="Create aws_cloudtrail to enable audit logging. "
                            "Ghana DPA 2012, Section 34.",
            )
        else:
            for name, config in trails:
                res = f"aws_cloudtrail.{name}"
                if config.get("enable_log_file_validation") is True:
                    self.passed("CKV_GHA_004", "CloudTrail with log validation enabled", res)
                else:
                    self.warned(
                        "CKV_GHA_004", "CloudTrail exists but log validation not enabled", res,
                        remediation="Set enable_log_file_validation = true. "
                                    "Ghana DPA 2012, Section 34.",
                    )

    # ------------------------------------------------------------------
    def check_gha_005_https(self):
        """CKV_GHA_005 — HTTPS enforcement on load balancers (DPA 2012, Section 22)."""
        for rtype in ("aws_lb_listener", "aws_alb_listener"):
            for name, config in self.get_resources(rtype):
                res      = f"{rtype}.{name}"
                protocol = self._str(config, "protocol").upper()
                if protocol in ("HTTPS", "TLS", "SSL"):
                    self.passed("CKV_GHA_005", "Load balancer listener uses HTTPS/TLS", res)
                elif protocol == "HTTP":
                    self.failed(
                        "CKV_GHA_005", "Load balancer listener uses plain HTTP", res,
                        remediation="Change protocol to HTTPS. Ghana DPA 2012, Section 22 "
                                    "requires data in transit to be encrypted.",
                    )
                else:
                    self.warned(
                        "CKV_GHA_005", "Load balancer listener protocol not verified", res,
                        remediation="Confirm protocol is HTTPS or TLS.",
                    )
