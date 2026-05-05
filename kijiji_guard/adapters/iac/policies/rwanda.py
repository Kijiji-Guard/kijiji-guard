"""Rwanda Law No.058/2021 on Personal Data Protection — 5 checks (strictest localisation)."""
from .base_policy import BasePolicy

AFRICA_ONLY = ("af-south-1",)   # Rwanda requires THIS specific region


class RwandaPolicies(BasePolicy):
    country    = "rwanda"
    regulation = "Rwanda Law No.058/2021 on Personal Data Protection"

    # ------------------------------------------------------------------
    def check_rwa_001_encryption(self):
        """CKV_RWA_001 — Encryption at Rest (Art. 22)."""
        for name, config in self.get_resources("aws_s3_bucket"):
            res = f"aws_s3_bucket.{name}"
            if (
                "server_side_encryption_configuration" in config
                or "server_side_encryption" in config
            ):
                self.passed("CKV_RWA_001", "S3 encryption at rest enabled", res)
            else:
                self.failed(
                    "CKV_RWA_001", "S3 encryption at rest not configured", res,
                    remediation="Enable server_side_encryption_configuration. "
                                "Rwanda Law 058/2021, Article 22.",
                )

        for name, config in self.get_resources("aws_db_instance"):
            res = f"aws_db_instance.{name}"
            if config.get("storage_encrypted") is True:
                self.passed("CKV_RWA_001", "RDS encryption at rest enabled", res)
            else:
                self.failed(
                    "CKV_RWA_001", "RDS encryption at rest disabled", res,
                    remediation="Set storage_encrypted = true. Rwanda Law 058/2021, Art. 22.",
                )

    # ------------------------------------------------------------------
    def check_rwa_002_strict_localisation(self):
        """CKV_RWA_002 — Strict data localisation FAIL if not af-south-1 (Art. 50)."""
        for rtype in ("aws_s3_bucket", "aws_db_instance", "aws_instance"):
            for name, config in self.get_resources(rtype):
                region = self._resolve_region(config)
                res    = f"{rtype}.{name}"
                if region == "af-south-1":
                    self.passed(
                        "CKV_RWA_002", "Strict data localisation — af-south-1 confirmed", res
                    )
                elif region:
                    self.failed(
                        "CKV_RWA_002",
                        f"Strict data localisation — region '{region}' not permitted", res,
                        remediation="Rwanda Law 058/2021, Article 50 requires data stored in "
                                    "af-south-1. Cross-border transfers need explicit DPA approval.",
                    )
                else:
                    self.failed(
                        "CKV_RWA_002", "Strict data localisation — region not specified", res,
                        remediation="Explicitly set region = 'af-south-1'. "
                                    "Rwanda Law 058/2021, Article 50.",
                    )

    # ------------------------------------------------------------------
    def check_rwa_003_breach_monitoring(self):
        """CKV_RWA_003 — Breach notification readiness 48hr rule (Art. 34)."""
        trails = self.get_resources("aws_cloudtrail")
        if not trails:
            self.failed(
                "CKV_RWA_003", "No CloudTrail — breach response impossible",
                "project-level",
                remediation="Rwanda Law 058/2021, Art. 34 requires 48-hour breach "
                            "notification — impossible without audit trail. "
                            "Create aws_cloudtrail immediately.",
            )
        else:
            for name, config in trails:
                res = f"aws_cloudtrail.{name}"
                validated = config.get("enable_log_file_validation") is True
                multi     = config.get("is_multi_region_trail") is True
                if validated and multi:
                    self.passed(
                        "CKV_RWA_003",
                        "CloudTrail with validation + multi-region enabled", res,
                    )
                elif validated:
                    self.passed("CKV_RWA_003", "CloudTrail with log validation", res)
                else:
                    self.warned(
                        "CKV_RWA_003", "CloudTrail exists but hardening needed", res,
                        remediation="Set enable_log_file_validation = true and "
                                    "is_multi_region_trail = true. Rwanda Law 058/2021, Art. 34.",
                    )

    # ------------------------------------------------------------------
    def check_rwa_004_access_controls(self):
        """CKV_RWA_004 — IAM access controls (Art. 22)."""
        for rtype in ("aws_iam_role_policy", "aws_iam_policy"):
            for name, config in self.get_resources(rtype):
                res    = f"{rtype}.{name}"
                policy = config.get("policy", "")
                if self._has_wildcard_action(policy):
                    self.failed(
                        "CKV_RWA_004", "IAM policy uses wildcard actions", res,
                        remediation="Replace '*' actions with least-privilege. "
                                    "Rwanda Law 058/2021, Article 22.",
                    )
                else:
                    self.passed("CKV_RWA_004", "IAM policy has no wildcard actions", res)

    # ------------------------------------------------------------------
    def check_rwa_005_audit_logging(self):
        """CKV_RWA_005 — Audit logging required (Art. 34)."""
        trails = self.get_resources("aws_cloudtrail")
        if not trails:
            self.failed(
                "CKV_RWA_005", "No audit logging configured", "project-level",
                remediation="Create aws_cloudtrail. Rwanda Law 058/2021, Article 34.",
            )
        else:
            for name, _ in trails:
                self.passed(
                    "CKV_RWA_005", "Audit logging configured",
                    f"aws_cloudtrail.{name}",
                )
