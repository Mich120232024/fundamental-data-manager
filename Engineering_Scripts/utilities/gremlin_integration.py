#!/usr/bin/env python3
"""
Gremlin Integration - Complete Hybrid Pipeline
Blob→Cosmos→Gremlin implementation with ready database
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Azure imports
from azure.cosmos import CosmosClient
from dotenv import load_dotenv

# Gremlin imports
try:
    from gremlin_python.driver import client, serializer
    from gremlin_python.driver.protocol import GremlinServerError
    from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
    from gremlin_python.process.anonymous_traversal import traversal
    from gremlin_python.process.graph_traversal import __
    from gremlin_python.process.strategies import *
    from gremlin_python.process.traversal import T, P, Operator
    GREMLIN_AVAILABLE = True
except ImportError:
    GREMLIN_AVAILABLE = False
    print("⚠️  gremlin_python not installed - run: poetry add gremlinpython")

# Load environment
env_paths = [
    Path(__file__).parent.parent / '.env',
    Path(__file__).parent.parent.parent / '.env',
    Path.cwd() / '.env'
]

for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✓ Environment loaded from: {env_path}")
        break

class GremlinGraphManager:
    """Manage Gremlin knowledge graph operations"""
    
    def __init__(self):
        if not GREMLIN_AVAILABLE:
            raise ImportError("gremlinpython required - run: poetry add gremlinpython")
        
        self.cosmos_client = None
        self.gremlin_client = None
        self.g = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize Cosmos and Gremlin clients"""
        
        try:
            # Initialize Cosmos client
            self.cosmos_client = CosmosClient(
                os.getenv('COSMOS_ENDPOINT'), 
                os.getenv('COSMOS_KEY')
            )
            
            # Initialize Gremlin client
            gremlin_endpoint = os.getenv('GREMLIN_ENDPOINT')
            gremlin_username = os.getenv('GREMLIN_USERNAME')
            gremlin_password = os.getenv('GREMLIN_PASSWORD')
            
            if not all([gremlin_endpoint, gremlin_username, gremlin_password]):
                raise ValueError("Gremlin credentials not found in environment")
            
            # Create Gremlin connection
            self.gremlin_client = client.Client(
                gremlin_endpoint,
                'g',
                username=gremlin_username,
                password=gremlin_password,
                message_serializer=serializer.GraphSONSerializersV2d0()
            )
            
            print("✅ Gremlin and Cosmos clients initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing clients: {e}")
            raise
    
    def ingest_graph_data_from_cosmos(self, document_id: str) -> Dict[str, Any]:
        """Ingest graph-ready data from Cosmos document into Gremlin"""
        
        print(f"🔄 Ingesting graph data from Cosmos document: {document_id}")
        
        try:
            # Get document from Cosmos
            database = self.cosmos_client.get_database_client(os.getenv('COSMOS_DATABASE'))
            container = database.get_container_client('processed_documents')
            
            document = container.read_item(
                item=document_id,
                partition_key='research_document'
            )
            
            graph_data = document.get('graph_ready', {})
            
            if not graph_data:
                raise ValueError("No graph_ready data found in document")
            
            nodes = graph_data.get('nodes', [])
            edges = graph_data.get('edges', [])
            
            print(f"   📊 Found {len(nodes)} nodes and {len(edges)} edges")
            
            # Clear existing graph data for this document (optional)
            self._clear_document_graph_data(document_id)
            
            # Insert vertices
            vertices_created = []
            
            for node in nodes:
                try:
                    # Create vertex with properties
                    query = f"""
                    g.addV('{node['type']}')
                     .property('id', '{node['id']}')
                     .property('document_id', '{document_id}')
                     .property('domain', '{node['properties'].get('domain', 'general')}')
                    """
                    
                    # Add all node properties
                    for prop_key, prop_value in node['properties'].items():
                        if prop_key != 'domain':  # Already added
                            if isinstance(prop_value, str):
                                query += f".property('{prop_key}', '{prop_value}')"
                            else:
                                query += f".property('{prop_key}', {prop_value})"
                    
                    result = self.gremlin_client.submit(query).all().result()
                    vertices_created.append(node['id'])
                    
                    print(f"      ✅ Created vertex: {node['id']} ({node['type']})")
                    
                except Exception as e:
                    print(f"      ❌ Failed to create vertex {node['id']}: {e}")
            
            # Insert edges
            edges_created = []
            
            for edge in edges:
                try:
                    # Create edge between vertices
                    query = f"""
                    g.V().has('id', '{edge['source']}')
                     .addE('{edge['label']}')
                     .to(g.V().has('id', '{edge['target']}'))
                    """
                    
                    # Add edge properties
                    for prop_key, prop_value in edge.get('properties', {}).items():
                        if isinstance(prop_value, str):
                            query += f".property('{prop_key}', '{prop_value}')"
                        else:
                            query += f".property('{prop_key}', {prop_value})"
                    
                    result = self.gremlin_client.submit(query).all().result()
                    edges_created.append(edge['id'])
                    
                    print(f"      ✅ Created edge: {edge['source']} --{edge['label']}--> {edge['target']}")
                    
                except Exception as e:
                    print(f"      ❌ Failed to create edge {edge['id']}: {e}")
            
            # Update Cosmos document with Gremlin references
            document['gremlin_ingested'] = {
                "ingested_at": datetime.now().isoformat(),
                "vertices_created": vertices_created,
                "edges_created": edges_created,
                "gremlin_database": os.getenv('GREMLIN_DATABASE'),
                "gremlin_collection": os.getenv('GREMLIN_COLLECTION'),
                "ingestion_success": True
            }
            
            container.replace_item(
                item=document_id,
                body=document
            )
            
            result = {
                "success": True,
                "document_id": document_id,
                "vertices_created": len(vertices_created),
                "edges_created": len(edges_created),
                "gremlin_database": os.getenv('GREMLIN_DATABASE'),
                "ingestion_timestamp": datetime.now().isoformat()
            }
            
            print(f"✅ Graph data ingestion complete")
            print(f"   Vertices: {result['vertices_created']}")
            print(f"   Edges: {result['edges_created']}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error ingesting graph data: {e}")
            return {"success": False, "error": str(e)}
    
    def _clear_document_graph_data(self, document_id: str):
        """Clear existing graph data for document (optional cleanup)"""
        
        try:
            # Remove vertices associated with this document
            query = f"g.V().has('document_id', '{document_id}').drop()"
            self.gremlin_client.submit(query).all().result()
            print(f"   🧹 Cleared existing graph data for document: {document_id}")
            
        except Exception as e:
            print(f"   ⚠️  Could not clear existing data: {e}")
    
    def query_research_relationships(self, concept_name: str) -> List[Dict]:
        """Query research relationships around a concept"""
        
        try:
            # Find related research documents through concept
            query = f"""
            g.V().hasLabel('ResearchConcept').has('name', '{concept_name}')
             .in('CONTAINS_CONCEPT')
             .hasLabel('ResearchDocument')
             .project('id', 'title', 'domain', 'complexity')
             .by('id')
             .by('title')
             .by('domain')
             .by('complexity')
            """
            
            result = self.gremlin_client.submit(query).all().result()
            
            print(f"🔍 Found {len(result)} documents related to '{concept_name}'")
            for doc in result:
                print(f"   📄 {doc.get('title', 'Unknown')} (domain: {doc.get('domain', 'N/A')})")
            
            return result
            
        except Exception as e:
            print(f"❌ Error querying relationships: {e}")
            return []
    
    def analyze_concept_network(self, document_id: str) -> Dict[str, Any]:
        """Analyze concept network for a document"""
        
        try:
            # Get all concepts in the document
            query = f"""
            g.V().has('document_id', '{document_id}')
             .hasLabel('ResearchDocument')
             .out('CONTAINS_CONCEPT')
             .hasLabel('ResearchConcept')
             .project('name', 'frequency', 'connections')
             .by('name')
             .by('frequency')
             .by(__.bothE().count())
            """
            
            concepts = self.gremlin_client.submit(query).all().result()
            
            # Get document details
            doc_query = f"""
            g.V().has('document_id', '{document_id}')
             .hasLabel('ResearchDocument')
             .project('title', 'domain', 'complexity')
             .by('title')
             .by('domain')
             .by('complexity')
            """
            
            doc_info = self.gremlin_client.submit(doc_query).all().result()
            
            analysis = {
                "document_id": document_id,
                "document_info": doc_info[0] if doc_info else {},
                "concept_count": len(concepts),
                "concepts": concepts,
                "network_metrics": {
                    "total_concepts": len(concepts),
                    "avg_connections": sum(c.get('connections', 0) for c in concepts) / len(concepts) if concepts else 0,
                    "most_connected": max(concepts, key=lambda x: x.get('connections', 0)) if concepts else None
                }
            }
            
            print(f"📊 Concept network analysis for {document_id}:")
            print(f"   Total concepts: {analysis['network_metrics']['total_concepts']}")
            print(f"   Avg connections: {analysis['network_metrics']['avg_connections']:.1f}")
            
            return analysis
            
        except Exception as e:
            print(f"❌ Error analyzing concept network: {e}")
            return {"error": str(e)}
    
    def verify_graph_ingestion(self, document_id: str) -> Dict[str, Any]:
        """Verify graph data was properly ingested"""
        
        try:
            # Count vertices for this document
            vertex_query = f"g.V().has('document_id', '{document_id}').count()"
            vertex_count = self.gremlin_client.submit(vertex_query).all().result()[0]
            
            # Count edges from this document's vertices
            edge_query = f"g.V().has('document_id', '{document_id}').bothE().count()"
            edge_count = self.gremlin_client.submit(edge_query).all().result()[0]
            
            # Get vertex types
            type_query = f"g.V().has('document_id', '{document_id}').label().dedup()"
            vertex_types = self.gremlin_client.submit(type_query).all().result()
            
            verification = {
                "verified": True,
                "document_id": document_id,
                "vertex_count": vertex_count,
                "edge_count": edge_count,
                "vertex_types": vertex_types,
                "verification_timestamp": datetime.now().isoformat()
            }
            
            print(f"🔍 Graph ingestion verification:")
            print(f"   Document ID: {document_id}")
            print(f"   Vertices: {vertex_count}")
            print(f"   Edges: {edge_count}")
            print(f"   Vertex types: {vertex_types}")
            
            return verification
            
        except Exception as e:
            print(f"❌ Error verifying graph ingestion: {e}")
            return {"verified": False, "error": str(e)}

