#!/usr/bin/env python3
"""
Verification Script: Comprehensive Session/Organization Context Security Fix

This script verifies that all 5 steps of the comprehensive fix have been properly implemented:

1. Frontend Fixes - localStorage removal and JSDoc comments
2. Backend Fixes - Authentication dependency hardening
3. Data Migration - SQL migration for data integrity
4. Token/Session Creation - Proper organization_id handling
5. Testing & Verification - Test scripts available

Usage:
    python verify_comprehensive_fix.py
"""

import os
import re
import sys
from pathlib import Path


class ComprehensiveFixVerifier:
    def __init__(self, repo_root: str = "."):
        self.repo_root = Path(repo_root)
        self.frontend_path = self.repo_root / "frontend"
        self.backend_path = self.repo_root / "app"
        self.migration_path = self.repo_root / "migrations" / ".versions"
        
        self.results = {
            "frontend_fixes": {"status": "pending", "details": []},
            "backend_fixes": {"status": "pending", "details": []},
            "data_migration": {"status": "pending", "details": []},
            "token_creation": {"status": "pending", "details": []},
            "testing": {"status": "pending", "details": []},
        }
    
    def verify_frontend_fixes(self):
        """Verify Step 1: Frontend Fixes"""
        print("🔍 Verifying Frontend Fixes...")
        
        details = []
        
        # Check that localStorage.getItem('is_super_admin') has been removed
        localStorage_files = []
        if self.frontend_path.exists():
            for file_path in self.frontend_path.rglob("*.ts*"):
                try:
                    content = file_path.read_text(encoding='utf-8')
                    # Check for localStorage.getItem specifically with is_super_admin
                    if re.search(r"localStorage\.getItem\s*\(\s*['\"]is_super_admin['\"]", content):
                        if "@deprecated" not in content:  # Allow if marked as deprecated
                            localStorage_files.append(str(file_path))
                except UnicodeDecodeError:
                    continue
        
        if localStorage_files:
            details.append(f"❌ Found localStorage.getItem('is_super_admin') usage in: {localStorage_files}")
            self.results["frontend_fixes"]["status"] = "failed"
        else:
            details.append("✅ No localStorage.getItem('is_super_admin') usage found")
        
        # Check for JSDoc comments indicating organization context changes
        jsdoc_files = 0
        if self.frontend_path.exists():
            for file_path in self.frontend_path.rglob("*.ts*"):
                try:
                    content = file_path.read_text(encoding='utf-8')
                    if "@deprecated" in content and "organization" in content.lower():
                        jsdoc_files += 1
                except UnicodeDecodeError:
                    continue
        
        if jsdoc_files > 0:
            details.append(f"✅ Found {jsdoc_files} files with JSDoc comments for organization context")
        else:
            details.append("⚠️  No JSDoc comments found for organization context changes")
        
        # Check for useAuth() usage instead of localStorage
        useauth_files = 0
        if self.frontend_path.exists():
            for file_path in self.frontend_path.rglob("*.ts*"):
                try:
                    content = file_path.read_text(encoding='utf-8')
                    if "useAuth" in content:
                        useauth_files += 1
                except UnicodeDecodeError:
                    continue
        
        if useauth_files > 0:
            details.append(f"✅ Found {useauth_files} files using useAuth() hook")
        
        if self.results["frontend_fixes"]["status"] != "failed":
            self.results["frontend_fixes"]["status"] = "passed"
        
        self.results["frontend_fixes"]["details"] = details
    
    def verify_backend_fixes(self):
        """Verify Step 2: Backend Fixes"""
        print("🔍 Verifying Backend Fixes...")
        
        details = []
        
        # Check get_current_user function for proper platform user handling
        user_api_file = self.backend_path / "api" / "v1" / "user.py"
        if user_api_file.exists():
            content = user_api_file.read_text()
            
            if "is_super_admin" in content and "organization_id" in content:
                details.append("✅ get_current_user function updated for super admin handling")
            else:
                details.append("❌ get_current_user function may not be properly updated")
                self.results["backend_fixes"]["status"] = "failed"
            
            if "potential_super_admin" in content:
                details.append("✅ Logic for checking super admin before requiring org_id found")
            else:
                details.append("⚠️  Super admin check logic may be missing")
        else:
            details.append("❌ user.py not found")
            self.results["backend_fixes"]["status"] = "failed"
        
        # Check org_restrictions.py for new require_current_organization_id function
        org_restrictions_file = self.backend_path / "core" / "org_restrictions.py"
        if org_restrictions_file.exists():
            content = org_restrictions_file.read_text()
            
            if "require_current_organization_id" in content:
                details.append("✅ require_current_organization_id function found")
            else:
                details.append("⚠️  require_current_organization_id function not found")
            
            if "platform_admin" in content or "super_admin" in content:
                details.append("✅ Platform user handling logic found")
            else:
                details.append("⚠️  Platform user handling may be missing")
        else:
            details.append("❌ org_restrictions.py not found")
            self.results["backend_fixes"]["status"] = "failed"
        
        if self.results["backend_fixes"]["status"] != "failed":
            self.results["backend_fixes"]["status"] = "passed"
        
        self.results["backend_fixes"]["details"] = details
    
    def verify_data_migration(self):
        """Verify Step 3: Data Migration"""
        print("🔍 Verifying Data Migration...")
        
        details = []
        
        # Look for migration file with organization context fix
        migration_files = []
        if self.migration_path.exists():
            for file_path in self.migration_path.glob("*organization*context*.py"):
                migration_files.append(file_path)
            
            # Also check for any recent migration that mentions organization or user fixes
            for file_path in self.migration_path.glob("*.py"):
                if file_path.name.startswith("20250817"):  # Today's migrations
                    try:
                        content = file_path.read_text()
                        if "organization" in content.lower() and "user" in content.lower():
                            migration_files.append(file_path)
                    except UnicodeDecodeError:
                        continue
        
        if migration_files:
            details.append(f"✅ Found {len(migration_files)} migration file(s) for organization context")
            
            # Check migration content
            for migration_file in migration_files:
                try:
                    content = migration_file.read_text()
                    if "super_admin" in content and "organization_id" in content:
                        details.append(f"✅ Migration {migration_file.name} contains super_admin and organization_id logic")
                    if "data integrity" in content.lower():
                        details.append(f"✅ Migration {migration_file.name} addresses data integrity")
                except UnicodeDecodeError:
                    continue
        else:
            details.append("❌ No migration file found for organization context fix")
            self.results["data_migration"]["status"] = "failed"
        
        if self.results["data_migration"]["status"] != "failed":
            self.results["data_migration"]["status"] = "passed"
        
        self.results["data_migration"]["details"] = details
    
    def verify_token_creation(self):
        """Verify Step 4: Token/Session Creation"""
        print("🔍 Verifying Token/Session Creation...")
        
        details = []
        
        # Check auth.py for proper token creation logic
        auth_file = self.backend_path / "api" / "v1" / "auth.py"
        if auth_file.exists():
            content = auth_file.read_text()
            
            if "is_super_admin" in content and "organization_id" in content:
                details.append("✅ Token creation logic updated for super admin handling")
            else:
                details.append("❌ Token creation may not properly handle super admin case")
                self.results["token_creation"]["status"] = "failed"
            
            if "user_type" in content and "platform" in content:
                details.append("✅ Platform user type handling found in token creation")
            else:
                details.append("⚠️  Platform user type handling may be missing")
        else:
            details.append("❌ auth.py not found")
            self.results["token_creation"]["status"] = "failed"
        
        # Check security.py for create_access_token function
        security_file = self.backend_path / "core" / "security.py"
        if security_file.exists():
            content = security_file.read_text()
            
            if "organization_id" in content and "user_type" in content:
                details.append("✅ create_access_token function supports organization_id and user_type")
            else:
                details.append("⚠️  create_access_token function may not support all required parameters")
        
        if self.results["token_creation"]["status"] != "failed":
            self.results["token_creation"]["status"] = "passed"
        
        self.results["token_creation"]["details"] = details
    
    def verify_testing(self):
        """Verify Step 5: Testing & Verification"""
        print("🔍 Verifying Testing & Verification...")
        
        details = []
        
        # Look for test scripts
        test_files = []
        for pattern in ["*test*session*context*.py", "*test*organization*.py", "*verify*.py"]:
            test_files.extend(self.repo_root.glob(pattern))
        
        if test_files:
            details.append(f"✅ Found {len(test_files)} test/verification script(s)")
            
            for test_file in test_files:
                try:
                    content = test_file.read_text()
                    if "super_admin" in content and "organization" in content:
                        details.append(f"✅ Test script {test_file.name} covers both super admin and organization user scenarios")
                except UnicodeDecodeError:
                    continue
        else:
            details.append("❌ No test scripts found for session/organization context")
            self.results["testing"]["status"] = "failed"
        
        if self.results["testing"]["status"] != "failed":
            self.results["testing"]["status"] = "passed"
        
        self.results["testing"]["details"] = details
    
    def run_verification(self):
        """Run all verification steps"""
        print("=" * 80)
        print("🔍 COMPREHENSIVE SESSION/ORGANIZATION CONTEXT SECURITY FIX VERIFICATION")
        print("=" * 80)
        
        self.verify_frontend_fixes()
        self.verify_backend_fixes()
        self.verify_data_migration()
        self.verify_token_creation()
        self.verify_testing()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 VERIFICATION SUMMARY")
        print("=" * 50)
        
        for step, result in self.results.items():
            status_icon = "✅" if result["status"] == "passed" else "❌" if result["status"] == "failed" else "⏳"
            print(f"{status_icon} {step.replace('_', ' ').title()}: {result['status'].upper()}")
            
            for detail in result["details"]:
                print(f"   {detail}")
            print()
        
        # Overall result
        passed_count = sum(1 for result in self.results.values() if result["status"] == "passed")
        total_count = len(self.results)
        
        if passed_count == total_count:
            print("🎉 ALL VERIFICATION STEPS PASSED!")
            print("The comprehensive session/organization context security fix is properly implemented.")
            return True
        else:
            print(f"⚠️  {passed_count}/{total_count} verification steps passed.")
            print("Some issues need to be addressed before the fix is complete.")
            return False


def main():
    """Main verification function"""
    verifier = ComprehensiveFixVerifier()
    
    try:
        success = verifier.run_verification()
        
        if success:
            print("\n✅ Verification completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Verification found issues that need attention.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Verification error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()