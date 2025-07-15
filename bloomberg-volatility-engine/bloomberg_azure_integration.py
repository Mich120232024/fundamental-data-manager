"""
Bloomberg Terminal Azure Integration Service
Runs on Bloomberg Terminal VM and streams data to Azure services
"""

import blpapi
import json
import logging
import time
from datetime import datetime
from typing import List, Dict, Any
import os
import sys

from azure.identity import DefaultAzureCredential
from azure.cosmos import CosmosClient, exceptions
from azure.eventhub import EventHubProducerClient, EventData
from azure.keyvault.secrets import SecretClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BloombergAzureIntegration:
    """Bloomberg Terminal integration with Azure services"""
    
    def __init__(self):
        """Initialize Bloomberg and Azure connections"""
        logger.info("Initializing Bloomberg Azure Integration Service")
        
        # Azure credential using managed identity
        self.credential = DefaultAzureCredential()
        
        # Key Vault configuration
        self.key_vault_url = "https://bloomberg-kv-1752226585.vault.azure.net/"
        
        # Initialize connections
        self.setup_azure_clients()
        self.bloomberg_session = None
        
    def setup_azure_clients(self):
        """Setup Azure service clients with private endpoints"""
        try:
            # Initialize Key Vault client
            secret_client = SecretClient(
                vault_url=self.key_vault_url, 
                credential=self.credential
            )
            
            # Get connection strings from Key Vault
            # Note: You'll need to add these secrets to Key Vault first
            try:
                cosmos_key = secret_client.get_secret("cosmos-primary-key").value
                eventhub_conn = secret_client.get_secret("eventhub-connection-string").value
            except:
                logger.warning("Secrets not found in Key Vault, using environment variables")
                cosmos_key = os.environ.get("COSMOS_KEY", "")
                eventhub_conn = os.environ.get("EVENTHUB_CONNECTION", "")
            
            # Cosmos DB client (using private endpoint)
            cosmos_endpoint = "https://cosmos-research-analytics-prod.documents.azure.com:443/"
            self.cosmos_client = CosmosClient(cosmos_endpoint, cosmos_key)
            self.database = self.cosmos_client.get_database_client("bloomberg-data")
            self.container = self.database.get_container_client("market-data")
            
            # Event Hub client (using private endpoint)
            self.event_hub_producer = EventHubProducerClient.from_connection_string(
                eventhub_conn,
                eventhub_name="bloomberg-stream"
            )
            
            logger.info("Azure clients initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup Azure clients: {e}")
            raise
    
    def init_bloomberg_session(self):
        """Initialize Bloomberg API session"""
        try:
            sessionOptions = blpapi.SessionOptions()
            sessionOptions.setServerHost("localhost")
            sessionOptions.setServerPort(8194)
            
            logger.info("Creating Bloomberg session...")
            self.bloomberg_session = blpapi.Session(sessionOptions)
            
            if not self.bloomberg_session.start():
                raise Exception("Failed to start Bloomberg session")
            
            if not self.bloomberg_session.openService("//blp/refdata"):
                raise Exception("Failed to open reference data service")
            
            logger.info("Bloomberg session initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Bloomberg session initialization failed: {e}")
            return False
    
    def get_reference_data(self, securities: List[str], fields: List[str]) -> List[Dict[str, Any]]:
        """Get reference data from Bloomberg"""
        if not self.bloomberg_session:
            if not self.init_bloomberg_session():
                return []
        
        try:
            refDataService = self.bloomberg_session.getService("//blp/refdata")
            request = refDataService.createRequest("ReferenceDataRequest")
            
            # Add securities
            for security in securities:
                request.getElement("securities").appendValue(security)
            
            # Add fields
            for field in fields:
                request.getElement("fields").appendValue(field)
            
            # Send request
            logger.info(f"Requesting data for {securities} with fields {fields}")
            self.bloomberg_session.sendRequest(request)
            
            # Process response
            results = []
            while True:
                ev = self.bloomberg_session.nextEvent(500)
                
                for msg in ev:
                    if msg.hasElement("responseError"):
                        logger.error(f"Response error: {msg.getElement('responseError')}")
                        continue
                    
                    if msg.hasElement("securityData"):
                        securityData = msg.getElement("securityData")
                        numSecurities = securityData.numValues()
                        
                        for i in range(numSecurities):
                            security = securityData.getValue(i)
                            securityName = security.getElementAsString("security")
                            
                            if security.hasElement("fieldData"):
                                fieldData = security.getElement("fieldData")
                                data = {
                                    "id": f"{securityName}_{datetime.utcnow().isoformat()}",
                                    "security": securityName,
                                    "timestamp": datetime.utcnow().isoformat(),
                                    "source": "Bloomberg Terminal",
                                    "data": {}
                                }
                                
                                # Extract field values
                                for field in fields:
                                    if fieldData.hasElement(field):
                                        data["data"][field] = fieldData.getElementAsString(field)
                                
                                results.append(data)
                
                if ev.eventType() == blpapi.Event.RESPONSE:
                    break
            
            logger.info(f"Retrieved {len(results)} data points")
            return results
            
        except Exception as e:
            logger.error(f"Failed to get reference data: {e}")
            return []
    
    def send_to_cosmos(self, data: List[Dict[str, Any]]):
        """Send data to Cosmos DB"""
        try:
            for item in data:
                self.container.upsert_item(item)
            logger.info(f"Sent {len(data)} items to Cosmos DB")
        except Exception as e:
            logger.error(f"Failed to send to Cosmos DB: {e}")
    
    def send_to_event_hub(self, data: List[Dict[str, Any]]):
        """Send data to Event Hub"""
        try:
            batch = self.event_hub_producer.create_batch()
            
            for item in data:
                event_data = EventData(json.dumps(item))
                batch.add(event_data)
            
            self.event_hub_producer.send_batch(batch)
            logger.info(f"Sent {len(data)} events to Event Hub")
            
        except Exception as e:
            logger.error(f"Failed to send to Event Hub: {e}")
    
    def run_continuous_update(self, securities: List[str], fields: List[str], interval: int = 60):
        """Continuously fetch and stream Bloomberg data"""
        logger.info(f"Starting continuous update with {interval}s interval")
        
        while True:
            try:
                # Get data from Bloomberg
                data = self.get_reference_data(securities, fields)
                
                if data:
                    # Send to Azure services
                    self.send_to_cosmos(data)
                    self.send_to_event_hub(data)
                else:
                    logger.warning("No data retrieved from Bloomberg")
                
                # Wait for next update
                time.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("Stopping continuous update...")
                break
            except Exception as e:
                logger.error(f"Error in continuous update: {e}")
                time.sleep(interval)
    
    def close(self):
        """Clean up connections"""
        if self.bloomberg_session:
            self.bloomberg_session.stop()
        self.event_hub_producer.close()
        logger.info("Connections closed")


def main():
    """Main entry point"""
    # Example securities and fields
    securities = [
        "EURUSD Curncy",
        "GBPUSD Curncy", 
        "USDJPY Curncy",
        "AUDUSD Curncy"
    ]
    
    fields = [
        "PX_LAST",
        "PX_BID", 
        "PX_ASK",
        "PX_VOLUME",
        "LAST_UPDATE_DT"
    ]
    
    # Create integration service
    service = BloombergAzureIntegration()
    
    try:
        # Run continuous updates
        service.run_continuous_update(securities, fields, interval=60)
    finally:
        service.close()


if __name__ == "__main__":
    main()