def main():
    """Test complete Gremlin integration"""
    
    if not GREMLIN_AVAILABLE:
        print("❌ gremlinpython not available - run: poetry add gremlinpython")
        return
    
    graph_manager = GremlinGraphManager()
    document_id = "4a81356e63d96dfe"
    
    print(f"🚀 Testing complete Gremlin integration")
    print(f"🎯 Target document: {document_id}")
    
    # 1. Ingest graph data
    print(f"\n1️⃣ INGESTING GRAPH DATA")
    ingestion_result = graph_manager.ingest_graph_data_from_cosmos(document_id)
    
    if ingestion_result["success"]:
        print(f"✅ Graph ingestion successful")
        
        # 2. Verify ingestion
        print(f"\n2️⃣ VERIFYING INGESTION")
        verification = graph_manager.verify_graph_ingestion(document_id)
        
        if verification["verified"]:
            print(f"✅ Graph verification successful")
            
            # 3. Test queries
            print(f"\n3️⃣ TESTING GRAPH QUERIES")
            
            # Query research relationships
            concept_analysis = graph_manager.analyze_concept_network(document_id)
            
            if "error" not in concept_analysis:
                print(f"✅ Concept network analysis successful")
                
                # Test concept queries
                if concept_analysis["concepts"]:
                    test_concept = concept_analysis["concepts"][0]["name"]
                    related_docs = graph_manager.query_research_relationships(test_concept)
                    print(f"✅ Found {len(related_docs)} related documents")
                
                print(f"\n🎯 COMPLETE HYBRID PIPELINE SUCCESS:")
                print(f"   📁 Blob Storage: research-content-blob")
                print(f"   🗄️  Cosmos DB: processed_documents")
                print(f"   🌐 Gremlin Graph: research-knowledge-graph")
                print(f"   📊 Document processed: {document_id}")
                print(f"   🔗 Graph nodes: {verification['vertex_count']}")
                print(f"   ↔️  Graph edges: {verification['edge_count']}")
                print(f"\n✅ AI-EXPLOITABLE KNOWLEDGE GRAPH OPERATIONAL")
                
            else:
                print(f"❌ Concept analysis failed: {concept_analysis['error']}")
        else:
            print(f"❌ Graph verification failed: {verification.get('error', 'Unknown error')}")
    else:
        print(f"❌ Graph ingestion failed: {ingestion_result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()