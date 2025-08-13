#!/usr/bin/env python3
"""
Research Corpus Summarizer - Generate comprehensive corpus analysis
Uses local AI to analyze and summarize the entire research corpus
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
import subprocess
import time
import logging

class CorpusSummarizer:
    """Generate comprehensive corpus summaries using local AI"""
    
    def __init__(self, corpus_base: str, model: str = "qwen-research"):
        self.corpus_base = Path(corpus_base)
        self.model = model
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)
        
        # Corpus sections to analyze
        self.sections = {
            "AI_SAFETY_CORPUS": "AI Safety Research",
            "EXPANDED_REFERENCES": "Expanded AI Safety References", 
            "ai_psychosis_CORPUS": "AI Psychosis Research",
            "Voice": "Voice Synthesis & Cloning",
            "ASI-arch": "Artificial Superintelligence Architecture",
            "PSYCHOSIS_CORPUS": "Psychosis Clinical Research",
            "INTEGRATED_ARCHIVES": "Integrated Archives (Autoimmune & MFT)"
        }
    
    def get_section_stats(self, section_path: Path) -> Dict:
        """Get basic statistics for a corpus section"""
        if not section_path.exists():
            return {"status": "not_found"}
        
        stats = {
            "status": "found",
            "total_files": 0,
            "pdf_files": 0,
            "json_files": 0,
            "md_files": 0,
            "directories": 0,
            "total_size_mb": 0
        }
        
        try:
            for item in section_path.rglob("*"):
                if item.is_file():
                    stats["total_files"] += 1
                    stats["total_size_mb"] += item.stat().st_size / (1024 * 1024)
                    
                    if item.suffix.lower() == '.pdf':
                        stats["pdf_files"] += 1
                    elif item.suffix.lower() == '.json':
                        stats["json_files"] += 1
                    elif item.suffix.lower() == '.md':
                        stats["md_files"] += 1
                        
                elif item.is_dir():
                    stats["directories"] += 1
                    
        except Exception as e:
            self.logger.error(f"Error analyzing {section_path}: {e}")
            stats["error"] = str(e)
        
        return stats
    
    def query_local_ai(self, prompt: str) -> str:
        """Query local AI model with prompt"""
        try:
            cmd = ["ollama", "run", self.model, prompt]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                self.logger.error(f"Ollama error: {result.stderr}")
                return f"Error: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return "Error: Local AI query timed out"
        except Exception as e:
            return f"Error: {e}"
    
    def analyze_section_content(self, section_name: str, section_path: Path) -> Dict:
        """Use local AI to analyze section content"""
        self.logger.info(f"🔍 Analyzing {section_name} with local AI...")
        
        # Sample some files for analysis
        sample_files = []
        if section_path.exists():
            for file_path in section_path.rglob("*"):
                if file_path.is_file() and len(sample_files) < 5:
                    try:
                        if file_path.suffix.lower() in ['.json', '.md', '.txt']:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()[:2000]  # First 2000 chars
                                sample_files.append({
                                    "filename": file_path.name,
                                    "content_preview": content
                                })
                    except:
                        continue
        
        # Create analysis prompt
        prompt = f"""Analyze this research corpus section: {section_name}

Sample files from this section:
{json.dumps(sample_files, indent=2)}

Provide a brief analysis including:
1. Research focus and themes
2. Key topics covered  
3. Quality and scope assessment
4. Potential research applications

Keep response under 200 words."""

        analysis = self.query_local_ai(prompt)
        
        return {
            "ai_analysis": analysis,
            "sample_files_analyzed": len(sample_files)
        }
    
    def generate_corpus_overview(self) -> str:
        """Generate high-level corpus overview using local AI"""
        self.logger.info("🎯 Generating corpus overview with local AI...")
        
        # Collect section summaries
        section_summaries = []
        for section_dir, section_name in self.sections.items():
            section_path = self.corpus_base / section_dir
            stats = self.get_section_stats(section_path)
            if stats["status"] == "found":
                section_summaries.append(f"- {section_name}: {stats['total_files']} files ({stats['total_size_mb']:.1f} MB)")
        
        prompt = f"""Analyze this research corpus composition:

{chr(10).join(section_summaries)}

This corpus contains AI safety research, psychosis studies, voice synthesis tools, and clinical research.

