#!/usr/bin/env python3
"""
Simple verification script to test imports and basic functionality
Run this to verify that our changes didn't break the basic structure
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

def test_basic_imports():
    """Test that basic imports work"""
    print("Testing basic imports...")
    
    try:
        # Test core imports
        from core.database import Base
        print("✓ Core database import successful")
        
        # Test model imports  
        from models.base import User, Customer, Vendor, Product
        print("✓ Basic model imports successful")
        
        # Test new file models
        from models.base import CustomerFile, VendorFile, ProductFile
        print("✓ File model imports successful")
        
        # Test schema imports
        from schemas.base import CustomerFileResponse, VendorFileResponse
        print("✓ File schema imports successful")
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    
    return True

def test_voucher_service_import():
    """Test voucher service imports"""
    print("\nTesting voucher service...")
    
    try:
        from services.voucher_service import VoucherNumberService
        print("✓ VoucherNumberService import successful")
        
        # Test that the method exists
        assert hasattr(VoucherNumberService, 'generate_voucher_number')
        print("✓ generate_voucher_number method exists")
        
    except ImportError as e:
        print(f"✗ Voucher service import error: {e}")
        return False
    except AssertionError as e:
        print(f"✗ Voucher service method missing: {e}")
        return False
    
    return True

def test_api_imports():
    """Test API imports"""
    print("\nTesting API imports...")
    
    try:
        # Test voucher API imports
        from api.v1.vouchers.payment_voucher import router as payment_router
        print("✓ Payment voucher API import successful")
        
        from api.v1.vouchers.receipt_voucher import router as receipt_router  
        print("✓ Receipt voucher API import successful")
        
        # Test customer and vendor API imports
        from api.customers import router as customer_router
        from api.vendors import router as vendor_router
        print("✓ Customer and vendor API imports successful")
        
    except ImportError as e:
        print(f"✗ API import error: {e}")
        return False
    
    return True

def test_main_app():
    """Test main app import"""
    print("\nTesting main app...")
    
    try:
        from main import app
        print("✓ Main app import successful")
        
        # Check that app has routes
        assert len(app.routes) > 0
        print(f"✓ App has {len(app.routes)} registered routes")
        
    except ImportError as e:
        print(f"✗ Main app import error: {e}")
        return False
    except AssertionError as e:
        print(f"✗ Main app validation error: {e}")
        return False
    
    return True

def main():
    """Run all verification tests"""
    print("=" * 50)
    print("FastAPI v1.1 Verification Script")
    print("=" * 50)
    
    tests = [
        test_basic_imports,
        test_voucher_service_import,
        test_api_imports,
        test_main_app
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print("Test failed!")
        except Exception as e:
            print(f"✗ Test error: {e}")
    
    print("\n" + "=" * 50)
    print(f"Verification Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All verification tests passed!")
        return 0
    else:
        print("✗ Some tests failed - check the output above")
        return 1

if __name__ == "__main__":
    sys.exit(main())