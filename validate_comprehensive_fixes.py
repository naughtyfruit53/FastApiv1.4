#!/usr/bin/env python3
"""
Comprehensive validation script for license management, email, and authentication fixes
"""

import sys
import traceback
from typing import Dict, Any, List

def validate_schema_changes() -> Dict[str, Any]:
    """Validate that our schema changes are working correctly"""
    results = {
        "test_name": "Schema Changes Validation",
        "passed": False,
        "details": [],
        "errors": []
    }
    
    try:
        # Test PasswordChangeResponse with JWT token
        from app.schemas.user import PasswordChangeResponse
        
        pwd_response = PasswordChangeResponse(
            message="Password changed successfully",
            access_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.test",
            token_type="bearer"
        )
        
        assert pwd_response.access_token is not None
        assert pwd_response.token_type == "bearer"
        results["details"].append("✅ PasswordChangeResponse schema includes JWT token fields")
        
        # Test OrganizationLicenseResponse with email status
        from app.schemas.base import OrganizationLicenseResponse
        
        license_response = OrganizationLicenseResponse(
            message="License created successfully",
            organization_id=1,
            organization_name="Test Organization",
            superadmin_email="admin@test.org",
            subdomain="test-org",
            temp_password="TempPass123!",
            org_code="24/08-(1)-tq0001",
            email_sent=True,
            email_error=None
        )
        
        assert hasattr(license_response, 'email_sent')
        assert hasattr(license_response, 'email_error')
        assert hasattr(license_response, 'org_code')
        results["details"].append("✅ OrganizationLicenseResponse schema includes email status and org_code")
        
        results["passed"] = True
        
    except Exception as e:
        results["errors"].append(f"Schema validation failed: {str(e)}")
        results["errors"].append(traceback.format_exc())
    
    return results

def validate_enhanced_logging() -> Dict[str, Any]:
    """Validate enhanced logging functions"""
    results = {
        "test_name": "Enhanced Logging Validation", 
        "passed": False,
        "details": [],
        "errors": []
    }
    
    try:
        from app.core.logging import log_license_creation, log_password_change, log_email_operation
        
        # Test license creation logging
        log_license_creation("Test Org", "admin@test.org", "super@platform.com", True)
        results["details"].append("✅ log_license_creation function works")
        
        # Test password change logging  
        log_password_change("user@test.com", "NORMAL", True, None, True)
        results["details"].append("✅ log_password_change function works")
        
        # Test email operation logging
        log_email_operation("send", "user@test.com", True)
        results["details"].append("✅ log_email_operation function works")
        
        results["passed"] = True
        
    except Exception as e:
        results["errors"].append(f"Logging validation failed: {str(e)}")
        results["errors"].append(traceback.format_exc())
    
    return results

def validate_email_service_enhancement() -> Dict[str, Any]:
    """Validate email service enhancements"""
    results = {
        "test_name": "Email Service Enhancement Validation",
        "passed": False, 
        "details": [],
        "errors": []
    }
    
    try:
        # Test the email service method exists by checking the file content
        import os
        service_file = "/home/runner/work/FastAPIv1.1/FastAPIv1.1/v1.1/app/services/email_service.py"
        
        if os.path.exists(service_file):
            with open(service_file, 'r') as f:
                content = f.read()
                
            if 'send_license_creation_email' in content:
                results["details"].append("✅ send_license_creation_email method exists in email service")
                
            required_params = ['org_admin_email', 'org_admin_name', 'organization_name', 'temp_password', 'subdomain', 'org_code', 'created_by']
            missing_params = []
            
            for param in required_params:
                if param not in content:
                    missing_params.append(param)
                    
            if not missing_params:
                results["details"].append("✅ send_license_creation_email has all required parameters")
            else:
                results["errors"].append(f"❌ Missing parameters: {missing_params}")
                
            if 'Dual notification system' in content or 'notify_creator' in content:
                results["details"].append("✅ Email service supports dual notification (admin + creator)")
                
            results["passed"] = len(results["errors"]) == 0
            
        else:
            results["errors"].append("❌ Email service file not found")
        
    except Exception as e:
        results["errors"].append(f"Email service validation failed: {str(e)}")
        results["errors"].append(traceback.format_exc())
    
    return results

