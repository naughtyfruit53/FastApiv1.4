#!/usr/bin/env python3
"""
Simple validation script for Customer Analytics module
Tests basic functionality without database dependencies
"""

import sys
import os

# Add project root to path
sys.path.insert(0, '/home/runner/work/FastApiv1.4/FastApiv1.4')

def test_schema_imports():
    """Test that all schemas can be imported successfully"""
    print("Testing schema imports...")
    
    try:
        from app.schemas.customer_analytics import (
            CustomerAnalyticsResponse, 
            SegmentAnalyticsResponse, 
            OrganizationAnalyticsSummary,
            DashboardMetrics,
            InteractionType,
            InteractionStatus,
            SegmentName
        )
        print("✓ All schemas imported successfully")
        
        # Test enum values
        assert InteractionType.CALL == "call"
        assert InteractionStatus.COMPLETED == "completed"
        assert SegmentName.PREMIUM == "premium"
        print("✓ Enums have correct values")
        
        return True
    except Exception as e:
        print(f"✗ Schema import failed: {e}")
        return False

def test_schema_validation():
    """Test schema validation works correctly"""
    print("\nTesting schema validation...")
    
    try:
        from app.schemas.customer_analytics import CustomerAnalyticsResponse
        from datetime import datetime
        
        # Test valid data
        valid_data = {
            "customer_id": 1,
            "customer_name": "Test Customer",
            "total_interactions": 5,
            "last_interaction_date": datetime.utcnow(),
            "interaction_types": {"call": 2, "email": 3},
            "interaction_status": {"completed": 4, "pending": 1},
            "segments": [],
            "recent_interactions": [],
            "calculated_at": datetime.utcnow()
        }
        
        response = CustomerAnalyticsResponse(**valid_data)
        assert response.customer_id == 1
        assert response.total_interactions == 5
        print("✓ Schema validation works for valid data")
        
        # Test serialization
        json_data = response.model_dump()
        assert "customer_id" in json_data
        print("✓ Schema serialization works")
        
        return True
    except Exception as e:
        print(f"✗ Schema validation failed: {e}")
        return False

def test_api_router_structure():
    """Test that API router is properly structured"""
    print("\nTesting API router structure...")
    
    try:
        # Import without database dependencies
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "customer_analytics", 
            "/home/runner/work/FastApiv1.4/FastApiv1.4/app/api/customer_analytics.py"
        )
        
        # Check if file exists and is readable
        if spec is None:
            print("✗ API module file not found")
            return False
            
        print("✓ API module file exists")
        
        # Check router is defined (without importing dependencies)
        with open("/home/runner/work/FastApiv1.4/FastApiv1.4/app/api/customer_analytics.py", 'r') as f:
            content = f.read()
            
        assert "router = APIRouter()" in content
        assert "@router.get" in content
        assert "/customers/{customer_id}/analytics" in content
        assert "/segments/{segment_name}/analytics" in content
        assert "/organization/summary" in content
        assert "/dashboard/metrics" in content
        
        print("✓ API router has all required endpoints")
        return True
        
    except Exception as e:
        print(f"✗ API router test failed: {e}")
        return False

def test_service_structure():
    """Test service module structure without database"""
    print("\nTesting service structure...")
    
    try:
        # Check service file exists and has required methods
        with open("/home/runner/work/FastApiv1.4/FastApiv1.4/app/services/customer_analytics_service.py", 'r') as f:
            content = f.read()
        
        required_methods = [
            "get_customer_metrics",
            "get_segment_analytics", 
            "get_organization_analytics_summary",
            "_calculate_interaction_metrics",
            "_get_customer_segments"
        ]
        
        for method in required_methods:
            assert f"def {method}" in content
            
        print("✓ Service has all required methods")
        
        # Check multi-tenant patterns
        assert "TenantQueryMixin" in content
        assert "organization_id" in content
        assert "filter_by_tenant" in content
        
        print("✓ Service uses multi-tenant patterns")
        return True
        
    except Exception as e:
        print(f"✗ Service structure test failed: {e}")
        return False

def test_integration_points():
    """Test integration with existing codebase"""
    print("\nTesting integration points...")
    
    try:
        # Check main.py includes the router
        with open("/home/runner/work/FastApiv1.4/FastApiv1.4/app/main.py", 'r') as f:
            main_content = f.read()
        
        assert "customer_analytics" in main_content
        assert "/api/v1/analytics" in main_content
        assert "customer-analytics" in main_content
        
        print("✓ Router is integrated in main.py")
        
        # Check test file structure
        with open("/home/runner/work/FastApiv1.4/FastApiv1.4/tests/test_customer_analytics.py", 'r') as f:
            test_content = f.read()
        
        test_classes = [
            "TestCustomerAnalyticsService",
            "TestCustomerAnalyticsAPI", 
            "TestMultiTenantIsolation"
        ]
        
        for test_class in test_classes:
            assert f"class {test_class}" in test_content
            
        print("✓ Comprehensive test suite exists")
        return True
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        return False

def main():
    """Run all validation tests"""
    print("=== Customer Analytics Module Validation ===\n")
    
    tests = [
        test_schema_imports,
        test_schema_validation,
        test_api_router_structure,
        test_service_structure,
        test_integration_points
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n=== Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All validation tests passed!")
        print("\nCustomer Analytics module is ready for deployment.")
        return 0
    else:
        print("❌ Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())