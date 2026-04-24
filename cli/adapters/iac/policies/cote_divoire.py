"""Côte d'Ivoire Loi n°2013-450 policies — 5 checks."""
from .base_policy import BasePolicy


class CoteDivoirePolicies(BasePolicy):
    country    = "cote-divoire"
    regulation = "Loi n°2013-450 (Côte d'Ivoire)"

    # ------------------------------------------------------------------
    def check_civ_001_encryption(self):
        """CKV_CIV_001 — Encryption at Rest (Art. 36)."""
        for name, config in self.get_resources("aws_s3_bucket"):
            res = f"aws_s3_bucket.{name}"
            if (
                "server_side_encryption_configuration" in config
                or "server_side_encryption" in config
            ):
                self.passed("CKV_CIV_001", "S3 encryption at rest enabled", res)
            else:
                self.failed(
                    "CKV_CIV_001", "S3 encryption at rest not configured", res,
                    remediation="Enable server_side_encryption_configuration. "
                                "Loi n°2013-450, Article 36.",
                )

        for name, config in self.get_resources("aws_db_instance"):
            res = f"aws_db_instance.{name}"
            if config.get("storage_encrypted") is True:
                self.passed("CKV_CIV_001", "RDS encryption at rest enabled", res)
            else:
                self.failed(
                    "CKV_CIV_001", "RDS encryption at rest disabled", res,
                    remediation="Set storage_encrypted = true. Loi n°2013-450, Art. 36.",
                )

    # ------------------------------------------------------------------
    def check_civ_002_access_control(self):
        """CKV_CIV_002 — Access control / IAM (Art. 26)."""
        for rtype in ("aws_iam_role_policy", "aws_iam_policy"):
            for name, config in self.get_resources(rtype):
                res    = f"{rtype}.{name}"
                policy = str(config.get("policy", ""))
                if '"*"' in policy or "'*'" in policy:
                    self.failed(
                        "CKV_CIV_002", "IAM policy uses wildcard actions", res,
                        remediation="Apply least-privilege IAM. Loi n°2013-450, Article 26.",
                    )
                else:
                    self.passed("CKV_CIV_002", "IAM policy uses specific actions", res)

    # ------------------------------------------------------------------
    def check_civ_003_public_access(self):
        """CKV_CIV_003 — Block S3 public access (Art. 36)."""
        for name, config in self.get_resources("aws_s3_bucket"):
            res = f"aws_s3_bucket.{name}"
            bpa = config.get("block_public_acls") or config.get("block_public_access")
            if bpa is True or str(bpa).lower() == "true":
                self.passed("CKV_CIV_003", "S3 public access blocked", res)
            else:
                self.failed(
                    "CKV_CIV_003", "S3 bucket may allow public access", res,
                    remediation="Set block_public_acls = true. Loi n°2013-450, Article 36.",
                )

    # ------------------------------------------------------------------
    def check_civ_004_https(self):
        """CKV_CIV_004 — HTTPS enforcement (Art. 36)."""
        for rtype in ("aws_lb_listener", "aws_alb_listener"):
            for name, config in self.get_resources(rtype):
                res      = f"{rtype}.{name}"
                protocol = self._str(config, "protocol").upper()
                if protocol in ("HTTPS", "TLS", "SSL"):
                    self.passed("CKV_CIV_004", "Load balancer uses HTTPS/TLS", res)
                elif protocol == "HTTP":
                    self.failed(
                        "CKV_CIV_004", "Load balancer uses plain HTTP", res,
                        remediation="Set protocol = 'HTTPS'. Loi n°2013-450, Article 36.",
                    )

    # ------------------------------------------------------------------
    def check_civ_005_audit_logging(self):
        """CKV_CIV_005 — Audit logging (Art. 29)."""
        trails = self.get_resources("aws_cloudtrail")
        if not trails:
            self.failed(
                "CKV_CIV_005", "No CloudTrail audit logging", "aws_cloudtrail",
                remediation="Create aws_cloudtrail. Loi n°2013-450, Article 29.",
            )
        else:
            for name, config in trails:
                res = f"aws_cloudtrail.{name}"
                if config.get("enable_log_file_validation") is True:
                    self.passed("CKV_CIV_005", "CloudTrail with log validation", res)
                else:
                    self.warned(
                        "CKV_CIV_005", "CloudTrail without log validation", res,
                        remediation="Set enable_log_file_validation = true. "
                                    "Loi n°2013-450, Article 29.",
                    )
