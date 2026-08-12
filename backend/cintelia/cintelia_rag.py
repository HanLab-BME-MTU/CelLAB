"""
cintelia RAG System - FIXED for Python 3.8 + Windows paths
===========================================================
"""
from __future__ import annotations
from sentence_transformers import SentenceTransformer
from pathlib import Path
import PyPDF2
from typing import Optional, List, Dict
import os
import sys

# CRITICAL: Disable ChromaDB telemetry BEFORE import (Python 3.8 fix)
os.environ['ANONYMIZED_TELEMETRY'] = 'False'

# Now safe to import chromadb
import chromadb
from chromadb.config import Settings


class cinteliaDocumentStore:
    """RAG system - FIXED for Python 3.8 and Windows paths with spaces"""
    
    def __init__(
        self, 
        docs_folder: Optional[str] = None,
        verbose: bool = False
    ):
        self.verbose = verbose
        
        # FIX 1: Proper path resolution (handles Windows + spaces)
        if docs_folder is not None:
            self.docs_folder = Path(docs_folder).resolve()
        else:
            # Auto-detect: relative to this file
            self.docs_folder = Path(__file__).parent.resolve() / "documents"
        
        # Create if doesn't exist
        self.docs_folder.mkdir(parents=True, exist_ok=True)
        
        if self.verbose:
            print(f"\n📚 Documents folder: {self.docs_folder}")
            print(f"Folder exists: {self.docs_folder.exists()}")
        
        # Load embedding model
        if self.verbose:
            print("\n📊 Loading embedding model...")
        
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        if self.verbose:
            print("✅ Embedding model loaded")
        
        # FIX 2: Use PersistentClient with explicit telemetry disable (Python 3.8 fix)
        if self.verbose:
            print("\n🗄️  Initializing vector database...")
        
        # Persist DB to avoid re-loading on every run
        db_dir = self.docs_folder / ".chroma"
        db_dir.mkdir(parents=True, exist_ok=True)
        
        # CRITICAL: Explicitly disable telemetry in Settings (Python 3.8 compatibility)
        self.client = chromadb.PersistentClient(
            path=str(db_dir),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(name="cintelia_docs")
            if self.verbose:
                print(f"✅ Loaded existing collection ({self.collection.count()} chunks)")
        except:
            self.collection = self.client.create_collection(
                name="cintelia_docs",
                metadata={"hnsw:space": "cosine"}
            )
            if self.verbose:
                print("✅ Created new collection")
        
        # Load documents
        if self.verbose:
            print("\n📖 Loading documents...")
        
        self.load_documents()
        
        if self.verbose:
            print(f"\n✅ Document Store Ready ({self.collection.count()} total chunks)\n")
    
    def load_documents(self):
        """Load and chunk documents from folder"""
        
        if not self.docs_folder.exists():
            if self.verbose:
                print(f"⚠️  Documents folder does not exist")
            return
        
        # Get all files
        all_files = list(self.docs_folder.rglob("*"))
        
        if self.verbose:
            print(f"🔍 Scanning: {self.docs_folder}")
            print(f"Found {len(all_files)} items")
        
        doc_count = 0
        chunk_count = 0
        
        for file_path in all_files:
            if not file_path.is_file():
                continue
            
            suffix = file_path.suffix.lower()
            
            if suffix in ['.txt', '.md']:
                chunks = self._process_text_file(file_path)
                if chunks > 0:
                    doc_count += 1
                    chunk_count += chunks
            
            elif suffix == '.pdf':
                chunks = self._process_pdf_file(file_path)
                if chunks > 0:
                    doc_count += 1
                    chunk_count += chunks
        
        if self.verbose:
            if doc_count > 0:
                print(f"\n✅ Loaded {doc_count} documents ({chunk_count} chunks)")
            else:
                print(f"\n⚠️  No documents found")
    
    def _process_text_file(self, file_path: Path) -> int:
        """Process text/markdown files"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
            
            if not text.strip():
                return 0
            
            chunks = self._chunk_text(text, chunk_size=500, overlap=50)
            
            if not chunks:
                return 0
            
            added = 0
            for i, chunk in enumerate(chunks):
                chunk_id = f"{file_path.stem}_{i}"
                
                # Check if exists
                try:
                    existing = self.collection.get(ids=[chunk_id])
                    if existing['ids']:
                        continue
                except:
                    pass
                
                self.collection.add(
                    documents=[chunk],
                    metadatas=[{
                        "source": file_path.name,
                        "chunk": i,
                        "type": "text"
                    }],
                    ids=[chunk_id]
                )
                added += 1
            
            if self.verbose and added > 0:
                print(f"  ✅ {file_path.name}: {added} chunks")
            
            return added
        
        except Exception as e:
            if self.verbose:
                print(f"  ❌ Error loading {file_path.name}: {e}")
            return 0
    
    def _process_pdf_file(self, file_path: Path) -> int:
        """Process PDF files"""
        try:
            with open(file_path, 'rb') as f:
                pdf = PyPDF2.PdfReader(f)
                text = ""
                for page in pdf.pages:
                    text += page.extract_text()
            
            if not text.strip():
                return 0
            
            chunks = self._chunk_text(text, chunk_size=500, overlap=50)
            
            if not chunks:
                return 0
            
            added = 0
            for i, chunk in enumerate(chunks):
                chunk_id = f"{file_path.stem}_{i}"
                
                try:
                    existing = self.collection.get(ids=[chunk_id])
                    if existing['ids']:
                        continue
                except:
                    pass
                
                self.collection.add(
                    documents=[chunk],
                    metadatas=[{
                        "source": file_path.name,
                        "chunk": i,
                        "type": "pdf"
                    }],
                    ids=[chunk_id]
                )
                added += 1
            
            if self.verbose and added > 0:
                print(f"  ✅ {file_path.name}: {added} chunks")
            
            return added
        
        except Exception as e:
            if self.verbose:
                print(f"  ❌ Error loading {file_path.name}: {e}")
            return 0
    
    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end].strip()
            
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
        
        return chunks
    
    def retrieve(self, query: str, n_results: int = 3) -> str:
        """Retrieve most relevant document chunks"""
        try:
            if self.collection.count() == 0:
                return ""
            
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            if not results['documents'][0]:
                return ""
            
            context = "\n=== RELEVANT RESEARCH DOCUMENTS ===\n"
            
            for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
                source = metadata['source']
                context += f"\n[Source: {source}]\n{doc}\n"
            
            context += "\n=== END OF DOCUMENTS ===\n"
            
            return context
        
        except Exception as e:
            if self.verbose:
                print(f"❌ Error retrieving: {e}")
            return ""
    
    def has_documents(self) -> bool:
        """Check if any documents are loaded"""
        try:
            return self.collection.count() > 0
        except:
            return False