Provide a strategic overview including:
1. Overall research scope and interdisciplinary connections
2. Key research strengths and capabilities  
3. Potential research directions and applications
4. Gaps that could be filled

Keep response under 300 words, focus on research value and opportunities."""

        return self.query_local_ai(prompt)
    
    def create_comprehensive_summary(self) -> Dict:
        """Create comprehensive corpus summary"""
        self.logger.info("📊 Creating comprehensive research corpus summary...")
        
        summary = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "corpus_base": str(self.corpus_base),
            "analysis_model": self.model,
            "sections": {},
            "overall_stats": {
                "total_sections": 0,
                "total_files": 0,
                "total_size_mb": 0,
                "active_sections": 0
            }
        }
        
        # Analyze each section
        for section_dir, section_name in self.sections.items():
            section_path = self.corpus_base / section_dir
            
            self.logger.info(f"📁 Analyzing section: {section_name}")
            
            # Get basic stats
            stats = self.get_section_stats(section_path)
            
            # Get AI analysis if section exists
            ai_analysis = {}
            if stats["status"] == "found":
                ai_analysis = self.analyze_section_content(section_name, section_path)
                summary["overall_stats"]["active_sections"] += 1
                summary["overall_stats"]["total_files"] += stats.get("total_files", 0)
                summary["overall_stats"]["total_size_mb"] += stats.get("total_size_mb", 0)
            
            summary["sections"][section_dir] = {
                "name": section_name,
                "statistics": stats,
                "ai_analysis": ai_analysis
            }
            summary["overall_stats"]["total_sections"] += 1
        
        # Generate overall analysis
        summary["corpus_overview"] = self.generate_corpus_overview()
        
        return summary
    
    def save_summary(self, summary: Dict, output_file: str = None) -> str:
        """Save summary to file"""
        if output_file is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_file = f"corpus_summary_{timestamp}.json"
        
        output_path = self.corpus_base / output_file
        
        with open(output_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        self.logger.info(f"💾 Summary saved to: {output_path}")
        return str(output_path)
    
    def generate_markdown_report(self, summary: Dict) -> str:
        """Generate markdown report from summary"""
        report = f"""# Research Corpus Summary

**Generated**: {summary['timestamp']}  
**Model**: {summary['analysis_model']}  
**Base**: {summary['corpus_base']}

## Overview

{summary.get('corpus_overview', 'No overview available')}

## Statistics

- **Total Sections**: {summary['overall_stats']['total_sections']}
- **Active Sections**: {summary['overall_stats']['active_sections']}  
- **Total Files**: {summary['overall_stats']['total_files']}
- **Total Size**: {summary['overall_stats']['total_size_mb']:.1f} MB

## Section Analysis

"""
        
        for section_id, section_data in summary['sections'].items():
            if section_data['statistics']['status'] == 'found':
                stats = section_data['statistics']
                report += f"""### {section_data['name']}

**Files**: {stats['total_files']} | **Size**: {stats['total_size_mb']:.1f} MB  
**PDFs**: {stats['pdf_files']} | **JSONs**: {stats['json_files']} | **Directories**: {stats['directories']}

{section_data['ai_analysis'].get('ai_analysis', 'No analysis available')}

---

"""
        
        return report

def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Summarize research corpus with local AI")
    parser.add_argument("corpus_path", help="Path to research corpus base directory")
    parser.add_argument("--model", default="qwen-research", help="Local AI model to use")
    parser.add_argument("--output", help="Output file name (optional)")
    
    args = parser.parse_args()
    
    summarizer = CorpusSummarizer(args.corpus_path, args.model)
    summary = summarizer.create_comprehensive_summary()
    
    # Save JSON summary
    json_file = summarizer.save_summary(summary, args.output)
    
    # Generate and save markdown report
    markdown_report = summarizer.generate_markdown_report(summary)
    md_file = json_file.replace('.json', '.md')
    with open(md_file, 'w') as f:
        f.write(markdown_report)
    
    print(f"\n📊 Corpus analysis complete!")
    print(f"JSON Summary: {json_file}")
    print(f"Markdown Report: {md_file}")
    print(f"\nTotal: {summary['overall_stats']['total_files']} files across {summary['overall_stats']['active_sections']} active sections")

if __name__ == "__main__":
    main()