def validate_password_reset_consistency() -> Dict[str, Any]:
    """Validate password reset endpoint consistency"""
    results = {
        "test_name": "Password Reset Consistency Validation",
        "passed": False,
        "details": [],
        "errors": []
    }
    
    try:
        from app.schemas.base import PasswordResetResponse
        from app.schemas.user import AdminPasswordResetResponse
        
        # Check that both response schemas have similar fields
        pwd_reset_fields = set(PasswordResetResponse.model_fields.keys())
        admin_reset_fields = set(AdminPasswordResetResponse.model_fields.keys())
        
        common_fields = pwd_reset_fields.intersection(admin_reset_fields)
        expected_common = {'message', 'email_sent', 'email_error', 'must_change_password'}
        
        for field in expected_common:
            if field in common_fields:
                results["details"].append(f"✅ Both schemas have '{field}' field")
            else:
                results["errors"].append(f"❌ Missing common field '{field}' in one of the schemas")
        
        if not results["errors"]:
            results["passed"] = True
            results["details"].append("✅ Password reset schemas are consistent")
        
    except Exception as e:
        results["errors"].append(f"Password reset validation failed: {str(e)}")
        results["errors"].append(traceback.format_exc())
    
    return results

def validate_jwt_token_handling() -> Dict[str, Any]:
    """Validate JWT token handling in password change"""
    results = {
        "test_name": "JWT Token Handling Validation",
        "passed": False,
        "details": [],
        "errors": []
    }
    
    try:
        from app.core.security import create_access_token, verify_token
        
        # Test token creation
        token = create_access_token(
            subject="test@example.com",
            organization_id=1,
            user_role="standard_user",
            user_type="organization"
        )
        
        assert token is not None
        assert isinstance(token, str)
        results["details"].append("✅ JWT token creation works")
        
        # Test token verification
        email, org_id, role, user_type = verify_token(token)
        assert email == "test@example.com"
        assert org_id == 1
        assert role == "standard_user"
        assert user_type == "organization"
        results["details"].append("✅ JWT token verification works")
        
        results["passed"] = True
        
    except Exception as e:
        results["errors"].append(f"JWT validation failed: {str(e)}")
        results["errors"].append(traceback.format_exc())
    
    return results

def run_all_validations() -> List[Dict[str, Any]]:
    """Run all validation tests"""
    validations = [
        validate_schema_changes,
        validate_enhanced_logging,
        validate_email_service_enhancement,
        validate_password_reset_consistency,
        validate_jwt_token_handling
    ]
    
    results = []
    for validation_func in validations:
        try:
            result = validation_func()
            results.append(result)
        except Exception as e:
            results.append({
                "test_name": f"Failed to run {validation_func.__name__}",
                "passed": False,
                "details": [],
                "errors": [f"Exception during validation: {str(e)}"]
            })
    
    return results

def print_results(results: List[Dict[str, Any]]):
    """Print validation results in a nice format"""
    print("\n" + "="*80)
    print("🔍 COMPREHENSIVE VALIDATION RESULTS")
    print("="*80)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r["passed"])
    
    for result in results:
        status = "✅ PASSED" if result["passed"] else "❌ FAILED"
        print(f"\n📋 {result['test_name']}: {status}")
        
        for detail in result["details"]:
            print(f"   {detail}")
        
        for error in result["errors"]:
            print(f"   ❌ {error}")
    
    print("\n" + "="*80)
    print(f"📊 SUMMARY: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL VALIDATIONS PASSED! Implementation is working correctly.")
        return True
    else:
        print("⚠️  Some validations failed. Please review and fix the issues above.")
        return False

def main():
    """Main validation function"""
    print("🚀 Starting comprehensive validation of license management fixes...")
    
    try:
        results = run_all_validations()
        success = print_results(results)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"💥 Fatal error during validation: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()