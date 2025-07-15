#!/usr/bin/env python3
"""
Hybrid Storage Pipeline - Blob→Cosmos Implementation
Based on research model from /RESEARCH/analytics/Hybrid_Storage_Content_Mapping_Model.md
"""

import os
import json
import hashlib
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Azure imports
from azure.storage.blob import BlobServiceClient
from azure.cosmos import CosmosClient
from dotenv import load_dotenv

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

@dataclass
class DocumentChunk:
    """Document chunk with metadata"""
    chunk_id: str
    sequence: int
    text: str
    position: int
    total_chunks: int
    semantic_density: float
    has_entities: bool
    metadata: Dict[str, Any]

@dataclass
class ProcessedDocument:
    """Processed document ready for Cosmos storage"""
    id: str
    type: str
    blob_reference: Dict[str, Any]
    content_summary: Dict[str, Any]
    chunks: List[Dict[str, Any]]
    graph_ready: Dict[str, Any]
    ai_metadata: Dict[str, Any]
    processing_timestamp: str

class IntelligentChunker:
    """Intelligent chunking based on research model"""
    
    def __init__(self):
        self.min_size = 256
        self.max_size = 512
        self.overlap = 50
        
    def chunk_document(self, document_text: str, doc_id: str) -> List[DocumentChunk]:
        """Apply semantic chunking strategy"""
        
        # Simple implementation - can be enhanced with NLP
        words = document_text.split()
        chunks = []
        
        current_chunk = []
        current_size = 0
        chunk_index = 0
        
        for word in words:
            current_chunk.append(word)
            current_size += len(word) + 1  # +1 for space
            
            if current_size >= self.max_size:
                # Create chunk
                chunk_text = ' '.join(current_chunk)
                chunk = DocumentChunk(
                    chunk_id=f"{doc_id}_chunk_{chunk_index}",
                    sequence=chunk_index,
                    text=chunk_text,
                    position=chunk_index,
                    total_chunks=0,  # Will be updated later
                    semantic_density=self.calculate_semantic_density(chunk_text),
                    has_entities=self.detect_entities(chunk_text),
                    metadata={
                        "word_count": len(current_chunk),
                        "char_count": len(chunk_text),
                        "chunk_type": "semantic"
                    }
                )
                chunks.append(chunk)
                
                # Overlap handling
                overlap_words = current_chunk[-self.overlap:] if len(current_chunk) > self.overlap else []
                current_chunk = overlap_words
                current_size = sum(len(word) + 1 for word in overlap_words)
                chunk_index += 1
        
        # Handle remaining words
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunk = DocumentChunk(
                chunk_id=f"{doc_id}_chunk_{chunk_index}",
                sequence=chunk_index,
                text=chunk_text,
                position=chunk_index,
                total_chunks=0,
                semantic_density=self.calculate_semantic_density(chunk_text),
                has_entities=self.detect_entities(chunk_text),
                metadata={
                    "word_count": len(current_chunk),
                    "char_count": len(chunk_text),
                    "chunk_type": "semantic"
                }
            )
            chunks.append(chunk)
        
        # Update total_chunks for all chunks
        for chunk in chunks:
            chunk.total_chunks = len(chunks)
            
        return chunks
    
    def calculate_semantic_density(self, text: str) -> float:
        """Calculate semantic density score"""
        # Simple heuristic - can be enhanced with ML
        words = text.split()
        unique_words = set(words)
        return len(unique_words) / len(words) if words else 0.0
    
    def detect_entities(self, text: str) -> bool:
        """Detect if chunk contains entities"""
        # Simple detection - can be enhanced with NER
        entity_indicators = [':', ';', '(', ')', '[', ']', '"', "'"]
        return any(indicator in text for indicator in entity_indicators)

