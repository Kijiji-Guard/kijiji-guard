from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

class CoteDIvoireEncryptionAtRestCheck(BaseResourceCheck):
    def __init__(self):
        # Côte d'Ivoire Loi n°2013-450 du 19 juin 2013 relative à la protection
        # des données à caractère personnel, Article 36: Sécurité des données.
        # Requires appropriate technical measures to protect personal data including encryption.
        name = "Mandate AES256 or KMS for all storage resources (Loi n°2013-450, Article 36)"
        id = "CKV_CIV_001"
        supported_resources = ['aws_s3_bucket', 'aws_db_instance']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        # Check S3 encryption
        if self.entity_type == 'aws_s3_bucket':
            if 'server_side_encryption_configuration' in conf:
                rules = conf['server_side_encryption_configuration'][0]['rule']
                for rule in rules:
                    if 'apply_server_side_encryption_by_default' in rule:
                        encryption = rule['apply_server_side_encryption_by_default'][0]['sse_algorithm']
                        if encryption in ['AES256', 'aws:kms']:
                            return CheckResult.PASSED
            return CheckResult.FAILED

        # Check RDS encryption
        if self.entity_type == 'aws_db_instance':
            if 'storage_encrypted' in conf and conf['storage_encrypted'][0] == True:
                return CheckResult.PASSED
            return CheckResult.FAILED

        return CheckResult.FAILED

check = CoteDIvoireEncryptionAtRestCheck()
