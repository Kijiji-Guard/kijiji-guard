"""Egypt Personal Data Protection Law No.151/2020 policies — 6 checks."""
from .base_policy import BasePolicy

AFRICAN_REGIONS  = ("af-south-1", "af-")
ME_REGIONS       = ("me-south-1", "me-")   # Middle East also acceptable


class EgyptPolicies(BasePolicy):
    country    = "egypt"
    regulation = "Egypt PDPL Law No.151/2020"

    # ------------------------------------------------------------------
    def check_egy_001_encryption(self):
        """CKV_EGY_001 — Encryption at Rest (Art. 19)."""
        for name, config in self.get_resources("aws_s3_bucket"):
            res = f"aws_s3_bucket.{name}"
            if (
                "server_side_encryption_configuration" in config
                or "server_side_encryption" in config
            ):
                self.passed("CKV_EGY_001", "S3 encryption at rest enabled", res)
            else:
                self.failed(
                    "CKV_EGY_001", "S3 encryption at rest not configured", res,
                    remediation="Enable server_side_encryption_configuration. "
                                "Egypt PDPL 2020, Article 19.",
                )

        for name, config in self.get_resources("aws_db_instance"):
            res = f"aws_db_instance.{name}"
            if config.get("storage_encrypted") is True:
                self.passed("CKV_EGY_001", "RDS encryption at rest enabled", res)
            else:
                self.failed(
                    "CKV_EGY_001", "RDS encryption at rest disabled", res,
                    remediation="Set storage_encrypted = true. Egypt PDPL 2020, Art. 19.",
                )

    # ------------------------------------------------------------------
    def check_egy_002_breach_monitoring(self):
        """CKV_EGY_002 — Breach detection for 72-hour notification (Art. 23)."""
        trails = self.get_resources("aws_cloudtrail")
        if not trails:
            self.failed(
                "CKV_EGY_002", "No CloudTrail — 72hr breach notification impossible",
                "aws_cloudtrail",
                remediation="Egypt PDPL 2020, Art. 23 requires breach notification within "
                            "72 hours. Create aws_cloudtrail with log validation.",
            )
        else:
            for name, config in trails:
                res = f"aws_cloudtrail.{name}"
                if config.get("enable_log_file_validation") is True:
                    self.passed("CKV_EGY_002", "CloudTrail with log validation for breach detection", res)
                else:
                    self.warned(
                        "CKV_EGY_002", "CloudTrail exists but log validation disabled", res,
                        remediation="Set enable_log_file_validation = true. "
                                    "Egypt PDPL 2020, Article 23.",
                    )

    # ------------------------------------------------------------------
    def check_egy_003_cross_border(self):
        """CKV_EGY_003 — Cross-border transfer controls (Art. 27)."""
        for name, config in self.get_resources("aws_s3_bucket"):
            res = f"aws_s3_bucket.{name}"
            region = self._resolve_region(config)
            all_acceptable = AFRICAN_REGIONS + ME_REGIONS
            if region and any(r in region for r in all_acceptable):
                self.passed(
                    "CKV_EGY_003",
                    "Data in Africa/Middle East — cross-border controls met", res,
                )
            elif region:
                self.failed(
                    "CKV_EGY_003",
                    f"Data in '{region}' — potential cross-border transfer", res,
                    remediation="Egypt PDPL 2020, Art. 27 restricts cross-border data transfers. "
                                "Use af-south-1 or me-south-1 or obtain DPA approval.",
                )
            else:
                self.warned(
                    "CKV_EGY_003", "Cannot verify data region for cross-border check", res,
                    remediation="Specify a region. Egypt PDPL 2020, Article 27.",
                )

    # ------------------------------------------------------------------
    def check_egy_004_access_controls(self):
        """CKV_EGY_004 — IAM access controls (Art. 19)."""
        for rtype in ("aws_iam_role_policy", "aws_iam_policy"):
            for name, config in self.get_resources(rtype):
                res    = f"{rtype}.{name}"
                policy = config.get("policy", "")
                if self._has_wildcard_action(policy):
                    self.failed(
                        "CKV_EGY_004", "IAM policy uses wildcard actions", res,
                        remediation="Apply least-privilege IAM. Egypt PDPL 2020, Article 19.",
                    )
                else:
                    self.passed("CKV_EGY_004", "IAM policy uses specific actions", res)

    # ------------------------------------------------------------------
    def check_egy_005_https(self):
        """CKV_EGY_005 — HTTPS enforcement (Art. 19)."""
        for rtype in ("aws_lb_listener", "aws_alb_listener"):
            for name, config in self.get_resources(rtype):
                res      = f"{rtype}.{name}"
                protocol = self._str(config, "protocol").upper()
                if protocol in ("HTTPS", "TLS", "SSL"):
                    self.passed("CKV_EGY_005", "Load balancer uses HTTPS/TLS", res)
                elif protocol == "HTTP":
                    self.failed(
                        "CKV_EGY_005", "Load balancer uses plain HTTP", res,
                        remediation="Set protocol = 'HTTPS'. Egypt PDPL 2020, Article 19.",
                    )

    # ------------------------------------------------------------------
    def check_egy_006_audit_trail(self):
        """CKV_EGY_006 — Audit trail with log validation (Art. 23)."""
        trails = self.get_resources("aws_cloudtrail")
        if not trails:
            self.failed(
                "CKV_EGY_006", "No audit trail configured", "aws_cloudtrail",
                remediation="Create aws_cloudtrail. Egypt PDPL 2020, Article 23.",
            )
        else:
            for name, config in trails:
                res       = f"aws_cloudtrail.{name}"
                validated = config.get("enable_log_file_validation") is True
                if validated:
                    self.passed("CKV_EGY_006", "CloudTrail with log validation enabled", res)
                else:
                    self.failed(
                        "CKV_EGY_006", "CloudTrail log validation not enabled", res,
                        remediation="Set enable_log_file_validation = true. "
                                    "Egypt PDPL 2020, Article 23.",
                    )
