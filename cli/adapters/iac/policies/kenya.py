"""Kenya Data Protection Act 2019 policies — 6 checks."""
from .base_policy import BasePolicy

AFRICAN_REGIONS = ("af-south-1", "af-")


class KenyaPolicies(BasePolicy):
    country    = "kenya"
    regulation = "Kenya Data Protection Act 2019"

    # ------------------------------------------------------------------
    def check_ken_001_encryption(self):
        """CKV_KEN_001 — Encryption at Rest (KE DPA 2019, Section 41)."""
        for name, config in self.get_resources("aws_s3_bucket"):
            res = f"aws_s3_bucket.{name}"
            if (
                "server_side_encryption_configuration" in config
                or "server_side_encryption" in config
            ):
                self.passed("CKV_KEN_001", "S3 encryption at rest enabled", res)
            else:
                self.failed(
                    "CKV_KEN_001", "S3 encryption at rest not configured", res,
                    remediation="Enable server_side_encryption_configuration. "
                                "Kenya DPA 2019, Section 41.",
                )

        for name, config in self.get_resources("aws_db_instance"):
            res = f"aws_db_instance.{name}"
            if config.get("storage_encrypted") is True:
                self.passed("CKV_KEN_001", "RDS encryption at rest enabled", res)
            else:
                self.failed(
                    "CKV_KEN_001", "RDS encryption at rest disabled", res,
                    remediation="Set storage_encrypted = true. Kenya DPA 2019, Section 41.",
                )

    # ------------------------------------------------------------------
    def check_ken_002_breach_monitoring(self):
        """CKV_KEN_002 — Breach detection via CloudWatch (KE DPA 2019, Section 43)."""
        alarms = self.get_resources("aws_cloudwatch_metric_alarm")
        groups = self.get_resources("aws_cloudwatch_log_group")
        if alarms or groups:
            for name, _ in alarms:
                self.passed(
                    "CKV_KEN_002", "CloudWatch alarm configured",
                    f"aws_cloudwatch_metric_alarm.{name}",
                )
            for name, _ in groups:
                self.passed(
                    "CKV_KEN_002", "CloudWatch log group configured",
                    f"aws_cloudwatch_log_group.{name}",
                )
        else:
            self.failed(
                "CKV_KEN_002", "No CloudWatch monitoring configured",
                "aws_cloudwatch",
                remediation="Create aws_cloudwatch_log_group and aws_cloudwatch_metric_alarm "
                            "for breach detection. Kenya DPA 2019, Section 43.",
            )

    # ------------------------------------------------------------------
    def check_ken_003_data_localisation(self):
        """CKV_KEN_003 — Data localisation preference (KE DPA 2019, Section 48)."""
        for rtype in ("aws_s3_bucket", "aws_db_instance", "aws_instance"):
            for name, config in self.get_resources(rtype):
                region = self._resolve_region(config)
                res    = f"{rtype}.{name}"
                if not region:
                    self.warned(
                        "CKV_KEN_003", "Data localisation — region undetermined", res,
                        remediation="Set region = 'af-south-1'. "
                                    "Kenya DPA 2019, Section 48 prefers local storage.",
                    )
                elif any(r in region for r in AFRICAN_REGIONS):
                    self.passed("CKV_KEN_003", "Data in African region", res)
                else:
                    self.warned(
                        "CKV_KEN_003", "Data outside Africa", res,
                        remediation=f"Region '{region}' is outside Africa. Consider af-south-1. "
                                    "Kenya DPA 2019, Section 48.",
                    )

    # ------------------------------------------------------------------
    def check_ken_004_access_controls(self):
        """CKV_KEN_004 — IAM least-privilege (KE DPA 2019, Section 41)."""
        for rtype in ("aws_iam_role_policy", "aws_iam_policy"):
            for name, config in self.get_resources(rtype):
                res    = f"{rtype}.{name}"
                policy = config.get("policy", "")
                if self._has_wildcard_action(policy):
                    self.failed(
                        "CKV_KEN_004", "IAM policy uses wildcard actions", res,
                        remediation="Replace Action: '*' with specific permissions. "
                                    "Kenya DPA 2019, Section 41.",
                    )
                else:
                    self.passed("CKV_KEN_004", "IAM policy uses specific actions", res)

    # ------------------------------------------------------------------
    def check_ken_005_audit_trail(self):
        """CKV_KEN_005 — CloudTrail audit trail (KE DPA 2019, Section 43)."""
        trails = self.get_resources("aws_cloudtrail")
        if not trails:
            self.failed(
                "CKV_KEN_005", "No CloudTrail audit trail", "aws_cloudtrail",
                remediation="Create aws_cloudtrail. Kenya DPA 2019, Section 43.",
            )
        else:
            for name, config in trails:
                res = f"aws_cloudtrail.{name}"
                if config.get("enable_log_file_validation") is True:
                    self.passed("CKV_KEN_005", "CloudTrail with log validation", res)
                else:
                    self.warned(
                        "CKV_KEN_005", "CloudTrail without log validation", res,
                        remediation="Set enable_log_file_validation = true. "
                                    "Kenya DPA 2019, Section 43.",
                    )

    # ------------------------------------------------------------------
    def check_ken_006_encryption_transit(self):
        """CKV_KEN_006 — HTTPS on load balancers (KE DPA 2019, Section 41)."""
        found_any = False
        for rtype in ("aws_lb_listener", "aws_alb_listener"):
            for name, config in self.get_resources(rtype):
                found_any = True
                res      = f"{rtype}.{name}"
                protocol = self._str(config, "protocol").upper()
                if protocol in ("HTTPS", "TLS", "SSL"):
                    self.passed("CKV_KEN_006", "Load balancer listener uses HTTPS/TLS", res)
                elif protocol == "HTTP":
                    self.failed(
                        "CKV_KEN_006", "Load balancer listener uses plain HTTP", res,
                        remediation="Set protocol = 'HTTPS'. Kenya DPA 2019, Section 41.",
                    )
