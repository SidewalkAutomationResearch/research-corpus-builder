#!/usr/bin/env python3
"""
Research Corpus Builder Module - Integrated functionality
Unified interface for all corpus building and management tools
"""

from .reference_expander import ReferenceExpander
from .archive_integrator import ArchiveIntegrator  
from .corpus_summarizer import CorpusSummarizer
from .execute_expansion_plan import CorpusExpansionExecutor
from .git_integration import GitIntegration
from .auto_update import track_usage, check_and_update, auto_push_when_used

__version__ = "2.0.0"
__author__ = "DFA_SUITE Research Team"

# Core functionality exports
__all__ = [
    "ReferenceExpander",
    "ArchiveIntegrator", 
    "CorpusSummarizer",
    "CorpusExpansionExecutor",
    "GitIntegration",
    "build_corpus",
    "expand_corpus",
    "integrate_archives",
    "summarize_corpus",
    "archive_topic_script",
    "archive_module_improvement",
    "push_archives_for_review"
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
    track_usage("expand_corpus", {"corpus_path": corpus_path, "max_downloads": max_downloads})
    expander = ReferenceExpander(corpus_path)
    result = expander.expand_corpus({"max_downloads": max_downloads})
    auto_push_when_used()
    return result

def integrate_archives(config_file: str):
    """Integrate archived research into corpus"""
    track_usage("integrate_archives", {"config_file": config_file})
    integrator = ArchiveIntegrator(config_file)
    result = integrator.integrate_archives()
    auto_push_when_used()
    return result

def summarize_corpus(corpus_path: str, model: str = "qwen-research"):
    """Generate corpus summary using local AI"""
    track_usage("summarize_corpus", {"corpus_path": corpus_path, "model": model})
    summarizer = CorpusSummarizer(corpus_path, model)
    result = summarizer.create_comprehensive_summary()
    auto_push_when_used()
    return result

def archive_topic_script(script_path: str, topic_name: str, description: str = ""):
    """Archive a topic-related script as part of module operation"""
    track_usage("archive_topic_script", {"script_path": script_path, "topic_name": topic_name})
    from .git_integration import archive_topic_script as _archive_script
    result = _archive_script(script_path, topic_name, description)
    auto_push_when_used()
    return result

def archive_module_improvement(files: list, improvement_name: str, description: str = ""):
    """Archive module improvements as part of operation"""
    track_usage("archive_module_improvement", {"files": len(files), "improvement_name": improvement_name})
    from .git_integration import archive_module_improvement as _archive_improvement
    result = _archive_improvement(files, improvement_name, description)
    auto_push_when_used()
    return result

def push_archives_for_review(commit_message: str = None):
    """Push archived content for owner review"""
    track_usage("push_archives_for_review", {"has_message": commit_message is not None})
    from .git_integration import push_archives_for_review as _push_archives
    result = _push_archives(commit_message)
    auto_push_when_used()
    return result

# Module configuration
DEFAULT_CONFIG = {
    "local_ai_mode": False,
    "model": "claude-opus-4-1", 
    "local_download_model": "qwen-research",
    "analysis_focus": "comprehensive_research_analysis"
}