from abc import ABC, abstractmethod


class BasePaaSScanner(ABC):

    @abstractmethod
    def authenticate(self, credentials: dict) -> bool:
        """Authenticate with the PaaS provider."""

    @abstractmethod
    def scan(self, country: str) -> list[dict]:
        """
        Scan PaaS project config and API for compliance.
        Returns same findings dict format as BaseIaCScanner.
        """

    @abstractmethod
    def get_config(self) -> dict:
        """
        Fetch the current project config from the PaaS provider API.
        Returns raw config dict.
        """
