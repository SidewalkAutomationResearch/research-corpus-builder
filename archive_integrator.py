#!/usr/bin/env python3
"""
Archive Integrator - Merge archived research into current corpus
Integrates ARCHIVED_RESEARCH_2025_08_13 into DFA_SUITE research corpus
"""

import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
import logging
from dataclasses import dataclass
import time

@dataclass
class ArchiveStats:
    """Statistics for archive integration"""
    files_processed: int = 0
    files_copied: int = 0
    files_skipped: int = 0
    total_size: int = 0
    errors: int = 0

class ArchiveIntegrator:
    """Integrate archived research into current corpus"""
    
    def __init__(self, config_file: str):
        self.config = self._load_config(config_file)
        self.target_corpus = Path(self.config['target_corpus'])
        self.stats = ArchiveStats()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Create target directory
        self.target_corpus.mkdir(exist_ok=True)
    
    def _load_config(self, config_file: str) -> Dict:
        """Load integration configuration"""
        with open(config_file, 'r') as f:
            return json.load(f)
    
    def integrate_section(self, section_name: str, section_config: Dict) -> Tuple[int, int]:
        """Integrate a research section"""
        self.logger.info(f"📁 Integrating section: {section_name}")
        
        section_dir = self.target_corpus / section_name
        section_dir.mkdir(exist_ok=True)
        
        files_copied = 0
        files_processed = 0
        
        for subsection, source_paths in section_config.items():
            subsection_dir = section_dir / subsection
            subsection_dir.mkdir(exist_ok=True)
            
            self.logger.info(f"  📂 Processing subsection: {subsection}")
            
            for source_path in source_paths:
                source = Path(source_path)
                
                if source.is_dir():
                    # Copy all files from directory
                    for file_path in source.iterdir():
                        if file_path.is_file():
                            copied = self._copy_file(file_path, subsection_dir)
                            if copied:
                                files_copied += 1
                            files_processed += 1
                elif source.is_file():
                    # Copy individual file
                    copied = self._copy_file(source, subsection_dir)
                    if copied:
                        files_copied += 1
                    files_processed += 1
        
        self.logger.info(f"  ✅ Section {section_name}: {files_copied}/{files_processed} files integrated")
        return files_copied, files_processed
    
    def _copy_file(self, source: Path, target_dir: Path) -> bool:
        """Copy file to target directory with deduplication"""
        try:
            target_file = target_dir / source.name
            
            # Skip if file already exists and is identical
            if target_file.exists():
                if target_file.stat().st_size == source.stat().st_size:
                    self.stats.files_skipped += 1
                    return False
                else:
                    # Create unique name for different file
                    base = target_file.stem
                    suffix = target_file.suffix
                    counter = 1
                    while target_file.exists():
                        target_file = target_dir / f"{base}_{counter}{suffix}"
                        counter += 1
            
            # Copy file
            shutil.copy2(source, target_file)
            self.stats.total_size += source.stat().st_size
            self.logger.info(f"    ✓ Copied: {source.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"    ✗ Error copying {source.name}: {e}")
            self.stats.errors += 1
            return False
    
    def create_integration_manifest(self) -> Dict:
        """Create manifest of integrated files"""
        manifest = {
            "integration_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "source_archive": "ARCHIVED_RESEARCH_2025_08_13",
            "target_corpus": str(self.target_corpus),
            "statistics": {
                "files_processed": self.stats.files_processed,
                "files_copied": self.stats.files_copied,
                "files_skipped": self.stats.files_skipped,
                "total_size_bytes": self.stats.total_size,
                "errors": self.stats.errors
            },
            "sections": {}
        }
        
        # Catalog integrated files by section
        for section_dir in self.target_corpus.iterdir():
            if section_dir.is_dir():
                section_files = []
                for subsection_dir in section_dir.iterdir():
                    if subsection_dir.is_dir():
                        subsection_files = [f.name for f in subsection_dir.iterdir() if f.is_file()]
                        section_files.append({
                            "subsection": subsection_dir.name,
                            "files": subsection_files,
                            "count": len(subsection_files)
                        })
                
                manifest["sections"][section_dir.name] = {
                    "subsections": section_files,
                    "total_files": sum(s["count"] for s in section_files)
                }
        
        return manifest
    
    def integrate_archives(self) -> Dict:
        """Main integration function"""
        self.logger.info("🔗 Starting archive integration")
        self.logger.info(f"Target corpus: {self.target_corpus}")
        
        start_time = time.time()
        
        # Process each section
        for section_name, section_config in self.config['sections'].items():
            copied, processed = self.integrate_section(section_name, section_config)
            self.stats.files_copied += copied
            self.stats.files_processed += processed
        
        # Create integration manifest
        manifest = self.create_integration_manifest()
        
        # Save manifest
        manifest_file = self.target_corpus / "integration_manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        # Integration summary
        duration = time.time() - start_time
        
        self.logger.info("📊 INTEGRATION COMPLETE")
        self.logger.info(f"  Files processed: {self.stats.files_processed}")
        self.logger.info(f"  Files copied: {self.stats.files_copied}")
        self.logger.info(f"  Files skipped: {self.stats.files_skipped}")
        self.logger.info(f"  Total size: {self.stats.total_size / 1024 / 1024:.1f} MB")
        self.logger.info(f"  Errors: {self.stats.errors}")
        self.logger.info(f"  Duration: {duration:.1f} seconds")
        
        return manifest

def main():
    """CLI interface for archive integrator"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Integrate archived research into corpus")
    parser.add_argument("config_file", help="Path to integration configuration JSON")
    
    args = parser.parse_args()
    
    integrator = ArchiveIntegrator(args.config_file)
    manifest = integrator.integrate_archives()
    
    print(f"\n✅ Archive integration completed!")
    print(f"Integrated {manifest['statistics']['files_copied']} files")
    print(f"Check {integrator.target_corpus}/ for integrated research")

if __name__ == "__main__":
    main()