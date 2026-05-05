from abc import ABC, abstractmethod


class BaseAPIScanner(ABC):

    @abstractmethod
    def authenticate(self, credentials: dict) -> bool:
        """Authenticate with the cloud provider. Return True if successful."""

    @abstractmethod
    def scan(self, country: str) -> list[dict]:
        """
        Scan live cloud account for compliance.
        Returns same findings dict format as BaseIaCScanner.
        """
