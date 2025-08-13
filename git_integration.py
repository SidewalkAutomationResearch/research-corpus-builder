#!/usr/bin/env python3
"""
Git Integration Module for Corpus Builder
Enables users to push module improvements and updates to GitHub for owner approval
"""

import json
import subprocess
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

class GitIntegration:
    """Handles git operations for corpus builder module improvements and script archiving"""
    
    def __init__(self, module_path: str = None):
        if module_path is None:
            module_path = str(Path(__file__).parent)
        
        self.module_path = Path(module_path)
        self.logger = logging.getLogger(__name__)
        
        # Repository configuration
        self.upstream_repo = "https://github.com/SidewalkAutomationResearch/research-corpus-builder.git"
        self.branch_prefix = "user-contribution"
        
        # Script archiving configuration
        self.script_archive_dir = self.module_path / "topic_scripts_archive"
        self.improvements_archive_dir = self.module_path / "improvements_archive"
        
        # Initialize archive directories
        self.script_archive_dir.mkdir(exist_ok=True)
        self.improvements_archive_dir.mkdir(exist_ok=True)
        
    def setup_git_environment(self) -> Dict:
        """Setup git environment for contributions"""
        try:
            os.chdir(self.module_path)
            
            # Check if we're in a git repository
            result = subprocess.run(["git", "status"], capture_output=True, text=True)
            if result.returncode != 0:
                return {"error": "Not in a git repository. Please ensure module is properly installed."}
            
            # Configure user if not set
            self._ensure_user_config()
            
            # Add upstream remote if not exists
            self._add_upstream_remote()
            
            return {"success": True, "message": "Git environment configured"}
            
        except Exception as e:
            return {"error": f"Failed to setup git environment: {e}"}
    
    def create_contribution_branch(self, feature_name: str, user_id: str = None) -> Dict:
        """Create a new branch for user contributions"""
        try:
            os.chdir(self.module_path)
            
            # Fetch latest changes from upstream
            subprocess.run(["git", "fetch", "upstream"], check=True, capture_output=True)
            
            # Create unique branch name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if user_id:
                branch_name = f"{self.branch_prefix}_{user_id}_{feature_name}_{timestamp}"
            else:
                branch_name = f"{self.branch_prefix}_{feature_name}_{timestamp}"
            
            # Create and checkout new branch from upstream/main
            subprocess.run(["git", "checkout", "-b", branch_name, "upstream/main"], 
                         check=True, capture_output=True)
            
            self.logger.info(f"Created contribution branch: {branch_name}")
            
            return {
                "success": True,
                "branch_name": branch_name,
                "message": f"Created contribution branch: {branch_name}"
            }
            
        except subprocess.CalledProcessError as e:
            return {"error": f"Failed to create branch: {e}"}
    
    def commit_improvements(self, description: str, files: List[str] = None) -> Dict:
        """Commit user improvements with proper formatting"""
        try:
            os.chdir(self.module_path)
            
            # Stage specific files or all changes
            if files:
                for file in files:
                    subprocess.run(["git", "add", file], check=True, capture_output=True)
            else:
                subprocess.run(["git", "add", "."], check=True, capture_output=True)
            
            # Check if there are changes to commit
            status_result = subprocess.run(["git", "status", "--porcelain"], 
                                         capture_output=True, text=True)
            if not status_result.stdout.strip():
                return {"error": "No changes to commit"}
            
            # Create commit message
            commit_message = self._format_commit_message(description)
            
            # Commit changes
            subprocess.run(["git", "commit", "-m", commit_message], 
                         check=True, capture_output=True)
            
            self.logger.info(f"Committed improvements: {description}")
            
            return {
                "success": True,
                "message": f"Committed improvements: {description}",
                "commit_message": commit_message
            }
            
        except subprocess.CalledProcessError as e:
            return {"error": f"Failed to commit: {e}"}
    
    def archive_topic_script(self, script_path: str, topic_name: str, 
                           script_description: str = "") -> Dict:
        """Archive a topic-related script as part of module operation"""
        try:
            script_file = Path(script_path)
            if not script_file.exists():
                return {"error": f"Script not found: {script_path}"}
            
            # Create topic-specific directory in archive
            topic_dir = self.script_archive_dir / topic_name
            topic_dir.mkdir(exist_ok=True)
            
            # Generate timestamped filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archived_name = f"{script_file.stem}_{timestamp}{script_file.suffix}"
            archived_path = topic_dir / archived_name
            
            # Copy script to archive
            import shutil
            shutil.copy2(script_file, archived_path)
            
            # Create metadata file
            metadata = {
                "original_path": str(script_file),
                "archived_path": str(archived_path),
                "topic": topic_name,
                "description": script_description,
                "archived_at": datetime.now().isoformat(),
                "file_size": script_file.stat().st_size,
                "script_type": script_file.suffix
            }
            
            metadata_path = topic_dir / f"{script_file.stem}_{timestamp}_metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            self.logger.info(f"Archived script: {script_path} -> {archived_path}")
            
            return {
                "success": True,
                "archived_path": str(archived_path),
                "metadata_path": str(metadata_path),
                "topic": topic_name,
                "message": f"Script archived for topic: {topic_name}"
            }
            
        except Exception as e:
            return {"error": f"Failed to archive script: {e}"}
    
    def archive_improvement(self, improvement_files: List[str], 
                          improvement_name: str, description: str = "") -> Dict:
        """Archive module improvements as part of operation"""
        try:
            # Create improvement-specific directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            improvement_dir = self.improvements_archive_dir / f"{improvement_name}_{timestamp}"
            improvement_dir.mkdir(exist_ok=True)
            
            archived_files = []
            
            for file_path in improvement_files:
                file_obj = Path(file_path)
                if not file_obj.exists():
                    continue
                
                # Copy file to improvement archive
                import shutil
                dest_path = improvement_dir / file_obj.name
                shutil.copy2(file_obj, dest_path)
                archived_files.append(str(dest_path))
            
            # Create improvement manifest
            manifest = {
                "improvement_name": improvement_name,
                "description": description,
                "original_files": improvement_files,
                "archived_files": archived_files,
                "archived_at": datetime.now().isoformat(),
                "total_files": len(archived_files)
            }
            
            manifest_path = improvement_dir / "improvement_manifest.json"
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)
            
            self.logger.info(f"Archived improvement: {improvement_name}")
            
            return {
                "success": True,
                "improvement_dir": str(improvement_dir),
                "manifest_path": str(manifest_path),
                "archived_files": archived_files,
                "message": f"Improvement archived: {improvement_name}"
            }
            
        except Exception as e:
            return {"error": f"Failed to archive improvement: {e}"}
    
    def commit_and_push_archives(self, commit_message: str = None) -> Dict:
        """Commit and push archived scripts and improvements"""
        try:
            os.chdir(self.module_path)
            
            # Stage archive directories
            subprocess.run(["git", "add", str(self.script_archive_dir)], 
                         check=True, capture_output=True)
            subprocess.run(["git", "add", str(self.improvements_archive_dir)], 
                         check=True, capture_output=True)
            
            # Check if there are changes to commit
            status_result = subprocess.run(["git", "status", "--porcelain"], 
                                         capture_output=True, text=True)
            if not status_result.stdout.strip():
                return {"error": "No archive changes to commit"}
            
            # Create commit message
            if not commit_message:
                commit_message = f"Archive update: topic scripts and improvements - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            formatted_message = f"""{commit_message}

