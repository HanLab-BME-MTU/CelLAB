"""
cintelia Context Builder
=======================

Intelligently retrieves relevant documentation for user queries.

This module:
- Searches documentation based on keywords
- Ranks results by relevance
- Builds context strings for LLM prompts
- Handles different context types (IMMUNIA, FASTIA, error, general)
- Falls back gracefully when documentation is missing

The context builder uses simple keyword matching (no embeddings needed)
to keep the system lightweight and CPU-friendly.

Author: Han Lab - Mechanobiology Dry Lab
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from collections import defaultdict

# Get paths
cintelia_DIR = Path(__file__).parent
DOCS_DIR = cintelia_DIR / "docs"


# ============================================================================
# CONTEXT BUILDER CLASS
# ============================================================================

class ContextBuilder:
    """
    Build relevant context for cintelia queries
    
    Uses keyword-based retrieval to find relevant documentation
    without requiring embeddings or vector databases.
    
    Usage:
        builder = ContextBuilder()
        context = builder.build_context(
            query="How do I fix NK cell segmentation?",
            context_type='immunia'
        )
    """
    
    def __init__(self, docs_dir: Optional[Path] = None):
        """
        Initialize context builder
        
        Args:
            docs_dir: Path to documentation directory (default: backend/cintelia/docs)
        """
        
        self.docs_dir = docs_dir if docs_dir else DOCS_DIR
        
        # Storage for loaded documentation
        self.immunia_docs = None
        self.immunia_params = None
        self.immunia_index = None
        
        self.fastia_docs = None
        self.fastia_params = None
        self.fastia_index = None
        
        self.general_docs = None
        
        # Check if docs exist
        self.immunia_available = self._check_docs_exist('immunia')
        self.fastia_available = self._check_docs_exist('fastia')
        self.general_available = (self.docs_dir / 'general_docs.json').exists()
        
        # Load documentation on first use (lazy loading)
        self._loaded = {
            'immunia': False,
            'fastia': False,
            'general': False
        }
    
    def _check_docs_exist(self, pipeline: str) -> bool:
        """Check if documentation files exist for a pipeline"""
        required_files = [
            f"{pipeline}_docs.json",
            f"{pipeline}_params.json",
            f"{pipeline}_index.json"
        ]
        return all((self.docs_dir / f).exists() for f in required_files)
    
    def _load_documentation(self, pipeline: str):
        """
        Load documentation files for a pipeline
        
        Args:
            pipeline: 'immunia', 'fastia', or 'general'
        """
        
        if self._loaded[pipeline]:
            return  # Already loaded
        
        try:
            if pipeline == 'immunia' and self.immunia_available:
                with open(self.docs_dir / 'immunia_docs.json', 'r', encoding='utf-8') as f:
                    self.immunia_docs = json.load(f)
                with open(self.docs_dir / 'immunia_params.json', 'r', encoding='utf-8') as f:
                    self.immunia_params = json.load(f)
                with open(self.docs_dir / 'immunia_index.json', 'r', encoding='utf-8') as f:
                    self.immunia_index = json.load(f)
                self._loaded['immunia'] = True
            
            elif pipeline == 'fastia' and self.fastia_available:
                with open(self.docs_dir / 'fastia_docs.json', 'r', encoding='utf-8') as f:
                    self.fastia_docs = json.load(f)
                with open(self.docs_dir / 'fastia_params.json', 'r', encoding='utf-8') as f:
                    self.fastia_params = json.load(f)
                with open(self.docs_dir / 'fastia_index.json', 'r', encoding='utf-8') as f:
                    self.fastia_index = json.load(f)
                self._loaded['fastia'] = True
            
            elif pipeline == 'general' and self.general_available:
                with open(self.docs_dir / 'general_docs.json', 'r', encoding='utf-8') as f:
                    self.general_docs = json.load(f)
                self._loaded['general'] = True
        
        except Exception as e:
            print(f"Warning: Failed to load {pipeline} documentation: {e}")
    
    def build_context(
        self,
        query: str,
        context_type: str = 'general',
        max_sections: int = 3,
        max_length: int = 2000
    ) -> str:
        """
        Build relevant context for a query
        
        Args:
            query: User's question
            context_type: 'immunia', 'fastia', 'general', 'error'
            max_sections: Maximum number of doc sections to include
            max_length: Maximum total character length
        
        Returns:
            Formatted context string
        """
        
        # Handle 'error' context - treat as general with error keywords
        if context_type == 'error':
            query = f"error troubleshooting debugging {query}"
            context_type = 'general'
        
        # Load appropriate documentation
        if context_type == 'immunia':
            self._load_documentation('immunia')
            if not self.immunia_available:
                return self._get_fallback_context('immunia')
        elif context_type == 'fastia':
            self._load_documentation('fastia')
            if not self.fastia_available:
                return self._get_fallback_context('fastia')
        else:
            self._load_documentation('general')
        
        # Extract keywords from query
        keywords = self._extract_keywords(query)
        
        # Search for relevant sections
        relevant_sections = self._search_documentation(
            keywords,
            context_type,
            max_sections
        )
        
        # Build context string
        context = self._format_context(relevant_sections, max_length)
        
        return context
    
    def _extract_keywords(self, query: str) -> List[str]:
        """
        Extract meaningful keywords from query
        
        Args:
            query: User's question
        
        Returns:
            List of keywords (lowercase, 3+ chars)
        """
        
        # Convert to lowercase
        query_lower = query.lower()
        
        # Extract alphanumeric words (3+ chars)
        words = re.findall(r'\b\w{3,}\b', query_lower)
        
        # Remove common stop words
        stop_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all',
            'can', 'her', 'was', 'one', 'our', 'out', 'day', 'get',
            'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old',
            'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let',
            'put', 'say', 'she', 'too', 'use', 'what', 'when', 'with',
            'this', 'that', 'have', 'from', 'they', 'been', 'have',
            'does', 'doing', 'should', 'would', 'could'
        }
        
        keywords = [w for w in words if w not in stop_words]
        
        # Boost technical terms (keep duplicates for weighting)
        technical_terms = {
            'segmentation', 'segment', 'tracking', 'track', 'threshold',
            'parameter', 'detection', 'mask', 'cell', 'nk', 'tumor',
            'tissue', 'focal', 'adhesion', 'keller', 'segel', 'ccm',
            'granger', 'graph', 'network', 'analysis', 'error', 'failed',
            'velocity', 'msd', 'trajectory', 'gaussian', 'sigma'
        }
        
        # Add technical terms twice for higher weight
        boosted = []
        for kw in keywords:
            boosted.append(kw)
            if kw in technical_terms or any(tt in kw for tt in technical_terms):
                boosted.append(kw)  # Add twice for weighting
        
        return boosted
    
    def _search_documentation(
        self,
        keywords: List[str],
        context_type: str,
        max_sections: int
    ) -> List[Dict[str, str]]:
        """
        Search documentation for relevant sections
        
        Args:
            keywords: List of search keywords
            context_type: 'immunia', 'fastia', or 'general'
            max_sections: Maximum sections to return
        
        Returns:
            List of relevant doc sections with scores
        """
        
        sections = []
        
        if context_type == 'immunia' and self.immunia_docs:
            sections = self._search_pipeline_docs(
                keywords,
                self.immunia_docs,
                self.immunia_params,
                self.immunia_index
            )
        
        elif context_type == 'fastia' and self.fastia_docs:
            sections = self._search_pipeline_docs(
                keywords,
                self.fastia_docs,
                self.fastia_params,
                self.fastia_index
            )
        
        elif context_type == 'general' and self.general_docs:
            sections = self._search_general_docs(keywords, self.general_docs)
        
        # Sort by relevance score (descending)
        sections.sort(key=lambda x: x['score'], reverse=True)
        
        return sections[:max_sections]
    
    def _search_pipeline_docs(
        self,
        keywords: List[str],
        docs: Dict,
        params: Dict,
        index: Dict
    ) -> List[Dict[str, str]]:
        """Search pipeline documentation (IMMUNIA/FASTIA)"""
        
        sections = []
        
        # 1. Search parameter descriptions
        for param_key, param_info in params.items():
            score = self._calculate_match_score(
                keywords,
                [
                    param_info.get('name', ''),
                    param_info.get('description', ''),
                    param_info.get('function', ''),
                    param_info.get('method', ''),
                    param_info.get('module', '')
                ]
            )
            
            if score > 0:
                sections.append({
                    'type': 'parameter',
                    'title': f"Parameter: {param_info['name']}",
                    'content': self._format_parameter(param_info),
                    'score': score
                })
        
        # 2. Search function/method docstrings
        for module_name, module_doc in docs.get('modules', {}).items():
            # Search functions
            for func_name, func_doc in module_doc.get('functions', {}).items():
                docstring = func_doc.get('docstring', '')
                if docstring:
                    score = self._calculate_match_score(keywords, [func_name, docstring])
                    if score > 0:
                        sections.append({
                            'type': 'function',
                            'title': f"Function: {module_name}.{func_name}",
                            'content': docstring[:500],  # Truncate long docstrings
                            'score': score
                        })
            
            # Search class methods
            for class_name, class_doc in module_doc.get('classes', {}).items():
                for method_name, method_doc in class_doc.get('methods', {}).items():
                    docstring = method_doc.get('docstring', '')
                    if docstring and method_name not in ['__init__', '__repr__', '__str__']:
                        score = self._calculate_match_score(
                            keywords,
                            [class_name, method_name, docstring]
                        )
                        if score > 0:
                            sections.append({
                                'type': 'method',
                                'title': f"Method: {class_name}.{method_name}",
                                'content': docstring[:500],
                                'score': score
                            })
        
        return sections
    
    def _search_general_docs(self, keywords: List[str], docs: Dict) -> List[Dict[str, str]]:
        """Search general CELLAB documentation"""
        
        sections = []
        
        # Search CELLAB info
        cellab_info = docs.get('cellab', {})
        description = cellab_info.get('description', '')
        
        score = self._calculate_match_score(keywords, [description])
        if score > 0:
            sections.append({
                'type': 'general',
                'title': 'CELLAB Overview',
                'content': f"{description}\n\nPipelines: {', '.join(cellab_info.get('pipelines', {}).keys())}",
                'score': score
            })
        
        return sections
    
    def _calculate_match_score(self, keywords: List[str], texts: List[str]) -> float:
        """
        Calculate relevance score based on keyword matches
        
        Args:
            keywords: List of query keywords
            texts: List of text strings to search
        
        Returns:
            Relevance score (higher = more relevant)
        """
        
        if not keywords or not texts:
            return 0.0
        
        # Combine all text
        combined_text = ' '.join(str(t) for t in texts if t).lower()
        
        # Count keyword matches
        matches = sum(1 for kw in keywords if kw in combined_text)
        
        # Normalize by keyword count
        score = matches / len(keywords)
        
        return score
    
    def _format_parameter(self, param_info: Dict) -> str:
        """Format parameter information for context"""
        
        parts = []
        
        if param_info.get('description'):
            parts.append(f"Description: {param_info['description']}")
        
        if param_info.get('type'):
            parts.append(f"Type: {param_info['type']}")
        
        if param_info.get('default') is not None:
            parts.append(f"Default: {param_info['default']}")
        
        if param_info.get('function'):
            parts.append(f"Used in: {param_info['function']}")
        
        return '\n'.join(parts)
    
    def _format_context(self, sections: List[Dict[str, str]], max_length: int) -> str:
        """
        Format retrieved sections into context string
        
        Args:
            sections: List of relevant sections
            max_length: Maximum total character length
        
        Returns:
            Formatted context string
        """
        
        if not sections:
            return "No specific documentation found for this query."
        
        context_parts = []
        current_length = 0
        
        for section in sections:
            title = section['title']
            content = section['content']
            
            # Format section
            formatted = f"### {title}\n{content}\n"
            
            # Check length
            if current_length + len(formatted) > max_length:
                break
            
            context_parts.append(formatted)
            current_length += len(formatted)
        
        return '\n'.join(context_parts)
    
    def _get_fallback_context(self, pipeline: str) -> str:
        """
        Get fallback context when documentation is missing
        
        Args:
            pipeline: 'immunia' or 'fastia'
        
        Returns:
            Basic context string
        """
        
        if pipeline == 'immunia':
            return """### IMMUNIA Pipeline (Documentation Pending)

