#!/usr/bin/env python3
"""
Execute Corpus Expansion Plan - Multi-phase expansion using local AI
Orchestrates the corpus expansion plan using Qwen-research model
"""

import json
import os
import time
import subprocess
from pathlib import Path
from typing import Dict, List
import logging

class CorpusExpansionExecutor:
    """Execute corpus expansion plan with local AI"""
    
    def __init__(self, plan_file: str, corpus_base: str):
        self.plan = self._load_plan(plan_file)
        self.corpus_base = Path(corpus_base)
        self.model = self.plan["execution_strategy"]["model"]
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Execution tracking
        self.execution_log = {
            "start_time": time.time(),
            "phases_completed": [],
            "total_downloads": 0,
            "total_failures": 0,
            "errors": []
        }
    
    def _load_plan(self, plan_file: str) -> Dict:
        """Load expansion plan"""
        with open(plan_file, 'r') as f:
            return json.load(f)
    
    def check_local_model(self) -> bool:
        """Verify local model is available"""
        try:
            result = subprocess.run(
                ["ollama", "list"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            return self.model in result.stdout
        except:
            return False
    
    def execute_phase(self, phase_name: str, phase_config: Dict) -> Dict:
        """Execute a single expansion phase"""
        self.logger.info(f"🚀 Executing Phase: {phase_name}")
        self.logger.info(f"   Priority: {phase_config['priority']}")
        self.logger.info(f"   Download limit: {phase_config['download_limit']}")
        
        phase_results = {
            "phase": phase_name,
            "start_time": time.time(),
            "sections_processed": [],
            "downloads": 0,
            "failures": 0,
            "success": False
        }
        
        # Process each target section
        for section in phase_config["target_sections"]:
            section_path = self.corpus_base / section
            
            if not section_path.exists():
                self.logger.warning(f"   ⚠️  Section not found: {section}")
                continue
            
            self.logger.info(f"   📁 Processing section: {section}")
            
            # Run EXPAND function on section
            try:
                cmd = [
                    "python", 
                    "reference_expander.py",
                    str(section_path),
                    "--max-downloads", str(phase_config["download_limit"]),
                    "--file-types"] + self.plan["execution_strategy"]["file_types"]
                
                self.logger.info(f"      Executing: {' '.join(cmd)}")
                
                result = subprocess.run(
                    cmd,
                    cwd=self.corpus_base / "CORPUS-BUILDER-MODULE",
                    capture_output=True,
                    text=True,
                    timeout=600  # 10 minute timeout per section
                )
                
                if result.returncode == 0:
                    # Parse downloads from output
                    output_lines = result.stdout.split('\n')
                    downloads = 0
                    for line in output_lines:
                        if "References downloaded:" in line:
                            downloads = int(line.split(":")[1].strip())
                            break
                    
                    phase_results["downloads"] += downloads
                    phase_results["sections_processed"].append({
                        "section": section,
                        "downloads": downloads,
                        "status": "success"
                    })
                    
                    self.logger.info(f"      ✅ Section complete: {downloads} downloads")
                else:
                    phase_results["failures"] += 1
                    phase_results["sections_processed"].append({
                        "section": section,
                        "error": result.stderr,
                        "status": "failed"
                    })
                    self.logger.error(f"      ❌ Section failed: {result.stderr}")
                
                # Rate limiting between sections
                time.sleep(2)
                
            except subprocess.TimeoutExpired:
                self.logger.error(f"      ⏰ Section timeout: {section}")
                phase_results["failures"] += 1
                phase_results["sections_processed"].append({
                    "section": section,
                    "error": "timeout",
                    "status": "timeout"
                })
            
            except Exception as e:
                self.logger.error(f"      💥 Section error: {e}")
                phase_results["failures"] += 1
                phase_results["sections_processed"].append({
                    "section": section,
                    "error": str(e),
                    "status": "error"
                })
        
        # Phase completion
        phase_results["end_time"] = time.time()
        phase_results["duration"] = phase_results["end_time"] - phase_results["start_time"]
        phase_results["success"] = phase_results["downloads"] > 0
        
        self.logger.info(f"   📊 Phase {phase_name} complete:")
        self.logger.info(f"      Downloads: {phase_results['downloads']}")
        self.logger.info(f"      Failures: {phase_results['failures']}")
        self.logger.info(f"      Duration: {phase_results['duration']:.1f}s")
        
        return phase_results
    
    def execute_expansion_plan(self) -> Dict:
        """Execute complete expansion plan"""
        self.logger.info("🎯 Starting Corpus Expansion Plan Execution")
        self.logger.info(f"   Model: {self.model}")
        self.logger.info(f"   Corpus: {self.corpus_base}")
        
        # Verify local model
        if not self.check_local_model():
            self.logger.error(f"❌ Local model '{self.model}' not available")
            return {"error": "Local model not available"}
        
        self.logger.info(f"✅ Local model '{self.model}' verified")
        
        # Execute phases in order
        phase_results = []
        
        for phase_name, phase_config in self.plan["expansion_plan"].items():
            try:
                result = self.execute_phase(phase_name, phase_config)
                phase_results.append(result)
                
                self.execution_log["phases_completed"].append(phase_name)
                self.execution_log["total_downloads"] += result["downloads"]
                self.execution_log["total_failures"] += result["failures"]
                
                # Check if we should continue
                success_criteria = self.plan["success_criteria"]
                if self.execution_log["total_failures"] > success_criteria["maximum_failures"]:
                    self.logger.warning("⚠️  Maximum failures exceeded, stopping execution")
                    break
                
            except Exception as e:
                self.logger.error(f"💥 Phase {phase_name} failed: {e}")
                self.execution_log["errors"].append(f"Phase {phase_name}: {e}")
        
        # Final results
        self.execution_log["end_time"] = time.time()
        self.execution_log["total_duration"] = self.execution_log["end_time"] - self.execution_log["start_time"]
        
        final_results = {
            "execution_summary": self.execution_log,
            "phase_results": phase_results,
            "success_criteria_met": self._check_success_criteria(),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Log final summary
        self.logger.info("🏁 Expansion Plan Execution Complete")
        self.logger.info(f"   Total Downloads: {self.execution_log['total_downloads']}")
        self.logger.info(f"   Total Failures: {self.execution_log['total_failures']}")
        self.logger.info(f"   Phases Completed: {len(self.execution_log['phases_completed'])}")
        self.logger.info(f"   Total Duration: {self.execution_log['total_duration']:.1f}s")
        
        return final_results
    
    def _check_success_criteria(self) -> Dict:
        """Check if success criteria were met"""
        criteria = self.plan["success_criteria"]
        
        return {
            "minimum_new_papers": self.execution_log["total_downloads"] >= criteria["minimum_new_papers"],
            "maximum_failures": self.execution_log["total_failures"] <= criteria["maximum_failures"],
            "completion_time": self.execution_log["total_duration"] <= (criteria["completion_time_minutes"] * 60) if "completion_time_minutes" in criteria else True,
            "overall_success": (
                self.execution_log["total_downloads"] >= criteria["minimum_new_papers"] and
                self.execution_log["total_failures"] <= criteria["maximum_failures"]
            )
        }
    
    def save_results(self, results: Dict, output_file: str = None) -> str:
        """Save execution results"""
        if output_file is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_file = f"expansion_execution_results_{timestamp}.json"
        
        output_path = self.corpus_base / "CORPUS-BUILDER-MODULE" / output_file
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        self.logger.info(f"💾 Results saved to: {output_path}")
        return str(output_path)

def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Execute corpus expansion plan with local AI")
    parser.add_argument("--plan", default="corpus_expansion_plan.json", help="Expansion plan file")
    parser.add_argument("--corpus", default="../", help="Corpus base directory")
    parser.add_argument("--output", help="Output results file")
    
    args = parser.parse_args()
    
    executor = CorpusExpansionExecutor(args.plan, args.corpus)
    results = executor.execute_expansion_plan()
    
    # Save results
    results_file = executor.save_results(results, args.output)
    
    # Print summary
    print(f"\n🎯 Corpus Expansion Complete!")
    print(f"Downloads: {results['execution_summary']['total_downloads']}")
    print(f"Failures: {results['execution_summary']['total_failures']}")
    print(f"Duration: {results['execution_summary']['total_duration']:.1f}s")
    print(f"Results: {results_file}")
    
    if results['success_criteria_met']['overall_success']:
        print("✅ Success criteria met!")
    else:
        print("⚠️  Success criteria not fully met")

if __name__ == "__main__":
    main()