Automated archiving of topic-related scripts and module improvements.
- Topic scripts preserved in topic_scripts_archive/
- Module improvements preserved in improvements_archive/
- Maintains development history and enables owner review

🗄️ Generated with corpus builder git integration

Co-Authored-By: Corpus-Builder-Module <module@corpus-builder.auto>
"""
            
            # Commit changes
            subprocess.run(["git", "commit", "-m", formatted_message], 
                         check=True, capture_output=True)
            
            # Push to origin (for user's fork or contribution branch)
            push_result = subprocess.run(["git", "push"], capture_output=True, text=True)
            
            return {
                "success": True,
                "commit_message": formatted_message,
                "push_result": push_result.stdout if push_result.returncode == 0 else push_result.stderr,
                "message": "Archives committed and pushed for owner review"
            }
            
        except subprocess.CalledProcessError as e:
            return {"error": f"Failed to commit/push archives: {e}"}
    
    def push_for_review(self, fork_repo: str = None) -> Dict:
        """Push contribution branch for owner review"""
        try:
            os.chdir(self.module_path)
            
            # Get current branch name
            branch_result = subprocess.run(["git", "branch", "--show-current"], 
                                         capture_output=True, text=True, check=True)
            current_branch = branch_result.stdout.strip()
            
            if not current_branch.startswith(self.branch_prefix):
                return {"error": "Not on a contribution branch. Use create_contribution_branch() first."}
            
            # Push to user's fork (if provided) or origin
            remote = "origin"
            if fork_repo:
                # Add user's fork as remote
                remote_name = "user-fork"
                try:
                    subprocess.run(["git", "remote", "add", remote_name, fork_repo], 
                                 check=True, capture_output=True)
                    remote = remote_name
                except:
                    pass  # Remote might already exist
            
            # Push branch
            subprocess.run(["git", "push", "-u", remote, current_branch], 
                         check=True, capture_output=True)
            
            # Generate pull request information
            pr_info = self._generate_pr_info(current_branch, fork_repo or "origin")
            
            self.logger.info(f"Pushed branch {current_branch} for review")
            
            return {
                "success": True,
                "branch_name": current_branch,
                "remote": remote,
                "pr_info": pr_info,
                "message": f"Pushed {current_branch} for owner review"
            }
            
        except subprocess.CalledProcessError as e:
            return {"error": f"Failed to push: {e}"}
    
    def create_pull_request_template(self, feature_description: str, 
                                   changes_made: List[str]) -> str:
        """Generate pull request template for user contributions"""
        
        template = f"""## 🔧 Corpus Builder Module Improvement

