"""
cintelia Documentation Parser
=============================

Automatically extracts documentation from IMMUNIA and FASTIA codebases.

This module:
- Parses Python docstrings from pipeline modules
- Extracts function signatures and parameters
- Builds searchable documentation database
- Exports to JSON for cintelia context building

The parser handles:
- Module-level docstrings
- Class docstrings
- Function/method docstrings
- Parameter descriptions from docstrings
- Code comments (optional)

Author: Han Lab - Mechanobiology Dry Lab
"""

import ast
import json
import inspect
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import re
import sys

# Add backend to path for imports
BACKEND_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BACKEND_DIR))

# ============================================================================
# DOCUMENTATION PARSER CLASS
# ============================================================================

class DocumentationParser:
    """
    Parse Python modules to extract documentation
    
    Extracts:
    - Module docstrings
    - Class definitions and docstrings
    - Function signatures and docstrings
    - Parameter descriptions
    - Default values
    
    Usage:
        parser = DocumentationParser()
        docs = parser.parse_module('backend.immunia.IMMUNIA')
        parser.save_to_json(docs, 'immunia_docs.json')
    """
    
    def __init__(self):
        """Initialize documentation parser"""
        self.docs = {}
        
    def parse_module(self, module_path: str) -> Dict[str, Any]:
        """
        Parse a Python module and extract documentation
        
        Args:
            module_path: Import path (e.g., 'backend.immunia.IMMUNIA')
        
        Returns:
            Dictionary containing parsed documentation
        """
        
        try:
            # Import the module
            module = __import__(module_path, fromlist=[''])
            
            # Get module file path
            module_file = Path(inspect.getfile(module))
            
            # Parse with AST
            with open(module_file, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source)
            
            # Extract documentation
            doc = {
                'module_name': module_path,
                'file_path': str(module_file),
                'module_docstring': ast.get_docstring(tree),
                'classes': {},
                'functions': {},
                'constants': {}
            }
            
            # Parse top-level nodes
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    doc['classes'][node.name] = self._parse_class(node)
                elif isinstance(node, ast.FunctionDef):
                    doc['functions'][node.name] = self._parse_function(node)
                elif isinstance(node, ast.Assign):
                    # Extract constants (uppercase variables)
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id.isupper():
                            doc['constants'][target.id] = self._extract_value(node.value)
            
            return doc
            
        except Exception as e:
            print(f"Error parsing module {module_path}: {e}")
            return {}
    
    def _parse_class(self, node: ast.ClassDef) -> Dict[str, Any]:
        """Parse class definition"""
        
        class_doc = {
            'name': node.name,
            'docstring': ast.get_docstring(node),
            'bases': [self._get_name(base) for base in node.bases],
            'methods': {},
            'attributes': {}
        }
        
        # Parse methods
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                class_doc['methods'][item.name] = self._parse_function(item)
            elif isinstance(item, ast.Assign):
                # Class attributes
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        class_doc['attributes'][target.id] = self._extract_value(item.value)
        
        return class_doc
    
    def _parse_function(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """Parse function/method definition"""
        
        func_doc = {
            'name': node.name,
            'docstring': ast.get_docstring(node),
            'parameters': [],
            'returns': None,
            'raises': []
        }
        
        # Parse parameters
        for arg in node.args.args:
            param = {
                'name': arg.arg,
                'annotation': self._get_annotation(arg.annotation),
                'default': None
            }
            func_doc['parameters'].append(param)
        
        # Parse defaults
        defaults = node.args.defaults
        if defaults:
            # Defaults apply to last N parameters
            num_defaults = len(defaults)
            num_params = len(func_doc['parameters'])
            for i, default in enumerate(defaults):
                param_idx = num_params - num_defaults + i
                func_doc['parameters'][param_idx]['default'] = self._extract_value(default)
        
        # Parse return annotation
        if node.returns:
            func_doc['returns'] = self._get_annotation(node.returns)
        
        # Parse docstring for parameter descriptions
        if func_doc['docstring']:
            param_descriptions = self._parse_docstring_params(func_doc['docstring'])
            for param in func_doc['parameters']:
                if param['name'] in param_descriptions:
                    param['description'] = param_descriptions[param['name']]
        
        return func_doc
    
    def _parse_docstring_params(self, docstring: str) -> Dict[str, str]:
        """
        Extract parameter descriptions from docstring
        
        Supports formats:
        - Google style: Args: / Arguments:
        - NumPy style: Parameters / Parameters:
        - Sphinx style: :param name: description
        """
        
        params = {}
        
        # Google/NumPy style
        args_match = re.search(r'Args?:|Arguments?:|Parameters?:\s*\n(.*?)(?:\n\n|\n[A-Z]|\Z)', 
                              docstring, re.DOTALL | re.IGNORECASE)
        
        if args_match:
            args_block = args_match.group(1)
            # Match "param_name: description" or "param_name (type): description"
            param_pattern = r'(\w+)\s*(?:\([^)]+\))?\s*:\s*([^\n]+(?:\n\s+[^\n]+)*)'
            for match in re.finditer(param_pattern, args_block):
                param_name = match.group(1)
                param_desc = match.group(2).strip()
                params[param_name] = param_desc
        
        # Sphinx style
        sphinx_pattern = r':param\s+(\w+):\s*([^\n]+)'
        for match in re.finditer(sphinx_pattern, docstring):
            param_name = match.group(1)
            param_desc = match.group(2).strip()
            params[param_name] = param_desc
        
        return params
    
    def _get_name(self, node: ast.AST) -> str:
        """Get name from AST node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            return f"{self._get_name(node.value)}[...]"
        else:
            return str(node)
    
    def _get_annotation(self, node: Optional[ast.AST]) -> Optional[str]:
        """Extract type annotation as string"""
        if node is None:
            return None
        return self._get_name(node)
    
    def _extract_value(self, node: ast.AST) -> Any:
        """Extract constant value from AST node"""
        try:
            if isinstance(node, ast.Constant):
                return node.value
            elif isinstance(node, ast.Num):
                return node.n
            elif isinstance(node, ast.Str):
                return node.s
            elif isinstance(node, ast.List):
                return [self._extract_value(elt) for elt in node.elts]
            elif isinstance(node, ast.Dict):
                return {
                    self._extract_value(k): self._extract_value(v)
                    for k, v in zip(node.keys, node.values)
                }
            else:
                return None
        except:
            return None
    
    def parse_pipeline(self, pipeline_name: str) -> Dict[str, Any]:
        """
        Parse entire pipeline (all modules)
        
        Args:
            pipeline_name: 'immunia' or 'fastia'
        
        Returns:
            Complete pipeline documentation
        """
        
        pipeline_docs = {
            'pipeline_name': pipeline_name.upper(),
            'modules': {}
        }
        
        if pipeline_name.lower() == 'immunia':
            modules = [
                'backend.immunia.IMMUNIA',
                'backend.immunia.components.immunia_preprocessor_segmentor',
                'backend.immunia.components.immunia_tracker',
                'backend.immunia.components.immunia_analyzer',
                'backend.immunia.components.keller_segel_analyzer',
                'backend.immunia.components.particle_tracking_analyzer',
                'backend.immunia.components.graph_theory_analyzer'
            ]
        elif pipeline_name.lower() == 'fastia':
            modules = [
                'backend.fastia.FocalAdhesionDetector',
                'backend.fastia.FocalAdhesionTracker',
                'backend.fastia.FocalAdhesionAnalyzer',
                'backend.fastia.FocalAdhesionClassifier'
            ]
        else:
            return pipeline_docs
        
        # Parse each module
        for module_path in modules:
            module_name = module_path.split('.')[-1]
            print(f"Parsing {module_path}...")
            pipeline_docs['modules'][module_name] = self.parse_module(module_path)
        
        return pipeline_docs
    
    def save_to_json(self, docs: Dict[str, Any], output_path: str):
        """
        Save documentation to JSON file
        
        Args:
            docs: Documentation dictionary
            output_path: Output file path
        """
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(docs, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Documentation saved to: {output_file}")
    
    def load_from_json(self, input_path: str) -> Dict[str, Any]:
        """
        Load documentation from JSON file
        
        Args:
            input_path: Input file path
        
        Returns:
            Documentation dictionary
        """
        
        with open(input_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def extract_parameter_info(self, docs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract parameter information for quick lookup
        
        Args:
            docs: Full documentation dictionary
        
        Returns:
            Simplified parameter lookup table
        """
        
        params = {}
        
        for module_name, module_doc in docs.get('modules', {}).items():
            # Process functions
            for func_name, func_doc in module_doc.get('functions', {}).items():
                for param in func_doc.get('parameters', []):
                    param_key = f"{module_name}.{func_name}.{param['name']}"
                    params[param_key] = {
                        'name': param['name'],
                        'type': param.get('annotation'),
                        'default': param.get('default'),
                        'description': param.get('description'),
                        'function': func_name,
                        'module': module_name
                    }
            
            # Process class methods
            for class_name, class_doc in module_doc.get('classes', {}).items():
                for method_name, method_doc in class_doc.get('methods', {}).items():
                    for param in method_doc.get('parameters', []):
                        if param['name'] == 'self':
                            continue
                        param_key = f"{module_name}.{class_name}.{method_name}.{param['name']}"
                        params[param_key] = {
                            'name': param['name'],
                            'type': param.get('annotation'),
                            'default': param.get('default'),
                            'description': param.get('description'),
                            'method': method_name,
                            'class': class_name,
                            'module': module_name
                        }
        
        return params
    
    def build_searchable_index(self, docs: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Build keyword → documentation mapping for search
        
        Args:
            docs: Full documentation dictionary
        
        Returns:
            Keyword index: {keyword: [doc_paths]}
        """
        
        index = {}
        
        def add_keywords(text: str, doc_path: str):
            """Extract keywords from text and add to index"""
            if not text:
                return
            
            # Extract meaningful words (alphanumeric, 3+ chars)
            words = re.findall(r'\b\w{3,}\b', text.lower())
            
            for word in words:
                if word not in index:
                    index[word] = []
                if doc_path not in index[word]:
                    index[word].append(doc_path)
        
        # Index module docstrings
        for module_name, module_doc in docs.get('modules', {}).items():
            doc_path = f"modules.{module_name}"
            add_keywords(module_doc.get('module_docstring', ''), doc_path)
            
            # Index functions
            for func_name, func_doc in module_doc.get('functions', {}).items():
                func_path = f"{doc_path}.functions.{func_name}"
                add_keywords(func_doc.get('docstring', ''), func_path)
                add_keywords(func_name, func_path)
            
            # Index classes
            for class_name, class_doc in module_doc.get('classes', {}).items():
                class_path = f"{doc_path}.classes.{class_name}"
                add_keywords(class_doc.get('docstring', ''), class_path)
                add_keywords(class_name, class_path)
                
                # Index methods
                for method_name, method_doc in class_doc.get('methods', {}).items():
                    method_path = f"{class_path}.methods.{method_name}"
                    add_keywords(method_doc.get('docstring', ''), method_path)
                    add_keywords(method_name, method_path)
        
        return index


# ============================================================================
# STANDALONE DOCUMENTATION BUILDER
# ============================================================================

def build_all_documentation(output_dir: Optional[str] = None):
    """
    Build complete documentation for IMMUNIA and FASTIA
    
    Args:
        output_dir: Output directory (default: backend/cintelia/docs)
    """
    
    if output_dir is None:
        output_dir = Path(__file__).parent / 'docs'
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    parser = DocumentationParser()
    
    # Parse IMMUNIA
    print("\n" + "="*60)
    print("📚 Building IMMUNIA Documentation")
    print("="*60)
    
    immunia_docs = parser.parse_pipeline('immunia')
    immunia_params = parser.extract_parameter_info(immunia_docs)
    immunia_index = parser.build_searchable_index(immunia_docs)
    
    parser.save_to_json(immunia_docs, output_dir / 'immunia_docs.json')
    parser.save_to_json(immunia_params, output_dir / 'immunia_params.json')
    parser.save_to_json(immunia_index, output_dir / 'immunia_index.json')
    
    print(f"✅ IMMUNIA: {len(immunia_docs['modules'])} modules documented")
    print(f"✅ IMMUNIA: {len(immunia_params)} parameters indexed")
    
    # Parse FASTIA
    print("\n" + "="*60)
    print("📚 Building FASTIA Documentation")
    print("="*60)
    
    fastia_docs = parser.parse_pipeline('fastia')
    fastia_params = parser.extract_parameter_info(fastia_docs)
    fastia_index = parser.build_searchable_index(fastia_docs)
    
    parser.save_to_json(fastia_docs, output_dir / 'fastia_docs.json')
    parser.save_to_json(fastia_params, output_dir / 'fastia_params.json')
    parser.save_to_json(fastia_index, output_dir / 'fastia_index.json')
    
    print(f"✅ FASTIA: {len(fastia_docs['modules'])} modules documented")
    print(f"✅ FASTIA: {len(fastia_params)} parameters indexed")
    
    # Build general documentation
    print("\n" + "="*60)
    print("📚 Building General Documentation")
    print("="*60)
    
    general_docs = {
        'cellab': {
            'name': 'CELLAB',
            'description': 'Cellular Analysis Workbench',
            'version': '2.0',
            'pipelines': {
                'IMMUNIA': 'Immune cell analysis pipeline',
                'FASTIA': 'Focal adhesion analysis pipeline'
            },
            'features': [
                'Multi-tab workspace',
                'Docked configuration panels',
                'Real-time visualization',
                'Export to various formats',
                'AI assistant (cintelia)'
            ]
        }
    }
    
    parser.save_to_json(general_docs, output_dir / 'general_docs.json')
    print(f"✅ General documentation created")
    
    print("\n" + "="*60)
    print("✅ ALL DOCUMENTATION BUILT SUCCESSFULLY")
    print(f"📁 Output directory: {output_dir}")
    print("="*60)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    """Run documentation builder"""
    build_all_documentation()
