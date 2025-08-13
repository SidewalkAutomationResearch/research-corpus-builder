#!/usr/bin/env python3
"""
Research Corpus Builder Module - Integrated functionality
Unified interface for all corpus building and management tools
"""

from .reference_expander import ReferenceExpander
from .archive_integrator import ArchiveIntegrator  
from .corpus_summarizer import CorpusSummarizer
from .execute_expansion_plan import CorpusExpansionExecutor

__version__ = "2.0.0"
__author__ = "DFA_SUITE Research Team"

# Core functionality exports
__all__ = [
    "ReferenceExpander",
    "ArchiveIntegrator", 
    "CorpusSummarizer",
    "CorpusExpansionExecutor",
    "build_corpus",
    "expand_corpus",
    "integrate_archives",
    "summarize_corpus"
]

def build_corpus(config_file: str):
    """Main corpus building interface"""
    from pathlib import Path
    import json
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    corpus_name = config["name"]
    print(f"🏗️  Building corpus: {corpus_name}")
    
    # Use CORPUS_BUILDER.sh for basic building
    import subprocess
    result = subprocess.run(["./CORPUS_BUILDER.sh", config_file], capture_output=True, text=True)
    
    return result.returncode == 0

def expand_corpus(corpus_path: str, max_downloads: int = 25):
    """Expand corpus using reference extraction"""
    expander = ReferenceExpander(corpus_path)
    return expander.expand_corpus({"max_downloads": max_downloads})

def integrate_archives(config_file: str):
    """Integrate archived research into corpus"""
    integrator = ArchiveIntegrator(config_file)
    return integrator.integrate_archives()

def summarize_corpus(corpus_path: str, model: str = "qwen-research"):
    """Generate corpus summary using local AI"""
    summarizer = CorpusSummarizer(corpus_path, model)
    return summarizer.create_comprehensive_summary()

# Module configuration
DEFAULT_CONFIG = {
    "local_ai_mode": False,
    "model": "claude-opus-4-1", 
    "local_download_model": "qwen-research",
    "analysis_focus": "comprehensive_research_analysis"
}