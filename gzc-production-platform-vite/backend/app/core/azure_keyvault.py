"""
Azure Key Vault integration for secure secret management
"""
import logging
from typing import Optional
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ResourceNotFoundError

logger = logging.getLogger(__name__)


class AzureKeyVaultClient:
    def __init__(self, vault_url: str = "https://gzc-finma-keyvault.vault.azure.net/"):
        """Initialize Azure Key Vault client"""
        self.vault_url = vault_url
        self.credential = DefaultAzureCredential()
        self.client = SecretClient(vault_url=vault_url, credential=self.credential)
        logger.info(f"Initialized Azure Key Vault client for {vault_url}")
    
    def get_secret(self, secret_name: str) -> Optional[str]:
        """Get secret value from Key Vault"""
        try:
            secret = self.client.get_secret(secret_name)
            logger.debug(f"Retrieved secret '{secret_name}' from Key Vault")
            return secret.value
        except ResourceNotFoundError:
            logger.error(f"Secret '{secret_name}' not found in Key Vault")
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve secret '{secret_name}': {e}")
            return None
    
    def set_secret(self, secret_name: str, secret_value: str) -> bool:
        """Set secret value in Key Vault"""
        try:
            self.client.set_secret(secret_name, secret_value)
            logger.info(f"Successfully set secret '{secret_name}' in Key Vault")
            return True
        except Exception as e:
            logger.error(f"Failed to set secret '{secret_name}': {e}")
            return False


# Global Key Vault client instance
keyvault_client = AzureKeyVaultClient()