### Description
{feature_description}

### Changes Made
"""
        for change in changes_made:
            template += f"- {change}\n"
        
        template += f"""
### Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

### Testing
- [ ] I have tested this change locally
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes

### Additional Notes
Please review these improvements to the corpus builder module. All changes maintain compatibility with existing functionality.

### Contributor Information
- Module: Research Corpus Builder
- Timestamp: {datetime.now().isoformat()}
- Contribution Type: User Enhancement

---
*Generated with automated git integration for corpus builder contributions*
"""
        return template
    
    def submit_contribution(self, feature_name: str, description: str, 
                          changes_made: List[str], user_id: str = None,
                          fork_repo: str = None) -> Dict:
        """Complete workflow for submitting a contribution"""
        
        self.logger.info(f"Starting contribution workflow: {feature_name}")
        
        results = {
            "steps": [],
            "final_status": "pending"
        }
        
        # Step 1: Setup git environment
        setup_result = self.setup_git_environment()
        results["steps"].append({"step": "setup", "result": setup_result})
        
        if not setup_result.get("success"):
            results["final_status"] = "failed"
            return results
        
        # Step 2: Create contribution branch
        branch_result = self.create_contribution_branch(feature_name, user_id)
        results["steps"].append({"step": "branch", "result": branch_result})
        
        if not branch_result.get("success"):
            results["final_status"] = "failed"
            return results
        
        # Step 3: Commit improvements
        commit_result = self.commit_improvements(description)
        results["steps"].append({"step": "commit", "result": commit_result})
        
        if not commit_result.get("success"):
            results["final_status"] = "failed"
            return results
        
        # Step 4: Push for review
        push_result = self.push_for_review(fork_repo)
        results["steps"].append({"step": "push", "result": push_result})
        
        if not push_result.get("success"):
            results["final_status"] = "failed"
            return results
        
        # Step 5: Generate PR template
        pr_template = self.create_pull_request_template(description, changes_made)
        pr_file = self.module_path / "PULL_REQUEST_TEMPLATE.md"
        
        with open(pr_file, 'w') as f:
            f.write(pr_template)
        
        results["steps"].append({
            "step": "pr_template", 
            "result": {"success": True, "file": str(pr_file)}
        })
        
        results["final_status"] = "success"
        results["branch_name"] = branch_result["branch_name"]
        results["pr_template_path"] = str(pr_file)
        results["next_steps"] = [
            "Create pull request on GitHub using the generated template",
            f"Use branch: {branch_result['branch_name']}",
            "Target repository: https://github.com/SidewalkAutomationResearch/research-corpus-builder"
        ]
        
        return results
    
    def _ensure_user_config(self):
        """Ensure git user configuration exists"""
        try:
            # Check if user.name is configured
            result = subprocess.run(["git", "config", "user.name"], 
                                  capture_output=True, text=True)
            if result.returncode != 0 or not result.stdout.strip():
                # Set a default user name
                subprocess.run(["git", "config", "user.name", "Corpus Builder Contributor"], 
                             check=True, capture_output=True)
            
            # Check if user.email is configured
            result = subprocess.run(["git", "config", "user.email"], 
                                  capture_output=True, text=True)
            if result.returncode != 0 or not result.stdout.strip():
                # Set a default email
                subprocess.run(["git", "config", "user.email", "contributor@corpus-builder.local"], 
                             check=True, capture_output=True)
                
        except subprocess.CalledProcessError:
            pass  # Best effort configuration
    
    def _add_upstream_remote(self):
        """Add upstream remote if it doesn't exist"""
        try:
            # Check if upstream remote exists
            result = subprocess.run(["git", "remote", "get-url", "upstream"], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                # Add upstream remote
                subprocess.run(["git", "remote", "add", "upstream", self.upstream_repo], 
                             check=True, capture_output=True)
        except subprocess.CalledProcessError:
            pass  # Best effort setup
    
    def _format_commit_message(self, description: str) -> str:
        """Format commit message for contribution"""
        return f"""User contribution: {description}

Enhancement to corpus builder module functionality.
- Maintains compatibility with existing features
- Ready for maintainer review and integration

🔧 Generated with corpus builder git integration

Co-Authored-By: Corpus-Builder-User <contributor@corpus-builder.local>
"""
    
    def _generate_pr_info(self, branch_name: str, remote: str) -> Dict:
        """Generate pull request information"""
        return {
            "title": f"User Contribution: {branch_name.replace(self.branch_prefix + '_', '').replace('_', ' ').title()}",
            "head_branch": branch_name,
            "base_branch": "main",
            "target_repo": "SidewalkAutomationResearch/research-corpus-builder",
            "instructions": [
                "1. Go to https://github.com/SidewalkAutomationResearch/research-corpus-builder",
                "2. Click 'New Pull Request'",
                f"3. Select branch: {branch_name}",
                "4. Use the generated PULL_REQUEST_TEMPLATE.md for description",
                "5. Submit for maintainer review"
            ]
        }
    
    def get_contribution_status(self) -> Dict:
        """Get current contribution branch status"""
        try:
            os.chdir(self.module_path)
            
            # Get current branch
            branch_result = subprocess.run(["git", "branch", "--show-current"], 
                                         capture_output=True, text=True, check=True)
            current_branch = branch_result.stdout.strip()
            
            # Get git status
            status_result = subprocess.run(["git", "status", "--porcelain"], 
                                         capture_output=True, text=True)
            has_changes = bool(status_result.stdout.strip())
            
            # Get last commit info
            log_result = subprocess.run(["git", "log", "-1", "--pretty=format:%h %s"], 
                                      capture_output=True, text=True)
            last_commit = log_result.stdout.strip() if log_result.returncode == 0 else "No commits"
            
            return {
                "current_branch": current_branch,
                "is_contribution_branch": current_branch.startswith(self.branch_prefix),
                "has_uncommitted_changes": has_changes,
                "last_commit": last_commit,
                "ready_for_contribution": current_branch.startswith(self.branch_prefix) and not has_changes
            }
            
        except Exception as e:
            return {"error": f"Failed to get status: {e}"}

# Convenience functions for easy integration
def setup_contribution_environment() -> Dict:
    """Quick setup for contributions"""
    git_integration = GitIntegration()
    return git_integration.setup_git_environment()

def contribute_improvement(feature_name: str, description: str, 
                         changes_made: List[str], user_id: str = None) -> Dict:
    """Quick contribution workflow"""
    git_integration = GitIntegration()
    return git_integration.submit_contribution(feature_name, description, changes_made, user_id)

def archive_topic_script(script_path: str, topic_name: str, description: str = "") -> Dict:
    """Quick archive for topic-related scripts"""
    git_integration = GitIntegration()
    return git_integration.archive_topic_script(script_path, topic_name, description)

def archive_module_improvement(files: List[str], improvement_name: str, description: str = "") -> Dict:
    """Quick archive for module improvements"""
    git_integration = GitIntegration()
    return git_integration.archive_improvement(files, improvement_name, description)

def push_archives_for_review(commit_message: str = None) -> Dict:
    """Quick push of archived content for owner review"""
    git_integration = GitIntegration()
    return git_integration.commit_and_push_archives(commit_message)

if __name__ == "__main__":
    # CLI interface for git integration
    import argparse
    
    parser = argparse.ArgumentParser(description="Git Integration for Corpus Builder")
    parser.add_argument("--setup", action="store_true", help="Setup git environment")
    parser.add_argument("--contribute", help="Submit contribution (feature name)")
    parser.add_argument("--description", help="Description of changes")
    parser.add_argument("--user-id", help="User identifier")
    parser.add_argument("--status", action="store_true", help="Show contribution status")
    parser.add_argument("--archive-script", help="Archive topic script (path)")
    parser.add_argument("--topic", help="Topic name for script archiving")
    parser.add_argument("--archive-improvement", help="Archive improvement (improvement name)")
    parser.add_argument("--files", nargs="+", help="Files to archive for improvement")
    parser.add_argument("--push-archives", action="store_true", help="Push archived content for review")
    
    args = parser.parse_args()
    
    git_integration = GitIntegration()
    
    if args.setup:
        result = git_integration.setup_git_environment()
        print(f"Setup result: {json.dumps(result, indent=2)}")
    
    elif args.contribute and args.description:
        changes = [args.description]  # Simple single change for CLI
        result = git_integration.submit_contribution(
            args.contribute, 
            args.description, 
            changes, 
            args.user_id
        )
        print(f"Contribution result: {json.dumps(result, indent=2)}")
    
    elif args.archive_script and args.topic:
        result = git_integration.archive_topic_script(
            args.archive_script, 
            args.topic, 
            args.description or ""
        )
        print(f"Archive script result: {json.dumps(result, indent=2)}")
    
    elif args.archive_improvement and args.files:
        result = git_integration.archive_improvement(
            args.files,
            args.archive_improvement,
            args.description or ""
        )
        print(f"Archive improvement result: {json.dumps(result, indent=2)}")
    
    elif args.push_archives:
        result = git_integration.commit_and_push_archives(args.description)
        print(f"Push archives result: {json.dumps(result, indent=2)}")
    
    elif args.status:
        status = git_integration.get_contribution_status()
        print(f"Contribution status: {json.dumps(status, indent=2)}")
    
    else:
        print("🔧 Git Integration for Corpus Builder")
        print("Available commands:")
        print("  --setup                     Setup git environment")
        print("  --contribute FEATURE        Submit contribution")
        print("  --description DESC          Description of changes")
        print("  --user-id ID               User identifier")
        print("  --status                   Show current status")
        print("  --archive-script PATH      Archive topic script")
        print("  --topic TOPIC              Topic name for script")
        print("  --archive-improvement NAME Archive improvement")
        print("  --files FILE1 FILE2        Files to archive")
        print("  --push-archives            Push archived content")
        print("\nExamples:")
        print('  python git_integration.py --setup')
        print('  python git_integration.py --archive-script "./my_script.py" --topic "ai-safety" --description "Analysis script"')
        print('  python git_integration.py --archive-improvement "new-feature" --files "file1.py" "file2.py"')
        print('  python git_integration.py --push-archives --description "Monthly archive update"')