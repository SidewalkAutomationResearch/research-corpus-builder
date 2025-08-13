#!/usr/bin/env python3
"""
EXPAND Function for Corpus Builder - Reference Extraction and Download
Extracts references from corpus documents and downloads them to expand the corpus
"""

import json
import os
import re
import sqlite3
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import requests
from urllib.parse import urlparse, urljoin
import time
import logging
from dataclasses import dataclass

@dataclass
class Reference:
    """Structure to hold reference information"""
    citation: str
    url: Optional[str] = None
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    title: Optional[str] = None
    authors: Optional[str] = None
    year: Optional[str] = None
    source_document: Optional[str] = None

class ReferenceExpander:
    """EXPAND function implementation for corpus builder"""
    
    def __init__(self, corpus_base_dir: str):
        self.corpus_base_dir = Path(corpus_base_dir)
        self.references_db = self.corpus_base_dir / "references.db"
        self.expansion_log = self.corpus_base_dir / "expansion_log.json"
        self.downloaded_refs = set()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize database
        self._init_database()
        
        # Reference extraction patterns
        self.doi_pattern = re.compile(r'10\.\d{4,}[^\s]*[a-zA-Z0-9]', re.IGNORECASE)
        self.arxiv_pattern = re.compile(r'arXiv:(\d{4}\.\d{4,5})', re.IGNORECASE)
        self.url_pattern = re.compile(r'https?://[^\s<>"\']+', re.IGNORECASE)
        
        # Citation patterns (APA, IEEE, etc.)
        self.citation_patterns = [
            re.compile(r'\[(\d+)\]\s*([^[]+?)(?=\[|\n|$)', re.MULTILINE),  # IEEE style [1] Author
            re.compile(r'(\w+(?:,\s*\w+)*)\s*\((\d{4})\)\.\s*([^.]+\.)', re.MULTILINE),  # APA style
            re.compile(r'References?\s*\n(.*?)(?=\n\n|\Z)', re.DOTALL | re.IGNORECASE),  # References section
        ]
    
    def _init_database(self):
        """Initialize SQLite database for tracking references"""
        with sqlite3.connect(self.references_db) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS ref_citations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    citation TEXT,
                    url TEXT,
                    doi TEXT,
                    arxiv_id TEXT,
                    title TEXT,
                    authors TEXT,
                    year TEXT,
                    source_document TEXT,
                    download_status TEXT DEFAULT 'pending',
                    download_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS expansion_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    corpus_name TEXT,
                    expansion_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    documents_processed INTEGER,
                    references_found INTEGER,
                    references_downloaded INTEGER,
                    expansion_config TEXT
                )
            ''')
    
    def extract_references_from_pdf(self, pdf_path: str) -> List[Reference]:
        """Extract references from PDF using pdfplumber"""
        references = []
        
        try:
            import pdfplumber
            
            with pdfplumber.open(pdf_path) as pdf:
                full_text = ""
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"
                
                # Extract references using patterns
                references = self._extract_references_from_text(full_text, pdf_path)
                
        except ImportError:
            self.logger.warning("pdfplumber not available, skipping PDF reference extraction")
        except Exception as e:
            self.logger.error(f"Error extracting from PDF {pdf_path}: {e}")
        
        return references
    
    def extract_references_from_text(self, text_path: str) -> List[Reference]:
        """Extract references from text/markdown files"""
        references = []
        
        try:
            with open(text_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            references = self._extract_references_from_text(content, text_path)
            
        except Exception as e:
            self.logger.error(f"Error extracting from text {text_path}: {e}")
        
        return references
    
    def _extract_references_from_text(self, text: str, source_file: str) -> List[Reference]:
        """Extract references from text content using various patterns"""
        references = []
        
        # Extract DOIs
        dois = self.doi_pattern.findall(text)
        for doi in dois:
            ref = Reference(
                citation=f"DOI: {doi}",
                doi=doi,
                source_document=source_file
            )
            references.append(ref)
        
        # Extract arXiv IDs
        arxiv_ids = self.arxiv_pattern.findall(text)
        for arxiv_id in arxiv_ids:
            ref = Reference(
                citation=f"arXiv:{arxiv_id}",
                arxiv_id=arxiv_id,
                url=f"https://arxiv.org/pdf/{arxiv_id}.pdf",
                source_document=source_file
            )
            references.append(ref)
        
        # Extract direct URLs
        urls = self.url_pattern.findall(text)
        for url in urls:
            if any(domain in url for domain in ['arxiv.org', 'doi.org', 'pubmed', 'scholar.google']):
                ref = Reference(
                    citation=f"URL: {url}",
                    url=url,
                    source_document=source_file
                )
                references.append(ref)
        
        # Extract structured citations
        for pattern in self.citation_patterns:
            matches = pattern.findall(text)
            for match in matches:
                if isinstance(match, tuple) and len(match) >= 2:
                    ref = Reference(
                        citation=str(match),
                        authors=match[0] if len(match) > 0 else None,
                        year=match[1] if len(match) > 1 else None,
                        title=match[2] if len(match) > 2 else None,
                        source_document=source_file
                    )
                    references.append(ref)
        
        return references
    
    def resolve_doi_to_url(self, doi: str) -> Optional[str]:
        """Resolve DOI to downloadable URL"""
        try:
            response = requests.head(f"https://doi.org/{doi}", allow_redirects=True, timeout=10)
            if response.status_code == 200:
                return response.url
        except Exception as e:
            self.logger.error(f"Error resolving DOI {doi}: {e}")
        
        return None
    
    def download_reference(self, reference: Reference, target_dir: Path) -> Tuple[bool, str]:
        """Download a reference document"""
        if not reference.url and reference.doi:
            reference.url = self.resolve_doi_to_url(reference.doi)
        
        if not reference.url:
            return False, "No downloadable URL available"
        
        try:
            # Determine filename
            if reference.arxiv_id:
                filename = f"{reference.arxiv_id}.pdf"
            elif reference.doi:
                filename = f"{reference.doi.replace('/', '_')}.pdf"
            else:
                parsed = urlparse(reference.url)
                filename = os.path.basename(parsed.path) or "document.pdf"
            
            # Ensure target directory exists
            target_dir.mkdir(parents=True, exist_ok=True)
            target_path = target_dir / filename
            
            # Skip if already downloaded
            if target_path.exists():
                return True, str(target_path)
            
            # Download with curl (more reliable than requests for large files)
            cmd = [
                'curl', '-s', '-L', '-o', str(target_path),
                '--max-time', '300',  # 5 minute timeout
                '--retry', '3',
                reference.url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and target_path.exists() and target_path.stat().st_size > 1000:
                self.logger.info(f"✓ Downloaded {filename}")
                return True, str(target_path)
            else:
                if target_path.exists():
                    target_path.unlink()  # Remove failed download
                return False, f"Download failed: {result.stderr}"
                
        except Exception as e:
            return False, f"Download error: {e}"
    
    def save_reference_to_db(self, reference: Reference, download_status: str = "pending", download_path: str = None):
        """Save reference to database"""
        with sqlite3.connect(self.references_db) as conn:
            conn.execute('''
                INSERT INTO ref_citations 
                (citation, url, doi, arxiv_id, title, authors, year, source_document, download_status, download_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                reference.citation,
                reference.url,
                reference.doi,
                reference.arxiv_id,
                reference.title,
                reference.authors,
                reference.year,
                reference.source_document,
                download_status,
                download_path
            ))
    
    def expand_corpus(self, config: Dict = None) -> Dict:
        """
        Main EXPAND function - Extract and download references from corpus
        
        Args:
            config: Optional configuration dict with settings like:
                   - max_downloads: Maximum number of references to download
                   - target_sections: Specific corpus sections to expand
                   - file_types: File types to process for reference extraction
        
        Returns:
            Dict with expansion statistics and results
        """
        if config is None:
            config = {}
        
        max_downloads = config.get('max_downloads', 50)
        target_sections = config.get('target_sections', None)
        file_types = config.get('file_types', ['.pdf', '.txt', '.md'])
        
        self.logger.info(f"🔍 Starting EXPAND function on corpus: {self.corpus_base_dir.name}")
        
        expansion_stats = {
            'start_time': time.time(),
            'documents_processed': 0,
            'references_found': 0,
            'references_downloaded': 0,
            'failed_downloads': 0,
            'skipped_duplicates': 0,
            'expansion_config': config
        }
        
        # Find all documents in corpus
        documents_to_process = []
        
        for corpus_section in self.corpus_base_dir.iterdir():
            if corpus_section.is_dir() and not corpus_section.name.startswith('.'):
                # Skip if target_sections specified and this isn't included
                if target_sections and corpus_section.name not in target_sections:
                    continue
                
                # Find all relevant files
                for file_path in corpus_section.rglob("*"):
                    if file_path.is_file() and file_path.suffix.lower() in file_types:
                        documents_to_process.append(file_path)
        
        self.logger.info(f"📄 Found {len(documents_to_process)} documents to process")
        
        # Extract references from each document
        all_references = []
        
        for doc_path in documents_to_process:
            self.logger.info(f"Processing: {doc_path.name}")
            
            if doc_path.suffix.lower() == '.pdf':
                refs = self.extract_references_from_pdf(str(doc_path))
            else:
                refs = self.extract_references_from_text(str(doc_path))
            
            all_references.extend(refs)
            expansion_stats['documents_processed'] += 1
            
            self.logger.info(f"  Found {len(refs)} references")
        
        expansion_stats['references_found'] = len(all_references)
        self.logger.info(f"🔗 Total references found: {len(all_references)}")
        
        # Deduplicate references
        unique_refs = {}
        for ref in all_references:
            # Use DOI, arXiv ID, or URL as deduplication key
            key = ref.doi or ref.arxiv_id or ref.url or ref.citation
            if key not in unique_refs:
                unique_refs[key] = ref
            else:
                expansion_stats['skipped_duplicates'] += 1
        
        self.logger.info(f"📚 Unique references after deduplication: {len(unique_refs)}")
        
        # Create expanded section directory
        expanded_dir = self.corpus_base_dir / "EXPANDED_REFERENCES"
        expanded_dir.mkdir(exist_ok=True)
        
        # Download references (limited by max_downloads)
        downloaded_count = 0
        
        for i, (key, ref) in enumerate(unique_refs.items()):
            if downloaded_count >= max_downloads:
                self.logger.info(f"Reached download limit of {max_downloads}")
                break
            
            # Save reference to database
            self.save_reference_to_db(ref)
            
            # Try to download if URL available
            if ref.url or ref.doi or ref.arxiv_id:
                success, result = self.download_reference(ref, expanded_dir)
                
                if success:
                    self.save_reference_to_db(ref, "downloaded", result)
                    downloaded_count += 1
                    expansion_stats['references_downloaded'] += 1
                else:
                    self.save_reference_to_db(ref, "failed", result)
                    expansion_stats['failed_downloads'] += 1
                
                # Rate limiting
                time.sleep(0.5)
        
        # Save expansion history
        expansion_stats['end_time'] = time.time()
        expansion_stats['duration'] = expansion_stats['end_time'] - expansion_stats['start_time']
        
        with sqlite3.connect(self.references_db) as conn:
            conn.execute('''
                INSERT INTO expansion_history 
                (corpus_name, documents_processed, references_found, references_downloaded, expansion_config)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                self.corpus_base_dir.name,
                expansion_stats['documents_processed'],
                expansion_stats['references_found'],
                expansion_stats['references_downloaded'],
                json.dumps(config)
            ))
        
        # Save expansion log
        with open(self.expansion_log, 'w') as f:
            json.dump(expansion_stats, f, indent=2)
        
        self.logger.info(f"✅ EXPAND function completed!")
        self.logger.info(f"   Documents processed: {expansion_stats['documents_processed']}")
        self.logger.info(f"   References found: {expansion_stats['references_found']}")
        self.logger.info(f"   References downloaded: {expansion_stats['references_downloaded']}")
        self.logger.info(f"   Failed downloads: {expansion_stats['failed_downloads']}")
        self.logger.info(f"   Duration: {expansion_stats['duration']:.1f} seconds")
        
        return expansion_stats

def main():
    """CLI interface for reference expander"""
    import argparse
    
    parser = argparse.ArgumentParser(description="EXPAND function - Extract and download references from corpus")
    parser.add_argument("corpus_dir", help="Path to corpus directory")
    parser.add_argument("--max-downloads", type=int, default=50, help="Maximum number of references to download")
    parser.add_argument("--sections", nargs="*", help="Specific corpus sections to expand")
    parser.add_argument("--file-types", nargs="*", default=['.pdf', '.txt', '.md'], help="File types to process")
    
    args = parser.parse_args()
    
    config = {
        'max_downloads': args.max_downloads,
        'target_sections': args.sections,
        'file_types': args.file_types
    }
    
    expander = ReferenceExpander(args.corpus_dir)
    results = expander.expand_corpus(config)
    
    print(f"\n🎯 EXPANSION COMPLETE")
    print(f"References downloaded: {results['references_downloaded']}")
    print(f"Check {args.corpus_dir}/EXPANDED_REFERENCES/ for new papers")

if __name__ == "__main__":
    main()