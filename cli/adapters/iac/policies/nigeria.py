"""Nigeria NDPA 2023 policies — 5 checks."""
from .base_policy import BasePolicy

AFRICAN_REGIONS = ("af-south-1", "af-")


class NigeriaPolicies(BasePolicy):
    country    = "nigeria"
    regulation = "NDPA 2023"

    # ------------------------------------------------------------------
    def check_ngr_001_data_residency(self):
        """CKV_NGR_001 — Data Residency (NDPA Section 41)."""
        for rtype in ("aws_s3_bucket", "aws_db_instance", "aws_instance"):
            for name, config in self.get_resources(rtype):
                region = self._resolve_region(config)
                res    = f"{rtype}.{name}"
                if not region:
                    self.warned(
                        "CKV_NGR_001", "Data residency — region not specified", res,
                        remediation="Set region = 'af-south-1' to keep data in Africa "
                                    "(NDPA 2023, Section 41).",
                    )
                elif any(r in region for r in AFRICAN_REGIONS):
                    self.passed("CKV_NGR_001", "Data residency — African region", res)
                else:
                    self.failed(
                        "CKV_NGR_001", "Data residency — non-African region", res,
                        remediation=f"Region '{region}' is outside Africa. "
                                    "Change to 'af-south-1'. NDPA 2023, Section 41.",
                    )

    # ------------------------------------------------------------------
    def check_ngr_002_retention(self):
        """CKV_NGR_002 — Data Retention Policy (NDPA Section 24)."""
        for name, config in self.get_resources("aws_s3_bucket"):
            has_lc = (
                "lifecycle_rule" in config
                or "lifecycle_configuration" in config
            )
            res = f"aws_s3_bucket.{name}"
            if has_lc:
                self.passed("CKV_NGR_002", "Data retention policy configured", res)
            else:
                self.failed(
                    "CKV_NGR_002", "No data retention lifecycle rule", res,
                    remediation="Add a lifecycle_rule with expiration to S3 bucket. "
                                "NDPA 2023, Section 24 prohibits indefinite PII storage.",
                )

    # ------------------------------------------------------------------
    def check_ngr_003_encryption(self):
        """CKV_NGR_003 — Encryption at Rest (NDPA Section 34)."""
        for name, config in self.get_resources("aws_s3_bucket"):
            sse = (
                "server_side_encryption_configuration" in config
                or "server_side_encryption" in config
            )
            res = f"aws_s3_bucket.{name}"
            if sse:
                self.passed("CKV_NGR_003", "S3 encryption at rest enabled", res)
            else:
                self.failed(
                    "CKV_NGR_003", "S3 encryption at rest not configured", res,
                    remediation="Enable server_side_encryption_configuration with "
                                "AES256 or aws:kms. NDPA 2023, Section 34.",
                )

        for name, config in self.get_resources("aws_db_instance"):
            res = f"aws_db_instance.{name}"
            if config.get("storage_encrypted") is True:
                self.passed("CKV_NGR_003", "RDS encryption at rest enabled", res)
            else:
                self.failed(
                    "CKV_NGR_003", "RDS encryption at rest disabled", res,
                    remediation="Set storage_encrypted = true. NDPA 2023, Section 34.",
                )

        for name, config in self.get_resources("aws_ebs_volume"):
            res = f"aws_ebs_volume.{name}"
            if config.get("encrypted") is True:
                self.passed("CKV_NGR_003", "EBS volume encryption enabled", res)
            else:
                self.failed(
                    "CKV_NGR_003", "EBS volume not encrypted", res,
                    remediation="Set encrypted = true on aws_ebs_volume. NDPA 2023, Section 34.",
                )

    # ------------------------------------------------------------------
    def check_ngr_004_breach_monitoring(self):
        """CKV_NGR_004 — Breach Notification Readiness (NDPA Section 40)."""
        trails = self.get_resources("aws_cloudtrail")
        if not trails:
            self.failed(
                "CKV_NGR_004", "No CloudTrail — breach detection impossible",
                "aws_cloudtrail",
                remediation="Create aws_cloudtrail with enable_log_file_validation = true. "
                            "NDPA Section 40 requires 72-hour breach notification.",
            )
        else:
            for name, config in trails:
                res = f"aws_cloudtrail.{name}"
                if config.get("enable_logging", True) is not False:
                    self.passed("CKV_NGR_004", "CloudTrail enabled for breach detection", res)
                else:
                    self.failed(
                        "CKV_NGR_004", "CloudTrail logging disabled", res,
                        remediation="Set enable_logging = true. NDPA 2023, Section 40.",
                    )

    # ------------------------------------------------------------------
    def check_ngr_005_public_access(self):
        """CKV_NGR_005 — Block S3 Public Access (NDPA Sections 41-43)."""
        for name, config in self.get_resources("aws_s3_bucket"):
            res = f"aws_s3_bucket.{name}"
            bpa = config.get("block_public_acls") or config.get("block_public_access")
            if bpa is True or str(bpa).lower() == "true":
                self.passed("CKV_NGR_005", "S3 public access blocked", res)
            else:
                self.failed(
                    "CKV_NGR_005", "S3 bucket may allow public access", res,
                    remediation="Set block_public_acls = true and block_public_policy = true "
                                "or use aws_s3_bucket_public_access_block. "
                                "NDPA 2023, Sections 41-43.",
                )

        for name, config in self.get_resources("aws_s3_bucket_public_access_block"):
            res = f"aws_s3_bucket_public_access_block.{name}"
            if config.get("block_public_acls") is True:
                self.passed("CKV_NGR_005", "S3 public access block configured", res)
            else:
                self.failed(
                    "CKV_NGR_005", "S3 public access block incomplete", res,
                    remediation="Set block_public_acls = true and block_public_policy = true.",
                )
