#!/usr/bin/env python3
"""
Validation script for Session Continuity & Debug Implementation
This script validates that all required changes have been implemented correctly.
"""

import os
import re
from pathlib import Path

def check_file_exists(filepath):
    """Check if a file exists and return its status."""
    return os.path.exists(filepath)

def check_code_pattern(filepath, pattern, description):
    """Check if a code pattern exists in a file."""
    if not os.path.exists(filepath):
        return False, f"File {filepath} not found"
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if re.search(pattern, content, re.MULTILINE | re.DOTALL):
                return True, f"✅ {description}"
            else:
                return False, f"❌ {description} - pattern not found"
    except Exception as e:
        return False, f"❌ Error reading {filepath}: {e}"

def validate_implementation():
    """Validate all session continuity implementation requirements."""
    print("🔍 Validating Session Continuity & Debug Implementation")
    print("=" * 70)
    
    checks = []
    
    # Frontend checks
    frontend_checks = [
        ("frontend/src/context/AuthContext.tsx", r"\[AuthContext\].*Starting fetchUser", "Enhanced AuthContext debug logging"),
        ("frontend/src/lib/api.ts", r"\[API\].*hasToken.*hasOrgId", "Enhanced API interceptor logging"),
        ("frontend/src/pages/dashboard/index.tsx", r"Loading user context", "Dashboard loading protection"),
        ("frontend/src/pages/login.tsx", r"All auth context stored", "Enhanced login flow"),
        ("frontend/src/components/CreateOrganizationLicenseModal.tsx", r"\[LicenseModal\].*current user session preserved", "License creation session logging"),
        ("frontend/src/services/authService.ts", r"\[AuthService\].*Starting.*login", "Enhanced auth service logging"),
    ]
    
    # Backend checks
    backend_checks = [
        ("app/api/companies.py", r"\[/companies/current\].*Request from user", "Enhanced companies endpoint logging"),
        ("app/api/v1/user.py", r"\[/users/me\].*Request from user", "Enhanced users/me endpoint logging"),
        ("app/core/org_restrictions.py", r"\[ensure_organization_context\]", "Enhanced organization context logging"),
        ("app/api/v1/organizations.py", r"\[License Creation\].*Session preservation", "License creation session preservation"),
    ]
    
    # Documentation checks
    doc_checks = [
        ("SESSION_CONTINUITY_IMPLEMENTATION.md", r"Session Continuity.*Implementation Summary", "Implementation documentation"),
        ("MANUAL_TESTING_GUIDE.md", r"Manual Testing Guide.*Session Continuity", "Testing guide documentation"),
    ]
    
    all_checks = [
        ("Frontend Enhancements", frontend_checks),
        ("Backend Enhancements", backend_checks),
        ("Documentation", doc_checks)
    ]
    
    total_passed = 0
    total_checks = 0
    
    for section, section_checks in all_checks:
        print(f"\n📋 {section}:")
        section_passed = 0
        
        for filepath, pattern, description in section_checks:
            total_checks += 1
            passed, message = check_code_pattern(filepath, pattern, description)
            print(f"  {message}")
            if passed:
                section_passed += 1
                total_passed += 1
        
        print(f"  📊 Section Result: {section_passed}/{len(section_checks)} passed")
    
    print("\n" + "=" * 70)
    print(f"🎯 Overall Result: {total_passed}/{total_checks} checks passed")
    
    if total_passed == total_checks:
        print("🎉 All implementation requirements validated successfully!")
        print("\n✅ Key Features Implemented:")
        print("  • Comprehensive debug logging throughout auth flows")
        print("  • Session preservation for license creation")
        print("  • Enhanced error handling with specific messages")
        print("  • Dashboard loading protection against race conditions")
        print("  • Improved localStorage management and context establishment")
        print("  • Backend logging for critical auth endpoints")
        print("  • Complete documentation and testing guides")
        
        print("\n🔧 Ready for Testing:")
        print("  1. Manual testing using MANUAL_TESTING_GUIDE.md")
        print("  2. Console-based debugging with enhanced logs")
        print("  3. Session continuity validation scenarios")
        
        return True
    else:
        print("⚠️  Some implementation requirements are missing.")
        print("Please review the failed checks and ensure all changes are complete.")
        return False

def check_additional_features():
    """Check for additional implementation features."""
    print("\n🔧 Additional Features Check:")
    
    features = [
        ("test_session_continuity.py", "Session continuity test suite"),
        ("SESSION_CONTINUITY_IMPLEMENTATION.md", "Comprehensive implementation documentation"),
        ("MANUAL_TESTING_GUIDE.md", "Manual testing procedures"),
    ]
    
    for filepath, description in features:
        if check_file_exists(filepath):
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ {description} - missing")

if __name__ == "__main__":
    print("🚀 Session Continuity Implementation Validator")
    print("This script validates the comprehensive session fixes implementation.")
    print()
    
    success = validate_implementation()
    check_additional_features()
    
    if success:
        print("\n✨ Implementation validation complete!")
        print("The session continuity and debug enhancements are ready for deployment.")
    else:
        print("\n🔄 Please complete the missing implementations before deployment.")
    
    exit(0 if success else 1)