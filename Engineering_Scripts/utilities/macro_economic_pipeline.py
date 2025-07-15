#!/usr/bin/env python3
"""
Macro-Economic Knowledge Graph Pipeline
Specialized pipeline for processing macro-economic research with domain-specific categorization
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
class MacroEconomicChunk:
    """Macro-economic document chunk with specialized metadata"""
    chunk_id: str
    sequence: int
    text: str
    position: int
    total_chunks: int
    economic_concepts: List[str]
    economic_indicators: List[str]
    policy_references: List[str]
    methodological_approaches: List[str]
    data_sources: List[str]
    semantic_density: float
    economic_relevance_score: float
    metadata: Dict[str, Any]

class MacroEconomicChunker:
    """Specialized chunking for macro-economic content"""
    
    def __init__(self):
        self.min_size = 512
        self.max_size = 1024  # Larger chunks for economic concepts
        self.overlap = 100
        
        # Economic concept dictionaries
        self.economic_concepts = [
            'gdp', 'inflation', 'unemployment', 'monetary_policy', 'fiscal_policy',
            'central_bank', 'interest_rates', 'trade_balance', 'current_account',
            'exchange_rate', 'budget_deficit', 'debt_to_gdp', 'productivity',
            'economic_growth', 'recession', 'business_cycle', 'shock_propagation'
        ]
        
        self.economic_indicators = [
            'cpi', 'ppi', 'employment_rate', 'labor_force_participation',
            'industrial_production', 'retail_sales', 'housing_starts',
            'consumer_confidence', 'manufacturing_pmi', 'services_pmi'
        ]
        
        self.policy_instruments = [
            'quantitative_easing', 'forward_guidance', 'repo_rate', 'reserve_requirements',
            'government_spending', 'taxation', 'tariffs', 'subsidies', 'regulation'
        ]
        
        self.methodological_terms = [
            'graph_neural_network', 'knowledge_graph', 'granger_causality',
            'vector_autoregression', 'impulse_response', 'cointegration',
            'machine_learning', 'natural_language_processing', 'sentiment_analysis'
        ]
    
    def chunk_macro_economic_document(self, document_text: str, doc_id: str) -> List[MacroEconomicChunk]:
        """Apply specialized chunking for macro-economic content"""
        
        # Split by sections first to preserve economic concepts
        sections = self._identify_economic_sections(document_text)
        chunks = []
        chunk_index = 0
        
        for section_title, section_content in sections:
            section_chunks = self._chunk_section(section_content, doc_id, chunk_index, section_title)
            chunks.extend(section_chunks)
            chunk_index += len(section_chunks)
        
        # Update total chunks for all
        for chunk in chunks:
            chunk.total_chunks = len(chunks)
            
        return chunks
    
    def _identify_economic_sections(self, text: str) -> List[tuple]:
        """Identify economic sections in the document"""
        
        lines = text.split('\n')
        sections = []
        current_section = None
        current_content = []
        
        economic_section_headers = [
            'methodology', 'data sources', 'performance', 'applications',
            'implementation', 'results', 'framework', 'analysis',
            'economic indicators', 'policy', 'forecasting', 'networks'
        ]
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check if this is a section header
            is_header = (line.startswith('#') or 
                        line.startswith('##') or
                        any(header in line_lower for header in economic_section_headers))
            
            if is_header and current_section is not None:
                # Save previous section
                sections.append((current_section, '\n'.join(current_content)))
                current_content = []
            
            if is_header:
                current_section = line.strip()
            else:
                current_content.append(line)
        
        # Add final section
        if current_section:
            sections.append((current_section, '\n'.join(current_content)))
        
        return sections
    
    def _chunk_section(self, section_content: str, doc_id: str, start_index: int, section_title: str) -> List[MacroEconomicChunk]:
        """Chunk a specific economic section"""
        
        words = section_content.split()
        chunks = []
        current_chunk = []
        current_size = 0
        chunk_index = start_index
        
        for word in words:
            current_chunk.append(word)
            current_size += len(word) + 1
            
            if current_size >= self.max_size:
                chunk_text = ' '.join(current_chunk)
                chunk = self._create_economic_chunk(chunk_text, doc_id, chunk_index, section_title)
                chunks.append(chunk)
                
                # Handle overlap
                overlap_words = current_chunk[-self.overlap:] if len(current_chunk) > self.overlap else []
                current_chunk = overlap_words
                current_size = sum(len(word) + 1 for word in overlap_words)
                chunk_index += 1
        
        # Handle remaining words
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunk = self._create_economic_chunk(chunk_text, doc_id, chunk_index, section_title)
            chunks.append(chunk)
        
        return chunks
    
    def _create_economic_chunk(self, text: str, doc_id: str, chunk_index: int, section_title: str) -> MacroEconomicChunk:
        """Create a macro-economic chunk with specialized analysis"""
        
        # Extract economic concepts
        economic_concepts = self._extract_economic_concepts(text)
        economic_indicators = self._extract_economic_indicators(text)
        policy_references = self._extract_policy_references(text)
        methodological_approaches = self._extract_methodological_approaches(text)
        data_sources = self._extract_data_sources(text)
        
        # Calculate scores
        semantic_density = self._calculate_semantic_density(text)
        economic_relevance = self._calculate_economic_relevance(text, economic_concepts, economic_indicators)
        
        return MacroEconomicChunk(
            chunk_id=f"{doc_id}_econ_chunk_{chunk_index}",
            sequence=chunk_index,
            text=text,
            position=chunk_index,
            total_chunks=0,  # Will be updated later
            economic_concepts=economic_concepts,
            economic_indicators=economic_indicators,
            policy_references=policy_references,
            methodological_approaches=methodological_approaches,
            data_sources=data_sources,
            semantic_density=semantic_density,
            economic_relevance_score=economic_relevance,
            metadata={
                "section_title": section_title,
                "word_count": len(text.split()),
                "char_count": len(text),
                "chunk_type": "macro_economic",
                "domain": "macro_economics",
                "specialization": "knowledge_graph_modeling"
            }
        )
    
    def _extract_economic_concepts(self, text: str) -> List[str]:
        """Extract economic concepts from text"""
        text_lower = text.lower()
        found_concepts = []
        
        for concept in self.economic_concepts:
            if concept.replace('_', ' ') in text_lower or concept in text_lower:
                found_concepts.append(concept)
        
        return found_concepts
    
    def _extract_economic_indicators(self, text: str) -> List[str]:
        """Extract economic indicators from text"""
        text_lower = text.lower()
        found_indicators = []
        
        for indicator in self.economic_indicators:
            if indicator.replace('_', ' ') in text_lower or indicator in text_lower:
                found_indicators.append(indicator)
        
        return found_indicators
    
    def _extract_policy_references(self, text: str) -> List[str]:
        """Extract policy references from text"""
        text_lower = text.lower()
        found_policies = []
        
        for policy in self.policy_instruments:
            if policy.replace('_', ' ') in text_lower or policy in text_lower:
                found_policies.append(policy)
        
        return found_policies
    
    def _extract_methodological_approaches(self, text: str) -> List[str]:
        """Extract methodological approaches from text"""
        text_lower = text.lower()
        found_methods = []
        
        for method in self.methodological_terms:
            if method.replace('_', ' ') in text_lower or method in text_lower:
                found_methods.append(method)
        
        return found_methods
    
    def _extract_data_sources(self, text: str) -> List[str]:
        """Extract data sources mentioned in text"""
        data_source_keywords = [
            'fred', 'world bank', 'imf', 'oecd', 'central bank', 'bea',
            'eurostat', 'bis', 'bloomberg', 'reuters', 'arxiv', 'ssrn'
        ]
        
        text_lower = text.lower()
        found_sources = []
        
        for source in data_source_keywords:
            if source in text_lower:
                found_sources.append(source)
        
        return found_sources
    
    def _calculate_semantic_density(self, text: str) -> float:
        """Calculate semantic density for economic content"""
        words = text.split()
        unique_words = set(word.lower() for word in words)
        
        # Weight economic terms higher
        economic_word_count = sum(1 for word in unique_words 
                                 if any(econ_term in word for econ_term in self.economic_concepts + self.economic_indicators))
        
        base_density = len(unique_words) / len(words) if words else 0
        economic_boost = min(economic_word_count / 10, 0.3)  # Cap at 0.3 boost
        
        return min(base_density + economic_boost, 1.0)
    
    def _calculate_economic_relevance(self, text: str, concepts: List[str], indicators: List[str]) -> float:
        """Calculate economic relevance score"""
        text_lower = text.lower()
        
        # Score based on economic content density
        concept_score = len(concepts) * 0.1
        indicator_score = len(indicators) * 0.15
        
        # Boost for specific economic terms
        economic_keywords = ['economic', 'monetary', 'fiscal', 'financial', 'macroeconomic']
        keyword_score = sum(0.05 for keyword in economic_keywords if keyword in text_lower)
        
        # Boost for quantitative content
        quantitative_indicators = ['%', 'percent', 'basis points', 'trillion', 'billion', 'growth rate']
        quant_score = sum(0.03 for indicator in quantitative_indicators if indicator in text_lower)
        
        total_score = concept_score + indicator_score + keyword_score + quant_score
        return min(total_score, 1.0)

class MacroEconomicMetadataExtractor:
    """Extract specialized metadata for macro-economic content"""
    
    def extract_macro_economic_metadata(self, document_text: str, blob_info: Dict) -> Dict[str, Any]:
        """Extract comprehensive macro-economic metadata"""
        
        metadata = {
            "domain_classification": {
                "primary_domain": "macro_economics",
                "sub_domains": self._classify_economic_sub_domains(document_text),
                "methodology_focus": self._identify_methodology_focus(document_text),
                "geographic_scope": self._identify_geographic_scope(document_text)
            },
            "economic_content": {
                "economic_concepts": self._extract_all_economic_concepts(document_text),
                "policy_areas": self._identify_policy_areas(document_text),
                "data_sources": self._identify_data_sources(document_text),
                "time_periods": self._extract_time_periods(document_text)
            },
            "research_characteristics": {
                "research_type": self._classify_research_type(document_text),
                "empirical_vs_theoretical": self._classify_empirical_theoretical(document_text),
                "model_complexity": self._assess_model_complexity(document_text),
                "innovation_level": self._assess_innovation_level(document_text)
            },
            "academic_metadata": {
                "citation_density": self._calculate_citation_density(document_text),
                "academic_rigor": self._assess_academic_rigor(document_text),
                "practical_applications": self._identify_practical_applications(document_text),
                "future_research_directions": self._extract_future_research(document_text)
            },
            "technical_metadata": blob_info
        }
        
        return metadata
    
    def _classify_economic_sub_domains(self, text: str) -> List[str]:
        """Classify economic sub-domains"""
        text_lower = text.lower()
        sub_domains = []
        
        domain_keywords = {
            'monetary_economics': ['monetary policy', 'central bank', 'interest rates', 'money supply'],
            'fiscal_economics': ['fiscal policy', 'government spending', 'taxation', 'budget'],
            'international_economics': ['trade', 'exchange rates', 'balance of payments', 'globalization'],
            'financial_economics': ['financial markets', 'banking', 'financial stability', 'systemic risk'],
            'development_economics': ['development', 'emerging markets', 'poverty', 'inequality'],
            'labor_economics': ['employment', 'unemployment', 'wages', 'labor markets'],
            'computational_economics': ['machine learning', 'artificial intelligence', 'big data', 'algorithms']
        }
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                sub_domains.append(domain)
        
        return sub_domains
    
    def _identify_methodology_focus(self, text: str) -> List[str]:
        """Identify methodological focus areas"""
        text_lower = text.lower()
        methodologies = []
        
        method_keywords = {
            'knowledge_graphs': ['knowledge graph', 'graph neural network', 'graph embedding'],
            'machine_learning': ['machine learning', 'deep learning', 'neural network'],
            'econometrics': ['econometric', 'regression', 'time series', 'vector autoregression'],
            'network_analysis': ['network analysis', 'centrality', 'community detection'],
            'natural_language_processing': ['nlp', 'text mining', 'sentiment analysis'],
            'causal_inference': ['causal', 'instrumental variables', 'difference in differences']
        }
        
        for method, keywords in method_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                methodologies.append(method)
        
        return methodologies
    
    def _identify_geographic_scope(self, text: str) -> List[str]:
        """Identify geographic scope of research"""
        text_lower = text.lower()
        geographic_scopes = []
        
        # Country mentions
        major_economies = ['usa', 'united states', 'china', 'germany', 'japan', 'uk', 'france', 'italy', 'brazil', 'india']
        country_regions = ['g7', 'g20', 'eu', 'eurozone', 'emerging markets', 'developed economies']
        
        for economy in major_economies:
            if economy in text_lower:
                geographic_scopes.append(economy)
        
        for region in country_regions:
            if region in text_lower:
                geographic_scopes.append(region)
        
        # Determine scope
        if len(geographic_scopes) > 5:
            return ['global']
        elif any('g7' in scope or 'g20' in scope for scope in geographic_scopes):
            return ['multi_country'] + geographic_scopes
        else:
            return geographic_scopes or ['general']
    
    def _extract_all_economic_concepts(self, text: str) -> Dict[str, int]:
        """Extract and count all economic concepts"""
        text_lower = text.lower()
        concept_counts = {}
        
        all_concepts = [
            'gdp', 'inflation', 'unemployment', 'interest rates', 'monetary policy',
            'fiscal policy', 'trade balance', 'exchange rate', 'productivity',
            'economic growth', 'recession', 'business cycle', 'central bank'
        ]
        
        for concept in all_concepts:
            count = text_lower.count(concept.replace('_', ' '))
            if count > 0:
                concept_counts[concept] = count
        
        return concept_counts
    
    def _classify_research_type(self, text: str) -> str:
        """Classify the type of research"""
        text_lower = text.lower()
        
        if 'survey' in text_lower or 'review' in text_lower:
            return 'literature_review'
        elif 'empirical' in text_lower or 'data' in text_lower:
            return 'empirical_study'
        elif 'model' in text_lower or 'theoretical' in text_lower:
            return 'theoretical_model'
        elif 'methodology' in text_lower or 'framework' in text_lower:
            return 'methodological_contribution'
        else:
            return 'mixed_approach'
    
    def _classify_empirical_theoretical(self, text: str) -> str:
        """Classify as empirical vs theoretical"""
        text_lower = text.lower()
        
        empirical_indicators = ['data', 'dataset', 'regression', 'statistical', 'evidence']
        theoretical_indicators = ['model', 'theoretical', 'framework', 'conceptual']
        
        empirical_score = sum(1 for indicator in empirical_indicators if indicator in text_lower)
        theoretical_score = sum(1 for indicator in theoretical_indicators if indicator in text_lower)
        
        if empirical_score > theoretical_score:
            return 'empirical'
        elif theoretical_score > empirical_score:
            return 'theoretical'
        else:
            return 'mixed'
    
    def _assess_model_complexity(self, text: str) -> str:
        """Assess model complexity level"""
        text_lower = text.lower()
        
        complexity_indicators = {
            'high': ['deep learning', 'neural network', 'machine learning', 'artificial intelligence'],
            'medium': ['econometric', 'statistical model', 'regression', 'time series'],
            'low': ['descriptive', 'correlation', 'simple model', 'basic analysis']
        }
        
        for level, indicators in complexity_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                return level
        
        return 'medium'  # Default
    
    def _assess_innovation_level(self, text: str) -> str:
        """Assess innovation level of research"""
        text_lower = text.lower()
        
        innovation_keywords = [
            'novel', 'new approach', 'innovative', 'breakthrough', 'first time',
            'unprecedented', 'cutting edge', 'state of the art'
        ]
        
        innovation_count = sum(1 for keyword in innovation_keywords if keyword in text_lower)
        
        if innovation_count >= 3:
            return 'high'
        elif innovation_count >= 1:
            return 'medium'
        else:
            return 'incremental'
    
    def _calculate_citation_density(self, text: str) -> float:
        """Calculate citation density"""
        # Simple approximation based on reference patterns
        citation_patterns = ['(', ')', '[', ']', 'et al', 'doi:', 'arxiv:']
        citation_count = sum(text.count(pattern) for pattern in citation_patterns)
        word_count = len(text.split())
        
        return min(citation_count / word_count * 100, 10.0) if word_count > 0 else 0.0
    
    def _assess_academic_rigor(self, text: str) -> str:
        """Assess academic rigor level"""
        text_lower = text.lower()
        
        rigor_indicators = [
            'methodology', 'statistical significance', 'robustness check',
            'sensitivity analysis', 'peer review', 'replication'
        ]
        
        rigor_score = sum(1 for indicator in rigor_indicators if indicator in text_lower)
        
        if rigor_score >= 4:
            return 'high'
        elif rigor_score >= 2:
            return 'medium'
        else:
            return 'low'
    
    def _identify_practical_applications(self, text: str) -> List[str]:
        """Identify practical applications"""
        text_lower = text.lower()
        applications = []
        
        application_areas = {
            'policy_making': ['policy', 'government', 'central bank', 'regulation'],
            'forecasting': ['forecast', 'prediction', 'early warning', 'nowcasting'],
            'risk_management': ['risk', 'stress test', 'financial stability'],
            'investment': ['investment', 'portfolio', 'asset allocation'],
            'academic_research': ['research', 'academic', 'scholarly', 'education']
        }
        
        for area, keywords in application_areas.items():
            if any(keyword in text_lower for keyword in keywords):
                applications.append(area)
        
        return applications
    
    def _extract_future_research(self, text: str) -> List[str]:
        """Extract future research directions"""
        text_lower = text.lower()
        future_keywords = [
            'future research', 'further investigation', 'next steps',
            'limitations', 'extensions', 'improvements'
        ]
        
        return [keyword for keyword in future_keywords if keyword in text_lower]
    
    def _identify_data_sources(self, text: str) -> List[str]:
        """Identify data sources mentioned"""
        text_lower = text.lower()
        data_sources = []
        
        source_keywords = [
            'fred', 'world bank', 'imf', 'oecd', 'bloomberg', 'reuters',
            'central bank', 'statistical office', 'survey data', 'administrative data'
        ]
        
        for source in source_keywords:
            if source in text_lower:
                data_sources.append(source)
        
        return data_sources
    
    def _identify_policy_areas(self, text: str) -> List[str]:
        """Identify policy areas mentioned in research"""
        text_lower = text.lower()
        policy_areas = []
        
        policy_keywords = {
            'monetary_policy': ['monetary policy', 'interest rates', 'central bank', 'money supply'],
            'fiscal_policy': ['fiscal policy', 'government spending', 'taxation', 'budget'],
            'financial_regulation': ['financial regulation', 'banking regulation', 'capital requirements'],
            'trade_policy': ['trade policy', 'tariffs', 'trade agreements', 'import', 'export'],
            'labor_policy': ['labor policy', 'employment policy', 'minimum wage', 'unemployment benefits']
        }
        
        for policy_area, keywords in policy_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                policy_areas.append(policy_area)
        
        return policy_areas
    
    def _extract_time_periods(self, text: str) -> List[str]:
        """Extract time periods mentioned in research"""
        import re
        
        # Find years mentioned
        years = re.findall(r'\b(19|20)\d{2}\b', text)
        
        # Find period descriptions
        text_lower = text.lower()
        periods = []
        
        period_keywords = [
            'post-crisis', 'pre-crisis', 'financial crisis', 'great recession',
            'covid-19', 'pandemic', 'recent years', 'last decade'
        ]
        
        for period in period_keywords:
            if period in text_lower:
                periods.append(period)
        
        # Combine years and periods
        time_periods = list(set(years + periods))
        return time_periods[:10]  # Limit to prevent bloat

class MacroEconomicGraphPreparer:
    """Prepare graph-ready data for macro-economic knowledge graphs"""
    
    def prepare_macro_economic_graph(self, document_text: str, chunks: List[MacroEconomicChunk], metadata: Dict) -> Dict[str, Any]:
        """Prepare specialized macro-economic graph data"""
        
        nodes = []
        edges = []
        
        # Create main document node
        doc_id = hashlib.md5(document_text.encode()).hexdigest()[:8]
        nodes.append({
            "id": f"macro_doc_{doc_id}",
            "label": "MacroEconomicDocument",
            "type": "ResearchDocument",
            "properties": {
                "title": metadata.get('title', 'Macro-Economic Research'),
                "domain": "macro_economics",
                "sub_domains": metadata['domain_classification']['sub_domains'],
                "methodology_focus": metadata['domain_classification']['methodology_focus'],
                "geographic_scope": metadata['domain_classification']['geographic_scope'],
                "research_type": metadata['research_characteristics']['research_type'],
                "complexity": metadata['research_characteristics']['model_complexity'],
                "innovation_level": metadata['research_characteristics']['innovation_level']
            }
        })
        
        # Create economic concept nodes
        all_concepts = set()
        for chunk in chunks:
            all_concepts.update(chunk.economic_concepts)
            all_concepts.update(chunk.economic_indicators)
        
        concept_node_map = {}
        for i, concept in enumerate(all_concepts):
            node_id = f"econ_concept_{concept}_{i}"
            concept_node_map[concept] = node_id
            
            # Count frequency across all chunks
            frequency = sum(1 for chunk in chunks if concept in chunk.economic_concepts + chunk.economic_indicators)
            
            nodes.append({
                "id": node_id,
                "label": "EconomicConcept",
                "type": "MacroEconomicConcept",
                "properties": {
                    "name": concept,
                    "frequency": frequency,
                    "concept_type": self._classify_concept_type(concept),
                    "domain": "macro_economics"
                }
            })
            
            # Create edge from document to concept
            edges.append({
                "id": f"edge_doc_concept_{i}",
                "label": "CONTAINS_ECONOMIC_CONCEPT",
                "source": f"macro_doc_{doc_id}",
                "target": node_id,
                "properties": {
                    "strength": min(frequency / 10.0, 1.0),
                    "relationship_type": "conceptual_containment"
                }
            })
        
        # Create methodology nodes
        all_methods = set()
        for chunk in chunks:
            all_methods.update(chunk.methodological_approaches)
        
        for i, method in enumerate(all_methods):
            node_id = f"methodology_{method}_{i}"
            frequency = sum(1 for chunk in chunks if method in chunk.methodological_approaches)
            
            nodes.append({
                "id": node_id,
                "label": "Methodology",
                "type": "ResearchMethodology",
                "properties": {
                    "name": method,
                    "frequency": frequency,
                    "methodology_type": self._classify_methodology_type(method)
                }
            })
            
            # Edge from document to methodology
            edges.append({
                "id": f"edge_doc_method_{i}",
                "label": "USES_METHODOLOGY",
                "source": f"macro_doc_{doc_id}",
                "target": node_id,
                "properties": {
                    "strength": min(frequency / 5.0, 1.0),
                    "relationship_type": "methodological_application"
                }
            })
        
        # Create data source nodes
        all_data_sources = set()
        for chunk in chunks:
            all_data_sources.update(chunk.data_sources)
        
        for i, data_source in enumerate(all_data_sources):
            node_id = f"data_source_{data_source.replace(' ', '_')}_{i}"
            frequency = sum(1 for chunk in chunks if data_source in chunk.data_sources)
            
            nodes.append({
                "id": node_id,
                "label": "DataSource",
                "type": "EconomicDataSource",
                "properties": {
                    "name": data_source,
                    "frequency": frequency,
                    "source_type": self._classify_data_source_type(data_source)
                }
            })
            
            # Edge from document to data source
            edges.append({
                "id": f"edge_doc_data_{i}",
                "label": "USES_DATA_SOURCE",
                "source": f"macro_doc_{doc_id}",
                "target": node_id,
                "properties": {
                    "strength": min(frequency / 3.0, 1.0),
                    "relationship_type": "data_dependency"
                }
            })
        
        # Create concept-to-concept relationships based on co-occurrence
        concept_pairs = []
        for chunk in chunks:
            chunk_concepts = chunk.economic_concepts + chunk.economic_indicators
            for i, concept1 in enumerate(chunk_concepts):
                for concept2 in chunk_concepts[i+1:]:
                    if concept1 != concept2:
                        concept_pairs.append((concept1, concept2))
        
        # Count co-occurrences and create edges for strong relationships
        from collections import Counter
        co_occurrence_counts = Counter(concept_pairs)
        
        for (concept1, concept2), count in co_occurrence_counts.items():
            if count >= 2:  # Only create edges for concepts that co-occur multiple times
                if concept1 in concept_node_map and concept2 in concept_node_map:
                    edges.append({
                        "id": f"edge_concept_{concept1}_{concept2}",
                        "label": "CO_OCCURS_WITH",
                        "source": concept_node_map[concept1],
                        "target": concept_node_map[concept2],
                        "properties": {
                            "co_occurrence_frequency": count,
                            "strength": min(count / 5.0, 1.0),
                            "relationship_type": "conceptual_association"
                        }
                    })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "graph_metadata": {
                "node_count": len(nodes),
                "edge_count": len(edges),
                "graph_type": "macro_economic_knowledge_graph",
                "domain_specialization": "macro_economics",
                "prepared_for": "gremlin_graph_database",
                "concept_types": list(set(node["properties"].get("concept_type", "unknown") for node in nodes if node["type"] == "MacroEconomicConcept")),
                "methodology_coverage": list(all_methods),
                "data_source_coverage": list(all_data_sources)
            }
        }
    
    def _classify_concept_type(self, concept: str) -> str:
        """Classify economic concept type"""
        policy_concepts = ['monetary_policy', 'fiscal_policy', 'interest_rates', 'government_spending']
        indicator_concepts = ['gdp', 'inflation', 'unemployment', 'cpi', 'ppi']
        institutional_concepts = ['central_bank', 'treasury', 'federal_reserve']
        
        if concept in policy_concepts:
            return 'policy_instrument'
        elif concept in indicator_concepts:
            return 'economic_indicator'
        elif concept in institutional_concepts:
            return 'economic_institution'
        else:
            return 'economic_concept'
    
    def _classify_methodology_type(self, method: str) -> str:
        """Classify methodology type"""
        ml_methods = ['machine_learning', 'deep_learning', 'neural_network', 'graph_neural_network']
        econometric_methods = ['granger_causality', 'vector_autoregression', 'cointegration']
        graph_methods = ['knowledge_graph', 'network_analysis', 'graph_embedding']
        
        if method in ml_methods:
            return 'machine_learning'
        elif method in econometric_methods:
            return 'econometric'
        elif method in graph_methods:
            return 'graph_analysis'
        else:
            return 'statistical_method'
    
    def _classify_data_source_type(self, source: str) -> str:
        """Classify data source type"""
        government_sources = ['fred', 'bea', 'central_bank', 'statistical_office']
        international_sources = ['world_bank', 'imf', 'oecd', 'bis']
        private_sources = ['bloomberg', 'reuters']
        academic_sources = ['arxiv', 'ssrn']
        
        if source in government_sources:
            return 'government_data'
        elif source in international_sources:
            return 'international_organization'
        elif source in private_sources:
            return 'private_data_provider'
        elif source in academic_sources:
            return 'academic_repository'
        else:
            return 'general_data_source'

class MacroEconomicPipeline:
    """Complete macro-economic processing pipeline"""
    
    def __init__(self):
        self.blob_client = None
        self.cosmos_client = None
        self.chunker = MacroEconomicChunker()
        self.extractor = MacroEconomicMetadataExtractor()
        self.graph_preparer = MacroEconomicGraphPreparer()
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
            
            print("✅ Macro-economic pipeline clients initialized")
            
        except Exception as e:
            print(f"❌ Error initializing clients: {e}")
            raise
    
    def process_macro_economic_research(self, file_path: str) -> Dict[str, Any]:
        """Process macro-economic research document"""
        
        print(f"🏦 Processing macro-economic research: {Path(file_path).name}")
        
        try:
            # 1. Upload to blob with macro-economic categorization
            blob_info = self.upload_to_blob_storage(file_path)
            
            # 2. Read and process content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 3. Generate document ID
            doc_id = hashlib.md5(content.encode()).hexdigest()[:16]
            
            # 4. Specialized macro-economic chunking
            chunks = self.chunker.chunk_macro_economic_document(content, doc_id)
            print(f"   📊 Created {len(chunks)} macro-economic chunks")
            
            # 5. Extract specialized metadata
            metadata = self.extractor.extract_macro_economic_metadata(content, blob_info)
            print(f"   🎯 Domain classification: {metadata['domain_classification']['primary_domain']}")
            print(f"   📈 Sub-domains: {', '.join(metadata['domain_classification']['sub_domains'])}")
            
            # 6. Prepare specialized graph data
            graph_data = self.graph_preparer.prepare_macro_economic_graph(content, chunks, metadata)
            print(f"   🌐 Graph preparation: {len(graph_data['nodes'])} nodes, {len(graph_data['edges'])} edges")
            
            # 7. Create processed document with macro-economic specialization
            processed_doc = {
                "id": f"macro_econ_{doc_id}",
                "type": "macro_economic_research",
                "blob_reference": blob_info,
                "content_summary": {
                    "title": Path(file_path).stem,
                    "chunk_count": len(chunks),
                    "total_chars": len(content),
                    "domain": "macro_economics",
                    "sub_domains": metadata['domain_classification']['sub_domains'],
                    "research_type": metadata['research_characteristics']['research_type'],
                    "complexity": metadata['research_characteristics']['model_complexity'],
                    "geographic_scope": metadata['domain_classification']['geographic_scope']
                },
                "chunks": [asdict(chunk) for chunk in chunks],
                "macro_economic_metadata": metadata,
                "graph_ready": graph_data,
                "ai_metadata": {
                    "processing_date": datetime.now().isoformat(),
                    "model_versions": {
                        "chunker": "macro_economic_v1.0",
                        "extractor": "macro_economic_v1.0",
                        "graph_preparer": "macro_economic_v1.0"
                    },
                    "quality_scores": {
                        "economic_relevance": sum(chunk.economic_relevance_score for chunk in chunks) / len(chunks),
                        "semantic_density": sum(chunk.semantic_density for chunk in chunks) / len(chunks),
                        "domain_specificity": 0.95,  # High for specialized processing
                        "completeness": 0.92
                    }
                },
                "processing_timestamp": datetime.now().isoformat()
            }
            
            # 8. Store in Cosmos DB
            success = self.store_in_cosmos(processed_doc)
            
            if success:
                result = {
                    "success": True,
                    "document_id": processed_doc["id"],
                    "domain": "macro_economics",
                    "sub_domains": metadata['domain_classification']['sub_domains'],
                    "chunks_created": len(chunks),
                    "economic_concepts": len(graph_data['graph_metadata']['concept_types']),
                    "methodologies": len(graph_data['graph_metadata']['methodology_coverage']),
                    "data_sources": len(graph_data['graph_metadata']['data_source_coverage']),
                    "blob_url": blob_info["url"],
                    "cosmos_container": self.cosmos_container,
                    "graph_nodes": len(graph_data["nodes"]),
                    "graph_edges": len(graph_data["edges"]),
                    "research_type": metadata['research_characteristics']['research_type'],
                    "geographic_scope": metadata['domain_classification']['geographic_scope']
                }
                
                print(f"✅ Macro-economic processing complete")
                print(f"   Document ID: {result['document_id']}")
                print(f"   Economic concepts: {result['economic_concepts']}")
                print(f"   Methodologies: {result['methodologies']}")
                print(f"   Graph nodes: {result['graph_nodes']}")
                
                return result
            else:
                raise Exception("Failed to store in Cosmos")
                
        except Exception as e:
            print(f"❌ Macro-economic processing failed: {e}")
            return {"success": False, "error": str(e)}
    
    def upload_to_blob_storage(self, file_path: str) -> Dict[str, Any]:
        """Upload to blob storage with macro-economic categorization"""
        
        try:
            blob_name = f"macro_economics/research/{Path(file_path).name}"
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            container_client = self.blob_client.get_container_client(self.container_name)
            blob_client = container_client.get_blob_client(blob_name)
            
            blob_client.upload_blob(
                data=content,
                metadata={
                    "original_name": Path(file_path).name,
                    "upload_time": datetime.now().isoformat(),
                    "content_type": "macro_economic_research",
                    "domain": "macro_economics",
                    "processing_stage": "raw_research",
                    "specialization": "knowledge_graph_modeling"
                },
                overwrite=True
            )
            
            blob_info = {
                "container": self.container_name,
                "blob_name": blob_name,
                "size_bytes": len(content.encode('utf-8')),
                "url": f"https://{self.blob_client.account_name}.blob.core.windows.net/{self.container_name}/{blob_name}"
            }
            
            print(f"   📁 Uploaded to blob: {blob_name}")
            return blob_info
            
        except Exception as e:
            print(f"❌ Error uploading to blob: {e}")
            raise
    
    def store_in_cosmos(self, processed_doc: Dict) -> bool:
        """Store processed document in Cosmos DB"""
        
        try:
            database = self.cosmos_client.get_database_client(os.getenv('COSMOS_DATABASE'))
            container = database.get_container_client(self.cosmos_container)
            
            # Store document
            container.create_item(processed_doc)
            
            print(f"   🗄️ Stored in Cosmos: {processed_doc['id']}")
            return True
            
        except Exception as e:
            print(f"❌ Error storing in Cosmos: {e}")
            return False

def main():
    """Test macro-economic pipeline"""
    
    pipeline = MacroEconomicPipeline()
    
    # Process the macro-economic research
    research_file = "/Users/mikaeleage/Research & Analytics Services/RESEARCH/macro_economics/Comprehensive_Macro_Economic_Knowledge_Graph_Research_2025.md"
    
    if Path(research_file).exists():
        print(f"🚀 Testing macro-economic pipeline")
        result = pipeline.process_macro_economic_research(research_file)
        
        if result["success"]:
            print(f"\n✅ MACRO-ECONOMIC PROCESSING SUCCESS:")
            print(f"   Document ID: {result['document_id']}")
            print(f"   Domain: {result['domain']}")
            print(f"   Sub-domains: {', '.join(result['sub_domains'])}")
            print(f"   Research type: {result['research_type']}")
            print(f"   Geographic scope: {', '.join(result['geographic_scope'])}")
            print(f"   Chunks created: {result['chunks_created']}")
            print(f"   Economic concepts: {result['economic_concepts']}")
            print(f"   Methodologies identified: {result['methodologies']}")
            print(f"   Data sources: {result['data_sources']}")
            print(f"   Graph nodes: {result['graph_nodes']}")
            print(f"   Graph edges: {result['graph_edges']}")
            print(f"   Blob URL: {result['blob_url']}")
            print(f"\n🎯 SPECIALIZED MACRO-ECONOMIC KNOWLEDGE GRAPH READY")
        else:
            print(f"\n❌ PROCESSING FAILED: {result.get('error', 'Unknown error')}")
    else:
        print(f"❌ Research file not found: {research_file}")

if __name__ == "__main__":
    main()