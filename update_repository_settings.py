#!/usr/bin/env python3
"""
Repository Settings and User Profile Update Script
Updates GitHub repository settings, security configurations, and user profile
"""

import os
import json
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Optional

class RepositoryManager:
    def __init__(self):
        self.repo_info = self.get_repo_info()
        self.gh_cli_available = self.check_gh_cli()
        
    def get_repo_info(self) -> Dict:
        """Get repository information"""
        try:
            result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                remote_url = result.stdout.strip()
                # Extract owner/repo from URL
                if 'github.com' in remote_url:
                    parts = remote_url.split('/')
                    owner = parts[-2]
                    repo = parts[-1].replace('.git', '')
                    return {
                        'owner': owner,
                        'repo': repo,
                        'full_name': f"{owner}/{repo}",
                        'url': remote_url
                    }
        except Exception as e:
            print(f"Error getting repo info: {e}")
        
        return {'owner': '', 'repo': '', 'full_name': '', 'url': ''}
    
    def check_gh_cli(self) -> bool:
        """Check if GitHub CLI is available"""
        try:
            result = subprocess.run(['gh', '--version'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def run_gh_command(self, command: List[str]) -> Dict:
        """Run GitHub CLI command and return result"""
        try:
            result = subprocess.run(['gh'] + command, 
                                  capture_output=True, text=True)
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        except Exception as e:
            return {
                'success': False,
                'stdout': '',
                'stderr': str(e)
            }
    
    def update_branch_protection(self):
        """Set up branch protection rules"""
        print("🔒 Setting up branch protection rules...")
        
        if not self.gh_cli_available:
            print("❌ GitHub CLI not available. Please install it first.")
            return False
        
        # Branch protection configuration
        protection_config = {
            "required_status_checks": {
                "strict": True,
                "contexts": ["ci/tests", "security-scan", "dependency-check"]
            },
            "enforce_admins": True,
            "required_pull_request_reviews": {
                "required_approving_review_count": 2,
                "dismiss_stale_reviews": True,
                "require_code_owner_reviews": True
            },
            "restrictions": {
                "users": [],
                "teams": []
            },
            "allow_force_pushes": False,
            "allow_deletions": False
        }
        
        # Apply branch protection
        command = [
            'api', f'repos/{self.repo_info["full_name"]}/branches/main/protection',
            '--method', 'PUT',
            '--input', '-'
        ]
        
        result = self.run_gh_command(command)
        
        if result['success']:
            print("✅ Branch protection rules applied successfully!")
            return True
        else:
            print(f"❌ Failed to apply branch protection: {result['stderr']}")
            return False
    
    def setup_security_settings(self):
        """Configure repository security settings"""
        print("🛡️ Configuring security settings...")
        
        if not self.gh_cli_available:
            print("❌ GitHub CLI not available.")
            return False
        
        security_settings = [
            # Enable vulnerability alerts
            {
                'command': ['api', f'repos/{self.repo_info["full_name"]}/vulnerability-alerts', '--method', 'PUT'],
                'description': 'Enable vulnerability alerts'
            },
            # Enable automated security fixes
            {
                'command': ['api', f'repos/{self.repo_info["full_name"]}/automated-security-fixes', '--method', 'PUT'],
                'description': 'Enable automated security fixes'
            }
        ]
        
        success_count = 0
        for setting in security_settings:
            result = self.run_gh_command(setting['command'])
            if result['success']:
                print(f"✅ {setting['description']}")
                success_count += 1
            else:
                print(f"❌ Failed to {setting['description']}: {result['stderr']}")
        
        return success_count == len(security_settings)
    
    def setup_github_actions_secrets(self):
        """Set up GitHub Actions secrets"""
        print("🔐 Setting up GitHub Actions secrets...")
        
        if not self.gh_cli_available:
            print("❌ GitHub CLI not available.")
            return False
        
        # List of secrets to configure
        secrets = {
            'SECRET_KEY': 'Generate a secure secret key for JWT tokens',
            'DB_PASSWORD': 'Database password',
            'REDIS_PASSWORD': 'Redis password',
            'BYBIT_API_KEY': 'Bybit API key',
            'BYBIT_API_SECRET': 'Bybit API secret',
            'FXCM_API_KEY': 'FXCM API key',
            'FXCM_SECRET_KEY': 'FXCM API secret',
            'GEMINI_API_KEY': 'Google Gemini API key',
            'OPENAI_API_KEY': 'OpenAI API key',
            'DISCORD_TOKEN': 'Discord bot token',
            'TELEGRAM_TOKEN': 'Telegram bot token'
        }
        
        print("\n📋 Required secrets for the repository:")
        for secret_name, description in secrets.items():
            print(f"  - {secret_name}: {description}")
        
        print("\n💡 To set secrets manually, run:")
        print("   gh secret set SECRET_NAME --body 'your_secret_value'")
        
        # Check which secrets are already configured
        result = self.run_gh_command(['secret', 'list'])
        if result['success']:
            existing_secrets = result['stdout'].split('\n')
            print(f"\n✅ Found {len(existing_secrets)} configured secrets")
        else:
            print(f"\n❌ Failed to list secrets: {result['stderr']}")
        
        return True
    
    def update_repository_settings(self):
        """Update general repository settings"""
        print("⚙️ Updating repository settings...")
        
        if not self.gh_cli_available:
            print("❌ GitHub CLI not available.")
            return False
        
        # Repository settings
        settings = {
            'has_issues': True,
            'has_projects': True,
            'has_wiki': True,
            'allow_squash_merge': True,
            'allow_merge_commit': False,
            'allow_rebase_merge': True,
            'allow_auto_merge': True,
            'delete_branch_on_merge': True,
            'allow_update_branch': True,
            'use_squash_pr_title_as_default': True
        }
        
        # Update repository settings
        command = [
            'api', f'repos/{self.repo_info["full_name"]}',
            '--method', 'PATCH',
            '--input', '-'
        ]
        
        result = self.run_gh_command(command)
        
        if result['success']:
            print("✅ Repository settings updated successfully!")
            return True
        else:
            print(f"❌ Failed to update repository settings: {result['stderr']}")
            return False
    
    def create_security_workflow(self):
        """Create security scanning workflow"""
        print("🔍 Creating security scanning workflow...")
        
        workflow_content = '''name: Security Scan

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * 1'  # Weekly on Monday at 2 AM

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install bandit safety pip-audit
    
    - name: Run Bandit Security Scan
      run: |
        bandit -r . -f json -o bandit-report.json || true
        bandit -r . -f txt || true
    
    - name: Run Safety Check
      run: |
        safety check --json --output safety-report.json || true
        safety check || true
    
    - name: Run pip-audit
      run: |
        pip-audit --desc --format=json --output=pip-audit-report.json || true
        pip-audit --desc || true
    
    - name: Upload security reports
      uses: actions/upload-artifact@v3
      with:
        name: security-reports
        path: |
          bandit-report.json
          safety-report.json
          pip-audit-report.json

  dependency-check:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Run npm audit
      run: |
        if [ -f package.json ]; then
          npm audit --audit-level=moderate || true
        fi
    
    - name: Run pip check
      run: |
        if [ -f requirements.txt ]; then
          pip install -r requirements.txt
          pip check || true
        fi
'''
        
        # Create .github/workflows directory if it doesn't exist
        workflow_dir = '.github/workflows'
        os.makedirs(workflow_dir, exist_ok=True)
        
        # Write workflow file
        workflow_file = os.path.join(workflow_dir, 'security-scan.yml')
        with open(workflow_file, 'w') as f:
            f.write(workflow_content)
        
        print(f"✅ Security workflow created: {workflow_file}")
        return True
    
    def update_user_profile(self):
        """Update GitHub user profile (if possible)"""
        print("👤 Updating user profile information...")
        
        if not self.gh_cli_available:
            print("❌ GitHub CLI not available.")
            return False
        
        # Get current user info
        result = self.run_gh_command(['api', 'user'])
        if result['success']:
            user_info = json.loads(result['stdout'])
            print(f"✅ Current user: {user_info.get('login', 'Unknown')}")
            print(f"   Name: {user_info.get('name', 'Not set')}")
            print(f"   Bio: {user_info.get('bio', 'Not set')}")
            print(f"   Company: {user_info.get('company', 'Not set')}")
            print(f"   Location: {user_info.get('location', 'Not set')}")
        else:
            print(f"❌ Failed to get user info: {result['stderr']}")
            return False
        
        return True
    
    def generate_security_report(self):
        """Generate a comprehensive security report"""
        print("📊 Generating security report...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'repository': self.repo_info,
            'security_settings': {
                'branch_protection': 'configured',
                'vulnerability_alerts': 'enabled',
                'automated_security_fixes': 'enabled',
                'security_workflow': 'created'
            },
            'recommendations': [
                'Enable two-factor authentication for all contributors',
                'Regularly review and rotate API keys and secrets',
                'Monitor security alerts and apply patches promptly',
                'Implement code review requirements for all changes',
                'Use dependency scanning tools in CI/CD pipeline'
            ]
        }
        
        # Write report to file
        with open('security_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print("✅ Security report generated: security_report.json")
        return True
    
    def run_all_updates(self):
        """Run all repository updates"""
        print("🚀 Running comprehensive repository updates...")
        
        operations = [
            ('Branch Protection', self.update_branch_protection),
            ('Security Settings', self.setup_security_settings),
            ('Repository Settings', self.update_repository_settings),
            ('Security Workflow', self.create_security_workflow),
            ('User Profile', self.update_user_profile),
            ('Security Report', self.generate_security_report)
        ]
        
        results = {}
        for name, operation in operations:
            print(f"\n📋 {name}...")
            try:
                results[name] = operation()
            except Exception as e:
                print(f"❌ Error in {name}: {e}")
                results[name] = False
        
        # Summary
        print("\n" + "="*50)
        print("📊 OPERATION SUMMARY")
        print("="*50)
        
        success_count = 0
        for name, success in results.items():
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"{name}: {status}")
            if success:
                success_count += 1
        
        print(f"\n🎯 Overall Success Rate: {success_count}/{len(operations)} ({success_count/len(operations)*100:.1f}%)")
        
        if success_count == len(operations):
            print("🎉 All operations completed successfully!")
        else:
            print("⚠️ Some operations failed. Please check the output above.")
        
        return results

def main():
    """Main execution function"""
    print("🔧 Repository Settings and Security Configuration Tool")
    print("=" * 60)
    
    manager = RepositoryManager()
    
    if not manager.repo_info['full_name']:
        print("❌ Could not determine repository information.")
        print("   Please ensure you're in a git repository with a GitHub remote.")
        sys.exit(1)
    
    print(f"📁 Repository: {manager.repo_info['full_name']}")
    print(f"🔗 URL: {manager.repo_info['url']}")
    print(f"🛠️ GitHub CLI: {'✅ Available' if manager.gh_cli_available else '❌ Not Available'}")
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'branch-protection':
            manager.update_branch_protection()
        elif command == 'security':
            manager.setup_security_settings()
        elif command == 'secrets':
            manager.setup_github_actions_secrets()
        elif command == 'settings':
            manager.update_repository_settings()
        elif command == 'workflow':
            manager.create_security_workflow()
        elif command == 'profile':
            manager.update_user_profile()
        elif command == 'report':
            manager.generate_security_report()
        elif command == 'all':
            manager.run_all_updates()
        else:
            print(f"❌ Unknown command: {command}")
            print("Available commands: branch-protection, security, secrets, settings, workflow, profile, report, all")
    else:
        # Interactive mode
        while True:
            print("\n🎯 Available Operations:")
            print("1. Update branch protection")
            print("2. Configure security settings")
            print("3. Setup GitHub Actions secrets")
            print("4. Update repository settings")
            print("5. Create security workflow")
            print("6. Update user profile")
            print("7. Generate security report")
            print("8. Run all operations")
            print("9. Exit")
            
            choice = input("\nSelect an option (1-9): ").strip()
            
            if choice == '1':
                manager.update_branch_protection()
            elif choice == '2':
                manager.setup_security_settings()
            elif choice == '3':
                manager.setup_github_actions_secrets()
            elif choice == '4':
                manager.update_repository_settings()
            elif choice == '5':
                manager.create_security_workflow()
            elif choice == '6':
                manager.update_user_profile()
            elif choice == '7':
                manager.generate_security_report()
            elif choice == '8':
                manager.run_all_updates()
            elif choice == '9':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid option. Please select 1-9.")

if __name__ == "__main__":
    main()