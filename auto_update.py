#!/usr/bin/env python3
"""
Auto-Update Module for Corpus Builder
Enables automatic updates from GitHub and pushing improvements when used
"""

import subprocess
import os
import json
from pathlib import Path
from typing import Dict, Optional
import logging
from datetime import datetime
import time

class AutoUpdater:
    """Handles automatic updates and push functionality for the module"""
    
    def __init__(self, module_path: str = None):
        if module_path is None:
            module_path = str(Path(__file__).parent)
        
        self.module_path = Path(module_path)
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.repo_url = "https://github.com/SidewalkAutomationResearch/research-corpus-builder.git"
        self.update_check_file = self.module_path / ".last_update_check"
        self.usage_log_file = self.module_path / ".usage_log.json"
        self.auto_push_enabled = True
        
        # Initialize usage tracking
        self._init_usage_tracking()
    
    def _init_usage_tracking(self):
        """Initialize usage tracking"""
        if not self.usage_log_file.exists():
            usage_data = {
                "first_use": datetime.now().isoformat(),
                "usage_count": 0,
                "last_used": None,
                "functions_used": {},
                "auto_updates": []
            }
            
            with open(self.usage_log_file, 'w') as f:
                json.dump(usage_data, f, indent=2)
    
    def should_check_for_updates(self) -> bool:
        """Check if we should check for updates (every 24 hours)"""
        if not self.update_check_file.exists():
            return True
        
        try:
            last_check = self.update_check_file.stat().st_mtime
            current_time = time.time()
            # Check every 24 hours (86400 seconds)
            return (current_time - last_check) > 86400
        except:
            return True
    
    def check_for_updates(self, force: bool = False) -> Dict:
        """Check if updates are available from GitHub"""
        if not force and not self.should_check_for_updates():
            return {"update_available": False, "reason": "Recently checked"}
        
        try:
            os.chdir(self.module_path)
            
            # Fetch latest from remote
            subprocess.run(["git", "fetch", "origin"], check=True, capture_output=True)
            
            # Check if behind remote
            result = subprocess.run(["git", "rev-list", "--count", "HEAD..origin/main"], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                commits_behind = int(result.stdout.strip())
                
                # Update last check time
                self.update_check_file.touch()
                
                if commits_behind > 0:
                    # Get summary of new commits
                    log_result = subprocess.run([
                        "git", "log", "--oneline", f"HEAD..origin/main"
                    ], capture_output=True, text=True)
                    
                    return {
                        "update_available": True,
                        "commits_behind": commits_behind,
                        "new_commits": log_result.stdout.strip().split('\n') if log_result.returncode == 0 else [],
                        "checked_at": datetime.now().isoformat()
                    }
                else:
                    return {
                        "update_available": False,
                        "commits_behind": 0,
                        "checked_at": datetime.now().isoformat()
                    }
            else:
                return {"error": "Failed to check for updates"}
                
        except Exception as e:
            return {"error": f"Update check failed: {e}"}
    
    def auto_update(self, backup_local_changes: bool = True) -> Dict:
        """Automatically update from GitHub if updates are available"""
        # Check for updates first
        update_check = self.check_for_updates(force=True)
        
        if not update_check.get("update_available"):
            return {"updated": False, "reason": "No updates available", "check_result": update_check}
        
        try:
            os.chdir(self.module_path)
            
            # Backup local changes if requested
            backup_result = None
            if backup_local_changes:
                backup_result = self._backup_local_changes()
            
            # Pull latest changes
            pull_result = subprocess.run(["git", "pull", "origin", "main"], 
                                       capture_output=True, text=True, check=True)
            
            # Log the auto-update
            self._log_auto_update(update_check, backup_result)
            
            return {
                "updated": True,
                "commits_updated": update_check.get("commits_behind", 0),
                "new_commits": update_check.get("new_commits", []),
                "backup_result": backup_result,
                "pull_output": pull_result.stdout,
                "updated_at": datetime.now().isoformat()
            }
            
        except subprocess.CalledProcessError as e:
            return {"error": f"Auto-update failed: {e}"}
    
    def log_usage(self, function_name: str, parameters: Dict = None):
        """Log usage of module functions"""
        try:
            # Load existing usage data
            with open(self.usage_log_file, 'r') as f:
                usage_data = json.load(f)
            
            # Update usage statistics
            usage_data["usage_count"] += 1
            usage_data["last_used"] = datetime.now().isoformat()
            
            if function_name not in usage_data["functions_used"]:
                usage_data["functions_used"][function_name] = {"count": 0, "last_used": None}
            
            usage_data["functions_used"][function_name]["count"] += 1
            usage_data["functions_used"][function_name]["last_used"] = datetime.now().isoformat()
            
            if parameters:
                usage_data["functions_used"][function_name]["last_parameters"] = parameters
            
            # Save updated usage data
            with open(self.usage_log_file, 'w') as f:
                json.dump(usage_data, f, indent=2)
            
            # Auto-update check on usage
            if self.should_check_for_updates():
                update_result = self.check_for_updates()
                if update_result.get("update_available"):
                    self.logger.info(f"Updates available: {update_result['commits_behind']} commits behind")
            
        except Exception as e:
            self.logger.error(f"Failed to log usage: {e}")
    
    def auto_push_improvements(self, commit_message: str = None) -> Dict:
        """Automatically push improvements and archives when module is used"""
        if not self.auto_push_enabled:
            return {"pushed": False, "reason": "Auto-push disabled"}
        
        try:
            os.chdir(self.module_path)
            
            # Check if there are any changes to push
            status_result = subprocess.run(["git", "status", "--porcelain"], 
                                         capture_output=True, text=True)
            
            if not status_result.stdout.strip():
                return {"pushed": False, "reason": "No changes to push"}
            
            # Check if we're on main branch or should create a new branch
            branch_result = subprocess.run(["git", "branch", "--show-current"], 
                                         capture_output=True, text=True, check=True)
            current_branch = branch_result.stdout.strip()
            
            # If on main, create a new branch for auto-improvements
            if current_branch == "main":
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                auto_branch = f"auto-improvements-{timestamp}"
                
                subprocess.run(["git", "checkout", "-b", auto_branch], 
                             check=True, capture_output=True)
                push_branch = auto_branch
            else:
                push_branch = current_branch
            
            # Stage and commit changes
            subprocess.run(["git", "add", "."], check=True, capture_output=True)
            
            if not commit_message:
                commit_message = f"Auto-update: usage improvements and archives - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            formatted_message = f"""{commit_message}

Automatic commit of usage-based improvements and archives.
- Usage statistics updated
- Topic scripts and improvements archived
- Module enhancements from user activity

🤖 Auto-generated by corpus builder auto-update system

Co-Authored-By: Auto-Updater <auto-update@corpus-builder.module>
"""
            
            commit_result = subprocess.run(["git", "commit", "-m", formatted_message], 
                                         capture_output=True, text=True)
            
            if commit_result.returncode != 0:
                return {"pushed": False, "reason": "Nothing to commit"}
            
            # Push to origin
            push_result = subprocess.run(["git", "push", "-u", "origin", push_branch], 
                                       capture_output=True, text=True)
            
            return {
                "pushed": True,
                "branch": push_branch,
                "commit_message": formatted_message,
                "push_output": push_result.stdout,
                "pushed_at": datetime.now().isoformat()
            }
            
        except subprocess.CalledProcessError as e:
            return {"error": f"Auto-push failed: {e}"}
    
    def _backup_local_changes(self) -> Dict:
        """Backup local changes before auto-update"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_branch = f"auto-backup-{timestamp}"
            
            # Create backup branch
            subprocess.run(["git", "checkout", "-b", backup_branch], 
                         check=True, capture_output=True)
            
            # Commit any uncommitted changes
            subprocess.run(["git", "add", "."], check=True, capture_output=True)
            
            commit_result = subprocess.run([
                "git", "commit", "-m", f"Auto-backup before update - {timestamp}"
            ], capture_output=True, text=True)
            
            # Switch back to main
            subprocess.run(["git", "checkout", "main"], check=True, capture_output=True)
            
            return {
                "success": True,
                "backup_branch": backup_branch,
                "committed_changes": commit_result.returncode == 0
            }
            
        except subprocess.CalledProcessError as e:
            return {"error": f"Backup failed: {e}"}
    
    def _log_auto_update(self, update_check: Dict, backup_result: Dict):
        """Log auto-update activity"""
        try:
            with open(self.usage_log_file, 'r') as f:
                usage_data = json.load(f)
            
            auto_update_entry = {
                "timestamp": datetime.now().isoformat(),
                "commits_updated": update_check.get("commits_behind", 0),
                "new_commits": update_check.get("new_commits", []),
                "backup_created": backup_result.get("success", False) if backup_result else False
            }
            
            usage_data["auto_updates"].append(auto_update_entry)
            
            with open(self.usage_log_file, 'w') as f:
                json.dump(usage_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to log auto-update: {e}")
    
    def get_update_status(self) -> Dict:
        """Get current update and usage status"""
        try:
            # Load usage data
            with open(self.usage_log_file, 'r') as f:
                usage_data = json.load(f)
            
            # Check for updates
            update_check = self.check_for_updates()
            
            return {
                "usage_statistics": usage_data,
                "update_status": update_check,
                "auto_push_enabled": self.auto_push_enabled,
                "last_check_file_exists": self.update_check_file.exists(),
                "should_check_updates": self.should_check_for_updates()
            }
            
        except Exception as e:
            return {"error": f"Failed to get status: {e}"}

# Module-level auto-updater instance
_auto_updater = None

def get_auto_updater() -> AutoUpdater:
    """Get the global auto-updater instance"""
    global _auto_updater
    if _auto_updater is None:
        _auto_updater = AutoUpdater()
    return _auto_updater

def track_usage(function_name: str, parameters: Dict = None):
    """Track usage of a function"""
    updater = get_auto_updater()
    updater.log_usage(function_name, parameters)

def check_and_update():
    """Check for updates and auto-update if available"""
    updater = get_auto_updater()
    return updater.auto_update()

def auto_push_when_used():
    """Auto-push improvements when module is used"""
    updater = get_auto_updater()
    return updater.auto_push_improvements()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Auto-Update for Corpus Builder")
    parser.add_argument("--check", action="store_true", help="Check for updates")
    parser.add_argument("--update", action="store_true", help="Auto-update if available")
    parser.add_argument("--status", action="store_true", help="Show update status")
    parser.add_argument("--push", action="store_true", help="Auto-push improvements")
    
    args = parser.parse_args()
    
    updater = AutoUpdater()
    
    if args.check:
        result = updater.check_for_updates(force=True)
        print(f"Update check: {json.dumps(result, indent=2)}")
    
    elif args.update:
        result = updater.auto_update()
        print(f"Auto-update: {json.dumps(result, indent=2)}")
    
    elif args.push:
        result = updater.auto_push_improvements()
        print(f"Auto-push: {json.dumps(result, indent=2)}")
    
    elif args.status:
        status = updater.get_update_status()
        print(f"Status: {json.dumps(status, indent=2)}")
    
    else:
        print("🔄 Auto-Update for Corpus Builder")
        print("Available commands:")
        print("  --check    Check for updates")
        print("  --update   Auto-update if available") 
        print("  --push     Auto-push improvements")
        print("  --status   Show update status")