IMMUNIA is an immune cell analysis pipeline with these steps:
1. **Segmentation**: Segment dead cells, tumor, tissue, NK cells
2. **Tracking**: Track cell movement over time
3. **Signal Association**: Analyze relationships (CCM, Granger)
4. **Keller-Segel**: Model chemotaxis
5. **Particle Tracking**: Motion and spatial analysis
6. **Graph Theory**: Network analysis

Key parameters:
- Segmentation: `gaussian_sigma`, `threshold_factor`, `min_size`
- Tracking: `search_range`, `memory`, `min_frames`
- Analysis: `pixel_to_um`, `frame_to_min`

*Note: Run `python -m backend.cintelia.documentation_parser` to generate full documentation.*
"""
        
        elif pipeline == 'fastia':
            return """### FASTIA Pipeline (Documentation Pending)

FASTIA is a focal adhesion analysis pipeline with these steps:
1. **Detection**: Detect focal adhesions
2. **Tracking**: Track adhesion dynamics
3. **Analysis**: Compute statistics and turnover
4. **Classification**: Classify adhesion types

Key parameters:
- Detection: `sigma`, `threshold`, `min_area`, `max_area`
- Tracking: `max_displacement`, `memory`, `min_lifetime`

*Note: Run `python -m backend.cintelia.documentation_parser` to generate full documentation.*
"""
        
        return "Documentation not available for this pipeline."
    
    def get_parameter_info(
        self,
        parameter_name: str,
        context_type: str = 'immunia'
    ) -> Optional[Dict[str, str]]:
        """
        Get detailed information about a specific parameter
        
        Args:
            parameter_name: Name of parameter (e.g., 'gaussian_sigma')
            context_type: 'immunia' or 'fastia'
        
        Returns:
            Parameter info dict or None if not found
        """
        
        # Load documentation
        if context_type == 'immunia':
            self._load_documentation('immunia')
            params = self.immunia_params
        elif context_type == 'fastia':
            self._load_documentation('fastia')
            params = self.fastia_params
        else:
            return None
        
        if not params:
            return None
        
        # Search for parameter (case-insensitive partial match)
        param_lower = parameter_name.lower()
        
        for param_key, param_info in params.items():
            if param_lower in param_info['name'].lower():
                return param_info
        
        return None
    
    def list_available_parameters(self, context_type: str = 'immunia') -> List[str]:
        """
        List all available parameters for a pipeline
        
        Args:
            context_type: 'immunia' or 'fastia'
        
        Returns:
            List of parameter names
        """
        
        # Load documentation
        if context_type == 'immunia':
            self._load_documentation('immunia')
            params = self.immunia_params
        elif context_type == 'fastia':
            self._load_documentation('fastia')
            params = self.fastia_params
        else:
            return []
        
        if not params:
            return []
        
        return sorted(set(p['name'] for p in params.values()))


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def detect_context_type(query: str) -> str:
    """
    Auto-detect context type from query
    
    Args:
        query: User's question
    
    Returns:
        Context type: 'immunia', 'fastia', 'error', or 'general'
    """
    
    query_lower = query.lower()
    
    # Error context
    if any(word in query_lower for word in ['error', 'failed', 'crash', 'bug', 'fix', 'problem']):
        return 'error'
    
    # IMMUNIA context
    immunia_keywords = [
        'immunia', 'immune', 'nk cell', 'tumor', 'tissue', 'keller',
        'segel', 'chemotaxis', 'ccm', 'granger', 'segmentation',
        'tracking', 'trajectory', 'particle'
    ]
    if any(word in query_lower for word in immunia_keywords):
        return 'immunia'
    
    # FASTIA context
    fastia_keywords = [
        'fastia', 'focal adhesion', 'adhesion', 'fa', 'detection',
        'turnover', 'assembly', 'disassembly'
    ]
    if any(word in query_lower for word in fastia_keywords):
        return 'fastia'
    
    # Default to general
    return 'general'


# ============================================================================
# METADATA
# ============================================================================

__all__ = [
    'ContextBuilder',
    'detect_context_type'
]
