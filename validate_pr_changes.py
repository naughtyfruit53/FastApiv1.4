#!/usr/bin/env python3
"""
Validation script for PR changes to ensure requirements are met
"""
import re
import os
from pathlib import Path

def check_auto_login_removal():
    """Check that auto-login has been removed from license creation modal"""
    modal_path = Path("frontend/src/components/CreateOrganizationLicenseModal.tsx")
    if not modal_path.exists():
        return False, "Modal file not found"
    
    with open(modal_path, 'r') as f:
        content = f.read()
    
    # Check that auto-login code is removed
    auto_login_patterns = [
        r'authService\.loginWithEmail',
        r'window\.location\.reload\(\)',
        r'Auto-login successful'
    ]
    
    found_auto_login = any(re.search(pattern, content) for pattern in auto_login_patterns)
    
    if found_auto_login:
        return False, "Auto-login code still present in modal"
    
    # Check that appropriate comment exists explaining the removal
    comment_found = "Note: Removed auto-login functionality" in content
    
    if not comment_found:
        return False, "Missing explanatory comment about auto-login removal"
    
    return True, "Auto-login successfully removed from license creation modal"

def check_email_enhancements():
    """Check that email functionality has been enhanced with proper logging"""
    org_path = Path("app/api/v1/organizations.py")
    if not org_path.exists():
        return False, "Organizations API file not found"
    
    with open(org_path, 'r') as f:
        content = f.read()
    
    # Check for enhanced email subject line
    enhanced_subject = "Org Super Admin Account Created" in content
    
    # Check for enhanced logging
    enhanced_logging = "logger.info" in content and "email sent successfully" in content.lower()
    
    # Check for better error handling
    better_error_handling = "logger.error" in content and "email service error details" in content.lower()
    
    if not all([enhanced_subject, enhanced_logging, better_error_handling]):
        missing = []
        if not enhanced_subject:
            missing.append("enhanced email subject")
        if not enhanced_logging:
            missing.append("enhanced logging")
        if not better_error_handling:
            missing.append("better error handling")
        return False, f"Missing email enhancements: {', '.join(missing)}"
    
    return True, "Email functionality properly enhanced with logging and error handling"

def check_role_clarity():
    """Check that role distinctions are clear and correct"""
    user_schema_path = Path("app/schemas/user.py")
    base_schema_path = Path("app/schemas/base.py")
    
    if not user_schema_path.exists():
        return False, "User schema file not found"
    
    with open(user_schema_path, 'r') as f:
        user_content = f.read()
    
    # Check UserRole enum exists with correct roles
    role_definitions = [
        "SUPER_ADMIN",
        "ORG_ADMIN", 
        "ADMIN",
        "STANDARD_USER"
    ]
    
    all_roles_found = all(role in user_content for role in role_definitions)
    
    if not all_roles_found:
        return False, "Not all required roles found in UserRole enum"
    
    # Check base schema for display names
    if base_schema_path.exists():
        with open(base_schema_path, 'r') as f:
            base_content = f.read()
        
        display_names = [
            "App Super Admin",
            "Org Super Admin",
            "Admin", 
            "Standard User"
        ]
        
        all_displays_found = all(display in base_content for display in display_names)
        
        if not all_displays_found:
            return False, "Role display names not properly defined"
    
    return True, "Role definitions and display names are clear and correct"

def check_informational_text_update():
    """Check that informational text in modal has been updated"""
    modal_path = Path("frontend/src/components/CreateOrganizationLicenseModal.tsx")
    if not modal_path.exists():
        return False, "Modal file not found"
    
    with open(modal_path, 'r') as f:
        content = f.read()
    
    # Check for updated informational text
    updated_text_indicators = [
        "org super admin account will be set up",
        "welcome email with login credentials will be sent",
        "You will remain logged in as the current super admin",
        "org super admin must log in separately"
    ]
    
    found_indicators = sum(1 for indicator in updated_text_indicators if indicator.lower() in content.lower())
    
    if found_indicators < 3:  # At least 3 out of 4 indicators should be present
        return False, f"Informational text not sufficiently updated (found {found_indicators}/4 indicators)"
    
    return True, "Informational text properly updated to reflect new behavior"

def main():
    """Run all validation checks"""
    print("🔍 Validating PR Changes...")
    print("=" * 50)
    
    checks = [
        ("Auto-login Removal", check_auto_login_removal),
        ("Email Enhancements", check_email_enhancements), 
        ("Role Clarity", check_role_clarity),
        ("Informational Text Update", check_informational_text_update),
    ]
    
    results = []
    all_passed = True
    
    for check_name, check_func in checks:
        try:
            passed, message = check_func()
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} {check_name}: {message}")
            results.append((check_name, passed, message))
            if not passed:
                all_passed = False
        except Exception as e:
            print(f"❌ FAIL {check_name}: Error during check - {e}")
            results.append((check_name, False, f"Error: {e}"))
            all_passed = False
    
    print("=" * 50)
    if all_passed:
        print("🎉 All checks passed! PR requirements have been met.")
    else:
        print("⚠️  Some checks failed. Please review the issues above.")
        
    return all_passed

if __name__ == "__main__":
    # Change to v1.1 directory to run checks
    os.chdir(Path(__file__).parent)
    success = main()
    exit(0 if success else 1)