class MetadataExtractor:
    """Extract comprehensive metadata"""
    
    def extract_comprehensive_metadata(self, document_text: str, blob_info: Dict) -> Dict[str, Any]:
        """Extract rich metadata for AI exploitation"""
        
        metadata = {
            "structure": {
                "sections": self.extract_sections(document_text),
                "hierarchy": self.build_hierarchy(document_text),
                "cross_references": self.find_references(document_text)
            },
            "semantic": {
                "key_concepts": self.extract_concepts(document_text),
                "domain": self.classify_domain(document_text),
                "complexity_score": self.assess_complexity(document_text)
            },
            "temporal": {
                "creation_date": datetime.now().isoformat(),
                "references_timeframe": self.extract_time_refs(document_text),
                "relevance_decay": 0.95  # Default high relevance
            },
            "relationships": {
                "citations": self.extract_citations(document_text),
                "topics": self.identify_topics(document_text),
                "similarity_anchors": []  # To be filled by similarity search
            },
            "blob_metadata": blob_info
        }
        
        return metadata
    
    def extract_sections(self, text: str) -> List[str]:
        """Extract document sections"""
        # Simple section detection
        lines = text.split('\n')
        sections = []
        for line in lines:
            if line.strip() and (line.startswith('#') or line.isupper()):
                sections.append(line.strip())
        return sections[:10]  # Limit for storage
    
    def build_hierarchy(self, text: str) -> Dict[str, Any]:
        """Build document hierarchy"""
        return {
            "depth": text.count('\n\n'),
            "paragraphs": len(text.split('\n\n')),
            "structure_type": "research_document"
        }
    
    def find_references(self, text: str) -> List[str]:
        """Find cross-references"""
        # Simple reference detection
        refs = []
        if 'http' in text.lower():
            refs.append("web_references")
        if 'figure' in text.lower() or 'table' in text.lower():
            refs.append("visual_references")
        return refs
    
    def extract_concepts(self, text: str) -> List[str]:
        """Extract key concepts"""
        # Simple keyword extraction
        research_keywords = [
            'analysis', 'research', 'method', 'result', 'conclusion',
            'data', 'model', 'algorithm', 'system', 'approach'
        ]
        found_concepts = []
        text_lower = text.lower()
        for keyword in research_keywords:
            if keyword in text_lower:
                found_concepts.append(keyword)
        return found_concepts
    
    def classify_domain(self, text: str) -> str:
        """Classify document domain"""
        text_lower = text.lower()
        if any(word in text_lower for word in ['ai', 'machine learning', 'neural', 'deep learning']):
            return "artificial_intelligence"
        elif any(word in text_lower for word in ['data', 'analytics', 'statistics']):
            return "data_science"
        elif any(word in text_lower for word in ['research', 'study', 'analysis']):
            return "research"
        else:
            return "general"
    
    def assess_complexity(self, text: str) -> float:
        """Assess document complexity"""
        words = text.split()
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        return min(avg_word_length / 10.0, 1.0)  # Normalized complexity
    
    def extract_time_refs(self, text: str) -> List[str]:
        """Extract temporal references"""
        time_indicators = ['2025', '2024', 'recent', 'current', 'latest']
        found_refs = []
        text_lower = text.lower()
        for indicator in time_indicators:
            if indicator in text_lower:
                found_refs.append(indicator)
        return found_refs
    
    def extract_citations(self, text: str) -> List[str]:
        """Extract citations"""
        # Simple citation detection
        citations = []
        if '(' in text and ')' in text:
            citations.append("parenthetical_citations")
        if '[' in text and ']' in text:
            citations.append("bracket_citations")
        return citations
    
    def identify_topics(self, text: str) -> List[str]:
        """Identify main topics"""
        # Simple topic identification
        topics = []
        text_lower = text.lower()
        topic_keywords = {
            "methodology": ["method", "approach", "technique"],
            "analysis": ["analysis", "analyze", "evaluation"],
            "results": ["result", "finding", "outcome"],
            "discussion": ["discussion", "implication", "significance"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        return topics

class HybridStoragePipeline:
    """Main pipeline for Blob→Cosmos processing"""
    
    def __init__(self):
        self.blob_client = None
        self.cosmos_client = None
        self.chunker = IntelligentChunker()
        self.extractor = MetadataExtractor()
        self.container_name = "research-content-blob"
        self.cosmos_container = "processed_documents"
        
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize Azure clients"""
        try:
            # Blob client
            connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
            if not connection_string:
                raise ValueError("AZURE_STORAGE_CONNECTION_STRING not found")
            self.blob_client = BlobServiceClient.from_connection_string(connection_string)
            
            # Cosmos client
            cosmos_endpoint = os.getenv('COSMOS_ENDPOINT')
            cosmos_key = os.getenv('COSMOS_KEY')
            if not cosmos_endpoint or not cosmos_key:
                raise ValueError("Cosmos DB credentials not found")
            
            self.cosmos_client = CosmosClient(cosmos_endpoint, cosmos_key)
            
            print("✅ Azure clients initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing clients: {e}")
            raise
    
    def upload_document_to_blob(self, file_path: str, blob_name: str = None) -> Dict[str, Any]:
        """Upload document to blob storage"""
        
        try:
            if not blob_name:
                blob_name = f"raw_research/documents/{Path(file_path).name}"
            
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Upload to blob
            container_client = self.blob_client.get_container_client(self.container_name)
            blob_client = container_client.get_blob_client(blob_name)
            
            blob_client.upload_blob(
                data=content,
                metadata={
                    "original_name": Path(file_path).name,
                    "upload_time": datetime.now().isoformat(),
                    "content_type": "research_document",
                    "processing_stage": "raw"
                },
                overwrite=True
            )
            
            blob_info = {
                "container": self.container_name,
                "blob_name": blob_name,
                "size_bytes": len(content.encode('utf-8')),
                "url": f"https://{self.blob_client.account_name}.blob.core.windows.net/{self.container_name}/{blob_name}"
            }
            
            print(f"✅ Uploaded to blob: {blob_name}")
            return blob_info, content
            
        except Exception as e:
            print(f"❌ Error uploading to blob: {e}")
            raise
    
    def process_document(self, file_path: str) -> ProcessedDocument:
        """Complete document processing pipeline"""
        
        print(f"🔄 Processing document: {Path(file_path).name}")
        
        # 1. Upload to blob
        blob_info, content = self.upload_document_to_blob(file_path)
        
        # 2. Generate document ID
        doc_id = hashlib.md5(content.encode()).hexdigest()[:16]
        
        # 3. Chunk document
        chunks = self.chunker.chunk_document(content, doc_id)
        print(f"   📄 Created {len(chunks)} chunks")
        
        # 4. Extract metadata
        metadata = self.extractor.extract_comprehensive_metadata(content, blob_info)
        print(f"   🔍 Extracted metadata for {metadata['semantic']['domain']} domain")
        
        # 5. Prepare graph-ready data (for future Gremlin)
        graph_data = self.prepare_graph_data(content, chunks, metadata)
        
        # 6. Create processed document
        processed_doc = ProcessedDocument(
            id=doc_id,
            type="research_document",
            blob_reference=blob_info,
            content_summary={
                "title": Path(file_path).stem,
                "chunk_count": len(chunks),
                "total_chars": len(content),
                "domain": metadata['semantic']['domain'],
                "complexity": metadata['semantic']['complexity_score']
            },
            chunks=[asdict(chunk) for chunk in chunks],
            graph_ready=graph_data,
            ai_metadata={
                "processing_date": datetime.now().isoformat(),
                "model_versions": {
                    "chunker": "semantic_v1.0",
                    "extractor": "basic_v1.0"
                },
                "quality_scores": {
                    "extraction_confidence": 0.85,
                    "coherence": 0.90,
                    "completeness": 0.88
                }
            },
            processing_timestamp=datetime.now().isoformat()
        )
        
        return processed_doc
    
    def prepare_graph_data(self, content: str, chunks: List[DocumentChunk], metadata: Dict) -> Dict[str, Any]:
        """Prepare data for future Gremlin implementation"""
        
        # Extract potential graph nodes and edges
        nodes = []
        edges = []
        
        # Create document node
        nodes.append({
            "id": f"doc_{hashlib.md5(content.encode()).hexdigest()[:8]}",
            "label": "Document",
            "type": "ResearchDocument",
            "properties": {
                "title": metadata.get('title', 'Unknown'),
                "domain": metadata['semantic']['domain'],
                "complexity": metadata['semantic']['complexity_score']
            }
        })
        
        # Create concept nodes from extracted concepts
        for i, concept in enumerate(metadata['semantic']['key_concepts']):
            node_id = f"concept_{concept}_{i}"
            nodes.append({
                "id": node_id,
                "label": "Concept",
                "type": "ResearchConcept",
                "properties": {
                    "name": concept,
                    "frequency": content.lower().count(concept.lower())
                }
            })
            
            # Create edge between document and concept
            edges.append({
                "id": f"edge_doc_concept_{i}",
                "label": "CONTAINS_CONCEPT",
                "source": nodes[0]["id"],
                "target": node_id,
                "properties": {
                    "strength": min(content.lower().count(concept.lower()) / 10, 1.0)
                }
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "graph_metadata": {
                "node_count": len(nodes),
                "edge_count": len(edges),
                "prepared_for": "gremlin_future_implementation"
            }
        }
    
    def store_in_cosmos(self, processed_doc: ProcessedDocument) -> bool:
        """Store processed document in Cosmos DB"""
        
        try:
            database = self.cosmos_client.get_database_client(os.getenv('COSMOS_DATABASE'))
            
            # Create container if it doesn't exist
            try:
                container = database.get_container_client(self.cosmos_container)
            except:
                container = database.create_container_if_not_exists(
                    id=self.cosmos_container,
                    partition_key="/type"
                )
                print(f"✅ Created Cosmos container: {self.cosmos_container}")
            
            # Store document
            doc_dict = asdict(processed_doc)
            container.create_item(doc_dict)
            
            print(f"✅ Stored in Cosmos: {processed_doc.id}")
            return True
            
        except Exception as e:
            print(f"❌ Error storing in Cosmos: {e}")
            return False
    
    def process_and_store(self, file_path: str) -> Dict[str, Any]:
        """Complete pipeline: process document and store in Cosmos"""
        
        try:
            # Process document
            processed_doc = self.process_document(file_path)
            
            # Store in Cosmos
            success = self.store_in_cosmos(processed_doc)
            
            if success:
                result = {
                    "success": True,
                    "document_id": processed_doc.id,
                    "chunks_created": len(processed_doc.chunks),
                    "blob_url": processed_doc.blob_reference["url"],
                    "cosmos_container": self.cosmos_container,
                    "graph_nodes": len(processed_doc.graph_ready["nodes"]),
                    "graph_edges": len(processed_doc.graph_ready["edges"])
                }
                
                print(f"🎯 SUCCESS: Document processed and stored")
                print(f"   Document ID: {result['document_id']}")
                print(f"   Chunks: {result['chunks_created']}")
                print(f"   Graph nodes: {result['graph_nodes']}")
                
                return result
            else:
                raise Exception("Failed to store in Cosmos")
                
        except Exception as e:
            print(f"❌ Pipeline failed: {e}")
            return {"success": False, "error": str(e)}

def main():
    """Test the pipeline with the research report"""
    
    pipeline = HybridStoragePipeline()
    
    # Test with existing research report
    test_file = "/Users/mikaeleage/Research & Analytics Services/RESEARCH/analytics/Advanced_Agentic_Reasoning_Research_Report.md"
    
    if Path(test_file).exists():
        print(f"🚀 Testing hybrid pipeline with: {Path(test_file).name}")
        result = pipeline.process_and_store(test_file)
        
        if result["success"]:
            print(f"\n✅ EVIDENCE OF SUCCESS:")
            print(f"   Document ID: {result['document_id']}")
            print(f"   Blob URL: {result['blob_url']}")
            print(f"   Cosmos Container: {result['cosmos_container']}")
            print(f"   Total Chunks: {result['chunks_created']}")
            print(f"   Graph Ready: {result['graph_nodes']} nodes, {result['graph_edges']} edges")
        else:
            print(f"\n❌ PIPELINE FAILED: {result.get('error', 'Unknown error')}")
    else:
        print(f"❌ Test file not found: {test_file}")

if __name__ == "__main__":
    main()