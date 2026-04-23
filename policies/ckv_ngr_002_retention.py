from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

class RetentionEnforcementCheck(BaseResourceCheck):
    def __init__(self):
        # NDPA Section 24: Storage Limitation Principle.
        # Data must not be kept longer than necessary.
        name = "Ensure S3 buckets have a lifecycle_rule defined (NDPA Section 24)"
        id = "CKV_NGR_002"
        supported_resources = ['aws_s3_bucket']
        categories = [CheckCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'lifecycle_rule' in conf:
            return CheckResult.PASSED
        return CheckResult.FAILED

check = RetentionEnforcementCheck()
