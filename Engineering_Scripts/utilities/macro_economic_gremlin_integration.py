#!/usr/bin/env python3
"""
Macro-Economic Gremlin Integration with Detailed Summaries and Sources
Specialized integration for macro-economic knowledge graph with comprehensive content storage
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

class MacroEconomicDetailedSummaryExtractor:
    """Extract detailed summaries with facts, content, and sources for macro-economic research"""
    
    def __init__(self):
        self.academic_sources = []
        self.key_facts = []
        self.methodological_frameworks = []
        self.empirical_findings = []
    
    def extract_detailed_summary(self, document_text: str, metadata: Dict) -> Dict[str, Any]:
        """Extract comprehensive summary with facts, content, and sources"""
        
        # Parse document sections
        sections = self._parse_document_sections(document_text)
        
        # Extract academic sources
        sources = self._extract_academic_sources(document_text)
        
        # Extract key facts and findings
        facts = self._extract_key_facts(document_text, sections)
        
        # Extract methodological insights
        methodologies = self._extract_methodological_insights(document_text, sections)
        
        # Extract empirical findings
        findings = self._extract_empirical_findings(document_text, sections)
        
        # Extract policy implications
        policy_implications = self._extract_policy_implications(document_text, sections)
        
        # Extract future research directions
        future_research = self._extract_future_research_directions(document_text, sections)
        
        detailed_summary = {
            "executive_summary": {
                "main_contribution": self._identify_main_contribution(document_text),
                "research_scope": metadata.get('domain_classification', {}).get('geographic_scope', ['global']),
                "key_innovation": self._identify_key_innovation(document_text),
                "practical_impact": self._assess_practical_impact(document_text)
            },
            "academic_sources": {
                "total_sources": len(sources),
                "source_breakdown": self._categorize_sources(sources),
                "key_papers": sources[:10],  # Top 10 most important sources
                "complete_bibliography": sources
            },
            "key_facts_and_findings": {
                "performance_metrics": facts.get('performance_metrics', []),
                "quantitative_results": facts.get('quantitative_results', []),
                "comparative_analysis": facts.get('comparative_analysis', []),
                "statistical_evidence": facts.get('statistical_evidence', [])
            },
            "methodological_frameworks": {
                "graph_construction_methods": methodologies.get('graph_construction', []),
                "validation_approaches": methodologies.get('validation', []),
                "evaluation_metrics": methodologies.get('evaluation', []),
                "implementation_tools": methodologies.get('tools', [])
            },
            "empirical_findings": {
                "forecasting_improvements": findings.get('forecasting', []),
                "network_analysis_results": findings.get('network_analysis', []),
                "cross_country_validation": findings.get('cross_country', []),
                "performance_benchmarks": findings.get('benchmarks', [])
            },
            "policy_implications": {
                "central_bank_applications": policy_implications.get('central_bank', []),
                "government_policy_analysis": policy_implications.get('government', []),
                "financial_institution_use": policy_implications.get('financial', []),
                "international_organization_benefits": policy_implications.get('international', [])
            },
            "future_research_directions": {
                "emerging_technologies": future_research.get('technologies', []),
                "methodological_advances": future_research.get('methodologies', []),
                "data_integration_opportunities": future_research.get('data', []),
                "practical_applications": future_research.get('applications', [])
            },
            "content_structure": {
                "section_summaries": self._create_section_summaries(sections),
                "concept_hierarchy": self._build_concept_hierarchy(document_text),
                "cross_references": self._identify_cross_references(document_text)
            }
        }
        
        return detailed_summary
    
    def _parse_document_sections(self, text: str) -> Dict[str, str]:
        """Parse document into structured sections"""
        sections = {}
        current_section = None
        current_content = []
        
        lines = text.split('\n')
        
        for line in lines:
            if line.startswith('#'):
                # Save previous section
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # Start new section
                current_section = line.strip('#').strip()
                current_content = []
            else:
                current_content.append(line)
        
        # Save final section
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def _extract_academic_sources(self, text: str) -> List[Dict[str, str]]:
        """Extract academic sources with detailed metadata"""
        sources = []
        
        # Extract DOI references
        import re
        doi_pattern = r'DOI[:\s]*([0-9a-zA-Z\./\-_]+)'
        dois = re.findall(doi_pattern, text, re.IGNORECASE)
        
        # Extract ArXiv references
        arxiv_pattern = r'arXiv:([0-9]+\.[0-9]+)'
        arxiv_refs = re.findall(arxiv_pattern, text, re.IGNORECASE)
        
        # Extract URL references
        url_pattern = r'https?://[^\s\)]+(?:\.[^\s\)]+)*'
        urls = re.findall(url_pattern, text)
        
        # Extract publication references
        publication_pattern = r'(\*\*.*?\*\*)\s*\((\d{4})\)'
        publications = re.findall(publication_pattern, text)
        
        # Combine all sources
        for doi in dois:
            sources.append({
                "type": "DOI",
                "reference": doi,
                "url": f"https://doi.org/{doi}",
                "category": "peer_reviewed"
            })
        
        for arxiv in arxiv_refs:
            sources.append({
                "type": "ArXiv",
                "reference": arxiv,
                "url": f"https://arxiv.org/abs/{arxiv}",
                "category": "preprint"
            })
        
        for url in urls:
            if 'arxiv.org' in url:
                category = 'preprint'
            elif 'doi.org' in url or 'journal' in url:
                category = 'peer_reviewed'
            elif 'ssrn.com' in url:
                category = 'working_paper'
            else:
                category = 'web_resource'
            
            sources.append({
                "type": "URL",
                "reference": url,
                "url": url,
                "category": category
            })
        
        for title, year in publications:
            sources.append({
                "type": "Publication",
                "reference": f"{title} ({year})",
                "year": year,
                "category": "academic_paper"
            })
        
        return sources
    
    def _extract_key_facts(self, text: str, sections: Dict[str, str]) -> Dict[str, List[str]]:
        """Extract key facts and quantitative findings"""
        facts = {
            'performance_metrics': [],
            'quantitative_results': [],
            'comparative_analysis': [],
            'statistical_evidence': []
        }
        
        # Extract performance metrics
        import re
        
        # Find percentage improvements
        percentage_pattern = r'(\d+(?:\.\d+)?%)\s+improvement'
        percentages = re.findall(percentage_pattern, text, re.IGNORECASE)
        for perc in percentages:
            facts['performance_metrics'].append(f"Performance improvement: {perc}")
        
        # Find accuracy metrics
        accuracy_pattern = r'accuracy[:\s]*(\d+(?:\.\d+)?%?)'
        accuracies = re.findall(accuracy_pattern, text, re.IGNORECASE)
        for acc in accuracies:
            facts['performance_metrics'].append(f"Accuracy: {acc}")
        
        # Find F1 scores
        f1_pattern = r'F1[:\s-]*score[:\s]*(\d+\.\d+)'
        f1_scores = re.findall(f1_pattern, text, re.IGNORECASE)
        for f1 in f1_scores:
            facts['performance_metrics'].append(f"F1-score: {f1}")
        
        # Extract quantitative results from specific sections
        if 'Performance Results and Evaluation Metrics' in sections:
            performance_text = sections['Performance Results and Evaluation Metrics']
            
            # Extract RMSE improvements
            rmse_pattern = r'rmse[:\s]*(\d+\.\d+)'
            rmse_values = re.findall(rmse_pattern, performance_text, re.IGNORECASE)
            for rmse in rmse_values:
                facts['quantitative_results'].append(f"RMSE: {rmse}")
            
            # Extract forecast horizons
            horizon_pattern = r'(\d+)[_\s-]?month[s]?\s+horizon'
            horizons = re.findall(horizon_pattern, performance_text, re.IGNORECASE)
            for horizon in horizons:
                facts['quantitative_results'].append(f"Forecast horizon: {horizon} months")
        
        # Extract comparative analysis
        comparison_keywords = ['compared to', 'versus', 'outperforms', 'superior to']
        for keyword in comparison_keywords:
            if keyword in text.lower():
                # Extract context around comparison
                import re
                pattern = fr'.{{0,100}}{keyword}.{{0,100}}'
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches[:3]:  # Limit to 3 matches
                    facts['comparative_analysis'].append(match.strip())
        
        return facts
    
    def _extract_methodological_insights(self, text: str, sections: Dict[str, str]) -> Dict[str, List[str]]:
        """Extract methodological frameworks and approaches"""
        methodologies = {
            'graph_construction': [],
            'validation': [],
            'evaluation': [],
            'tools': []
        }
        
        # Extract graph construction methods
        graph_keywords = ['knowledge graph', 'graph neural network', 'graph construction', 'node embedding']
        for keyword in graph_keywords:
            if keyword in text.lower():
                # Find context
                import re
                pattern = fr'.{{0,150}}{keyword}.{{0,150}}'
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches[:2]:
                    methodologies['graph_construction'].append(match.strip())
        
        # Extract validation approaches
        validation_keywords = ['granger causality', 'statistical validation', 'cross-validation', 'robustness check']
        for keyword in validation_keywords:
            if keyword in text.lower():
                import re
                pattern = fr'.{{0,100}}{keyword}.{{0,100}}'
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches[:2]:
                    methodologies['validation'].append(match.strip())
        
        # Extract evaluation metrics
        metric_keywords = ['evaluation metric', 'performance measure', 'benchmark', 'assessment criteria']
        for keyword in metric_keywords:
            if keyword in text.lower():
                import re
                pattern = fr'.{{0,100}}{keyword}.{{0,100}}'
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches[:2]:
                    methodologies['evaluation'].append(match.strip())
        
        # Extract implementation tools
        tool_keywords = ['pytorch', 'tensorflow', 'networkx', 'neo4j', 'gremlin', 'fastapi']
        for keyword in tool_keywords:
            if keyword in text.lower():
                methodologies['tools'].append(keyword.upper())
        
        return methodologies
    
    def _extract_empirical_findings(self, text: str, sections: Dict[str, str]) -> Dict[str, List[str]]:
        """Extract empirical findings and results"""
        findings = {
            'forecasting': [],
            'network_analysis': [],
            'cross_country': [],
            'benchmarks': []
        }
        
        # Extract forecasting results
        forecast_keywords = ['forecast accuracy', 'prediction improvement', 'forecasting performance']
        for keyword in forecast_keywords:
            if keyword in text.lower():
                import re
                pattern = fr'.{{0,150}}{keyword}.{{0,150}}'
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches[:2]:
                    findings['forecasting'].append(match.strip())
        
        # Extract network analysis findings
        network_keywords = ['network structure', 'centrality measures', 'community detection', 'path analysis']
        for keyword in network_keywords:
            if keyword in text.lower():
                import re
                pattern = fr'.{{0,120}}{keyword}.{{0,120}}'
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches[:2]:
                    findings['network_analysis'].append(match.strip())
        
        # Extract cross-country validation
        country_keywords = ['cross-country', 'international validation', 'global performance']
        for keyword in country_keywords:
            if keyword in text.lower():
                import re
                pattern = fr'.{{0,120}}{keyword}.{{0,120}}'
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches[:2]:
                    findings['cross_country'].append(match.strip())
        
        return findings
    
    def _extract_policy_implications(self, text: str, sections: Dict[str, str]) -> Dict[str, List[str]]:
        """Extract policy implications and applications"""
        implications = {
            'central_bank': [],
            'government': [],
            'financial': [],
            'international': []
        }
        
        # Extract central bank applications
        cb_keywords = ['central bank', 'monetary policy', 'financial stability']
        for keyword in cb_keywords:
            if keyword in text.lower():
                import re
                pattern = fr'.{{0,100}}{keyword}.{{0,100}}'
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches[:2]:
                    implications['central_bank'].append(match.strip())
        
        # Extract government policy applications
        gov_keywords = ['government policy', 'fiscal policy', 'policy analysis']
        for keyword in gov_keywords:
            if keyword in text.lower():
                import re
                pattern = fr'.{{0,100}}{keyword}.{{0,100}}'
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches[:2]:
                    implications['government'].append(match.strip())
        
        return implications
    
    def _extract_future_research_directions(self, text: str, sections: Dict[str, str]) -> Dict[str, List[str]]:
        """Extract future research directions"""
        future_research = {
            'technologies': [],
            'methodologies': [],
            'data': [],
            'applications': []
        }
        
        # Look for future research section
        future_keywords = ['future research', 'research directions', 'next steps', 'limitations']
        
        for section_name, section_content in sections.items():
            if any(keyword in section_name.lower() for keyword in future_keywords):
                # Extract bullet points or numbered items
                import re
                bullet_pattern = r'[•\-\*]\s*([^\n]+)'
                bullets = re.findall(bullet_pattern, section_content)
                
                number_pattern = r'\d+\.\s*([^\n]+)'
                numbers = re.findall(number_pattern, section_content)
                
                all_items = bullets + numbers
                
                # Categorize items
                for item in all_items:
                    item_lower = item.lower()
                    if any(tech in item_lower for tech in ['llm', 'ai', 'machine learning', 'federated']):
                        future_research['technologies'].append(item.strip())
                    elif any(method in item_lower for method in ['causal', 'inference', 'discovery']):
                        future_research['methodologies'].append(item.strip())
                    elif any(data in item_lower for data in ['data', 'integration', 'modal']):
                        future_research['data'].append(item.strip())
                    else:
                        future_research['applications'].append(item.strip())
        
        return future_research
    
    def _categorize_sources(self, sources: List[Dict]) -> Dict[str, int]:
        """Categorize sources by type"""
        categories = {}
        for source in sources:
            category = source.get('category', 'unknown')
            categories[category] = categories.get(category, 0) + 1
        return categories
    
    def _identify_main_contribution(self, text: str) -> str:
        """Identify the main contribution of the research"""
        contribution_keywords = [
            'main contribution', 'key contribution', 'novel approach',
            'breakthrough', 'innovation', 'advancement'
        ]
        
        for keyword in contribution_keywords:
            if keyword in text.lower():
                import re
                pattern = fr'.{{0,200}}{keyword}.{{0,200}}'
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    return matches[0].strip()
        
        # Default based on document analysis
        return "Comprehensive analysis of knowledge graph modeling for macro-economic analysis with practical implementation frameworks"
    
    def _identify_key_innovation(self, text: str) -> str:
        """Identify key innovation"""
        if 'hybrid storage' in text.lower():
            return "Hybrid storage architecture combining Blob, Cosmos DB, and Gremlin for AI-exploitable knowledge graphs"
        elif 'graph neural network' in text.lower():
            return "Integration of graph neural networks with traditional economic modeling"
        else:
            return "Advanced knowledge graph methodologies for economic analysis"
    
    def _assess_practical_impact(self, text: str) -> str:
        """Assess practical impact"""
        impact_indicators = ['15-30% improvement', 'production-ready', 'real-time', 'policy makers']
        
        for indicator in impact_indicators:
            if indicator in text.lower():
                return "High practical impact with demonstrated performance improvements and production-ready implementations"
        
        return "Significant theoretical and methodological contributions to economic modeling"
    
    def _create_section_summaries(self, sections: Dict[str, str]) -> Dict[str, str]:
        """Create brief summaries for each section"""
        summaries = {}
        
        for section_name, content in sections.items():
            # Create a brief summary (first 200 characters + key points)
            brief = content[:200].strip()
            if len(content) > 200:
                brief += "..."
            
            # Add key points if they exist
            import re
            bullet_points = re.findall(r'[•\-\*]\s*([^\n]+)', content)
            if bullet_points:
                brief += f" Key points: {', '.join(bullet_points[:3])}"
            
            summaries[section_name] = brief
        
        return summaries
    
    def _build_concept_hierarchy(self, text: str) -> Dict[str, List[str]]:
        """Build concept hierarchy from document"""
        hierarchy = {
            'macro_economics': [],
            'methodologies': [],
            'technologies': [],
            'applications': []
        }
        
        # Extract concepts and categorize them
        econ_concepts = ['gdp', 'inflation', 'monetary policy', 'fiscal policy', 'central bank']
        method_concepts = ['graph neural network', 'knowledge graph', 'machine learning']
        tech_concepts = ['azure', 'cosmos db', 'gremlin', 'blob storage']
        app_concepts = ['forecasting', 'policy analysis', 'risk management']
        
        text_lower = text.lower()
        
        for concept in econ_concepts:
            if concept in text_lower:
                hierarchy['macro_economics'].append(concept)
        
        for concept in method_concepts:
            if concept in text_lower:
                hierarchy['methodologies'].append(concept)
        
        for concept in tech_concepts:
            if concept in text_lower:
                hierarchy['technologies'].append(concept)
        
        for concept in app_concepts:
            if concept in text_lower:
                hierarchy['applications'].append(concept)
        
        return hierarchy
    
    def _identify_cross_references(self, text: str) -> List[str]:
        """Identify cross-references within the document"""
        import re
        
        # Find section references
        section_refs = re.findall(r'[Ss]ection\s+(\d+(?:\.\d+)?)', text)
        
        # Find figure/table references
        fig_refs = re.findall(r'[Ff]igure\s+(\d+)', text)
        table_refs = re.findall(r'[Tt]able\s+(\d+)', text)
        
        cross_refs = []
        cross_refs.extend([f"Section {ref}" for ref in section_refs])
        cross_refs.extend([f"Figure {ref}" for ref in fig_refs])
        cross_refs.extend([f"Table {ref}" for ref in table_refs])
        
        return list(set(cross_refs))  # Remove duplicates

class MacroEconomicGremlinManager:
    """Specialized Gremlin manager for macro-economic knowledge graphs"""
    
    def __init__(self):
        if not GREMLIN_AVAILABLE:
            raise ImportError("gremlinpython required - run: poetry add gremlinpython")
        
        self.cosmos_client = None
        self.gremlin_client = None
        self.summary_extractor = MacroEconomicDetailedSummaryExtractor()
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
            
            print("✅ Macro-economic Gremlin and Cosmos clients initialized")
            
        except Exception as e:
            print(f"❌ Error initializing clients: {e}")
            raise
    
    def ingest_macro_economic_research_with_details(self, document_id: str) -> Dict[str, Any]:
        """Ingest macro-economic research with detailed summaries and sources"""
        
        print(f"🏦 Ingesting macro-economic research with detailed summaries: {document_id}")
        
        try:
            # Get document from Cosmos
            database = self.cosmos_client.get_database_client(os.getenv('COSMOS_DATABASE'))
            container = database.get_container_client('processed_documents')
            
            document = container.read_item(
                item=document_id,
                partition_key='macro_economic_research'
            )
            
            # Extract detailed summary with sources and facts
            original_content = self._get_original_content(document)
            metadata = document.get('macro_economic_metadata', {})
            
            detailed_summary = self.summary_extractor.extract_detailed_summary(original_content, metadata)
            
            print(f"   📊 Extracted detailed summary with {detailed_summary['academic_sources']['total_sources']} sources")
            
            # Store detailed summary back in Cosmos
            document['detailed_summary'] = detailed_summary
            document['summary_extraction_timestamp'] = datetime.now().isoformat()
            
            container.replace_item(
                item=document_id,
                body=document
            )
            
            print(f"   💾 Updated Cosmos document with detailed summary")
            
            # Get graph data
            graph_data = document.get('graph_ready', {})
            
            if not graph_data:
                raise ValueError("No graph_ready data found in document")
            
            nodes = graph_data.get('nodes', [])
            edges = graph_data.get('edges', [])
            
            print(f"   🌐 Processing {len(nodes)} nodes and {len(edges)} edges")
            
            # Clear existing graph data for this document
            self._clear_macro_economic_graph_data(document_id)
            
            # Create enhanced nodes with detailed summaries
            vertices_created = []
            
            for node in nodes:
                try:
                    # Enhanced node creation with detailed metadata
                    node_properties = node['properties'].copy()
                    
                    # Add detailed summary information for document nodes
                    if node['type'] == 'ResearchDocument':
                        node_properties.update({
                            'main_contribution': detailed_summary['executive_summary']['main_contribution'],
                            'key_innovation': detailed_summary['executive_summary']['key_innovation'],
                            'practical_impact': detailed_summary['executive_summary']['practical_impact'],
                            'total_sources': detailed_summary['academic_sources']['total_sources'],
                            'source_categories': json.dumps(detailed_summary['academic_sources']['source_breakdown']),
                            'performance_metrics_count': len(detailed_summary['key_facts_and_findings']['performance_metrics']),
                            'methodological_frameworks_count': len(detailed_summary['methodological_frameworks']['graph_construction_methods'])
                        })
                    
                    # Add economic concept details
                    elif node['type'] == 'MacroEconomicConcept':
                        concept_name = node_properties.get('name', '')
                        # Add context from detailed summary
                        node_properties['research_context'] = self._get_concept_context(concept_name, detailed_summary)
                    
                    # Create Gremlin vertex
                    query = f"""
                    g.addV('{node['type']}')
                     .property('id', '{node['id']}')
                     .property('document_id', '{document_id}')
                     .property('domain', 'macro_economics')
                    """
                    
                    # Add all properties
                    for prop_key, prop_value in node_properties.items():
                        if isinstance(prop_value, str):
                            escaped_value = prop_value.replace("'", "\\'").replace('"', '\\"')
                            query += f".property('{prop_key}', '{escaped_value}')"
                        elif isinstance(prop_value, (int, float)):
                            query += f".property('{prop_key}', {prop_value})"
                        elif isinstance(prop_value, list):
                            query += f".property('{prop_key}', '{json.dumps(prop_value)}')"
                    
                    result = self.gremlin_client.submit(query).all().result()
                    vertices_created.append(node['id'])
                    
                    print(f"      ✅ Created enhanced vertex: {node['id']} ({node['type']})")
                    
                except Exception as e:
                    print(f"      ❌ Failed to create vertex {node['id']}: {e}")
            
            # Create enhanced edges with relationship context
            edges_created = []
            
            for edge in edges:
                try:
                    # Enhanced edge creation with context
                    edge_properties = edge.get('properties', {}).copy()
                    
                    # Add relationship context
                    edge_properties['relationship_context'] = self._get_relationship_context(
                        edge['source'], edge['target'], edge['label'], detailed_summary
                    )
                    
                    query = f"""
                    g.V().has('id', '{edge['source']}')
                     .addE('{edge['label']}')
                     .to(g.V().has('id', '{edge['target']}'))
                    """
                    
                    # Add edge properties
                    for prop_key, prop_value in edge_properties.items():
                        if isinstance(prop_value, str):
                            escaped_value = prop_value.replace("'", "\\'").replace('"', '\\"')
                            query += f".property('{prop_key}', '{escaped_value}')"
                        elif isinstance(prop_value, (int, float)):
                            query += f".property('{prop_key}', {prop_value})"
                    
                    result = self.gremlin_client.submit(query).all().result()
                    edges_created.append(edge['id'])
                    
                    print(f"      ✅ Created enhanced edge: {edge['source']} --{edge['label']}--> {edge['target']}")
                    
                except Exception as e:
                    print(f"      ❌ Failed to create edge {edge['id']}: {e}")
            
            # Update Cosmos document with Gremlin references
            document['gremlin_ingested'] = {
                "ingested_at": datetime.now().isoformat(),
                "vertices_created": vertices_created,
                "edges_created": edges_created,
                "enhanced_with_detailed_summaries": True,
                "academic_sources_count": detailed_summary['academic_sources']['total_sources'],
                "key_facts_count": len(detailed_summary['key_facts_and_findings']['performance_metrics']),
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
                "detailed_summary_extracted": True,
                "academic_sources": detailed_summary['academic_sources']['total_sources'],
                "key_facts": len(detailed_summary['key_facts_and_findings']['performance_metrics']),
                "methodologies": len(detailed_summary['methodological_frameworks']['graph_construction_methods']),
                "policy_implications": len(detailed_summary['policy_implications']['central_bank']),
                "gremlin_database": os.getenv('GREMLIN_DATABASE'),
                "ingestion_timestamp": datetime.now().isoformat()
            }
            
            print(f"✅ Macro-economic graph ingestion with detailed summaries complete")
            print(f"   Vertices: {result['vertices_created']}")
            print(f"   Edges: {result['edges_created']}")
            print(f"   Academic sources: {result['academic_sources']}")
            print(f"   Key facts: {result['key_facts']}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error ingesting macro-economic research: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_original_content(self, document: Dict) -> str:
        """Reconstruct original content from chunks for detailed analysis"""
        chunks = document.get('chunks', [])
        
        # Sort chunks by sequence
        sorted_chunks = sorted(chunks, key=lambda x: x.get('sequence', 0))
        
        # Reconstruct content
        content_parts = []
        for chunk in sorted_chunks:
            content_parts.append(chunk.get('text', ''))
        
        return '\n'.join(content_parts)
    
    def _clear_macro_economic_graph_data(self, document_id: str):
        """Clear existing macro-economic graph data"""
        
        try:
            query = f"g.V().has('document_id', '{document_id}').drop()"
            self.gremlin_client.submit(query).all().result()
            print(f"   🧹 Cleared existing macro-economic graph data for document: {document_id}")
            
        except Exception as e:
            print(f"   ⚠️  Could not clear existing data: {e}")
    
    def _get_concept_context(self, concept_name: str, detailed_summary: Dict) -> str:
        """Get context for economic concept from detailed summary"""
        
        # Look for concept in key facts
        for fact in detailed_summary['key_facts_and_findings']['performance_metrics']:
            if concept_name.lower() in fact.lower():
                return f"Performance context: {fact}"
        
        # Look in methodological frameworks
        for method in detailed_summary['methodological_frameworks']['graph_construction_methods']:
            if concept_name.lower() in method.lower():
                return f"Methodological context: {method}"
        
        return f"Economic concept in macro-economic knowledge graph research"
    
    def _get_relationship_context(self, source: str, target: str, relationship: str, detailed_summary: Dict) -> str:
        """Get context for relationship from detailed summary"""
        
        # Default relationship context
        context = f"{relationship} relationship in macro-economic knowledge graph"
        
        # Look for specific relationship mentions in empirical findings
        for finding in detailed_summary['empirical_findings']['network_analysis']:
            if any(term in finding.lower() for term in [source.split('_')[-1], target.split('_')[-1]]):
                return f"Empirical context: {finding[:100]}"
        
        return context

def main():
    """Test macro-economic Gremlin integration with detailed summaries"""
    
    if not GREMLIN_AVAILABLE:
        print("❌ gremlinpython not available - run: poetry add gremlinpython")
        return
    
    graph_manager = MacroEconomicGremlinManager()
    document_id = "macro_econ_e083c9af60c354e3"
    
    print(f"🚀 Testing macro-economic Gremlin integration with detailed summaries")
    print(f"🎯 Target document: {document_id}")
    
    # Ingest with detailed summaries and sources
    result = graph_manager.ingest_macro_economic_research_with_details(document_id)
    
    if result["success"]:
        print(f"\n✅ MACRO-ECONOMIC GRAPH INGESTION SUCCESS:")
        print(f"   Document ID: {result['document_id']}")
        print(f"   Vertices created: {result['vertices_created']}")
        print(f"   Edges created: {result['edges_created']}")
        print(f"   Academic sources processed: {result['academic_sources']}")
        print(f"   Key facts extracted: {result['key_facts']}")
        print(f"   Methodologies identified: {result['methodologies']}")
        print(f"   Policy implications: {result['policy_implications']}")
        print(f"   Database: {result['gremlin_database']}")
        print(f"\n🎯 ENHANCED MACRO-ECONOMIC KNOWLEDGE GRAPH WITH DETAILED SUMMARIES READY")
    else:
        print(f"\n❌ INGESTION FAILED: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()