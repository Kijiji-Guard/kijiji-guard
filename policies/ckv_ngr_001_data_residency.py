from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

class DataResidencyCheck(BaseResourceCheck):
    def __init__(self):
        # NDPA Section 41: Cross-border transfer restrictions.
        # Data must be stored in Nigeria or "Adequate Protection" zones.
        name = "Ensure data residency is compliant with NDPA Section 41 (Africa/Adequate zones)"
        id = "CKV_NGR_001"
        supported_resources = ['aws_s3_bucket', 'aws_db_instance', 'google_storage_bucket', 'azurerm_storage_account']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        # For simplicity in this MVP, we check for 'region' or 'location' tags/attributes.
        # In a real scenario, we'd look at the provider region.
        # We flag any region that isn't 'af-south-1' (AWS Africa) or 'me-central-1' etc.
        
        # Check for AWS region in tags or provider (simulated here via tags for the MVP)
        if 'tags' in conf:
            tags = conf['tags'][0]
            if 'Region' in tags:
                region = tags['Region']
                if region in ['af-south-1', 'eu-west-1']: # eu-west-1 often considered adequate
                    return CheckResult.PASSED
        
        # Also check for explicit 'region' attribute if present in some resources
        if 'region' in conf:
            if conf['region'][0] in ['af-south-1', 'eu-west-1']:
                return CheckResult.PASSED

        return CheckResult.FAILED

check = DataResidencyCheck()
