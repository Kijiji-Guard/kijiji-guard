from abc import ABC, abstractmethod


class BaseIaCScanner(ABC):

    @abstractmethod
    def scan(self, path: str, country: str) -> list[dict]:
        """
        Scan IaC files at path for compliance with country regulations.
        Returns list of findings dicts with keys:
        check_id, check_name, result (PASSED/FAILED), resource,
        file_path, regulation, remediation
        """
