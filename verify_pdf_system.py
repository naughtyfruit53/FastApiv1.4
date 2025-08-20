#!/usr/bin/env python3
"""
PDF Voucher System Verification Script

This script verifies that the professional PDF voucher system is properly implemented
and tests the API endpoints.
"""

import requests
import sys
import json
from datetime import datetime

def test_api_endpoints():
    """Test the PDF-related API endpoints"""
    base_url = "http://localhost:8000"
    
    print("🔍 Testing PDF Voucher System API Endpoints...")
    print("=" * 50)
    
    # Test 1: Check if company branding endpoint exists
    print("1. Testing Company Branding Endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v1/company/branding")
        if response.status_code == 401:
            print("   ✅ Endpoint exists and requires authentication (as expected)")
        elif response.status_code == 200:
            print("   ⚠️  Endpoint accessible without auth (security concern)")
        else:
            print(f"   ❌ Unexpected status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Endpoint not accessible: {e}")
    
    # Test 2: Check if audit endpoint exists
    print("\n2. Testing Audit Logging Endpoint...")
    try:
        test_data = {
            "action": "pdf_generated",
            "voucher_type": "test-voucher",
            "voucher_number": "TEST001",
            "timestamp": datetime.now().isoformat()
        }
        response = requests.post(f"{base_url}/api/v1/audit/pdf-generation", json=test_data)
        if response.status_code == 401:
            print("   ✅ Endpoint exists and requires authentication (as expected)")
        elif response.status_code == 200:
            print("   ⚠️  Endpoint accessible without auth (security concern)")
        else:
            print(f"   ❌ Unexpected status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Endpoint not accessible: {e}")
    
    # Test 3: Check if routes are registered
    print("\n3. Testing Route Registration...")
    try:
        response = requests.get(f"{base_url}/routes")
        if response.status_code == 200:
            routes = response.json().get("routes", [])
            pdf_routes = [route for route in routes if "company/branding" in route or "audit/pdf" in route]
            if pdf_routes:
                print("   ✅ PDF-related routes are registered:")
                for route in pdf_routes:
                    print(f"      - {route}")
            else:
                print("   ❌ PDF-related routes not found in registered routes")
        else:
            print(f"   ❌ Could not retrieve routes: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Routes endpoint not accessible: {e}")
    
    print("\n" + "=" * 50)

def check_frontend_files():
    """Check if frontend files have been properly updated"""
    print("📁 Checking Frontend File Updates...")
    print("=" * 50)
    
    updated_files = [
        "frontend/src/services/pdfService.ts",
        "frontend/src/pages/vouchers/Financial-Vouchers/payment-voucher.tsx",
        "frontend/src/pages/vouchers/Financial-Vouchers/receipt-voucher.tsx",
        "frontend/src/pages/vouchers/Sales-Vouchers/sales-voucher.tsx",
        "frontend/src/pages/vouchers/Pre-Sales-Voucher/proforma-invoice.tsx",
        "frontend/src/pages/vouchers/Financial-Vouchers/journal-voucher.tsx",
        "frontend/src/pages/vouchers/Purchase-Vouchers/purchase-voucher.tsx"
    ]
    
    for file_path in updated_files:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                if 'pdfService' in content and 'generateVoucherPDF' in content:
                    print(f"   ✅ {file_path} - Updated to use professional PDF service")
                elif 'generatePDF' in content:
                    if 'jsPDF' in content and 'pdfService' not in content:
                        print(f"   ⚠️  {file_path} - Still using old PDF system")
                    else:
                        print(f"   ✅ {file_path} - Updated (partial)")
                else:
                    print(f"   ❓ {file_path} - No PDF generation found")
        except FileNotFoundError:
            print(f"   ❌ {file_path} - File not found")
        except Exception as e:
            print(f"   ❌ {file_path} - Error reading file: {e}")
    
    print("\n" + "=" * 50)

def check_backend_files():
    """Check if backend files are properly implemented"""
    print("🔧 Checking Backend Implementation...")
    print("=" * 50)
    
    backend_files = [
        "app/api/v1/company_branding.py",
        "app/main.py"
    ]
    
    for file_path in backend_files:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                if file_path.endswith('company_branding.py'):
                    if 'get_company_branding' in content and 'log_pdf_generation' in content:
                        print(f"   ✅ {file_path} - Company branding API implemented")
                    else:
                        print(f"   ❌ {file_path} - Missing required functions")
                elif file_path.endswith('main.py'):
                    if 'company_branding' in content:
                        print(f"   ✅ {file_path} - Company branding router registered")
                    else:
                        print(f"   ⚠️  {file_path} - Company branding router not found")
        except FileNotFoundError:
            print(f"   ❌ {file_path} - File not found")
        except Exception as e:
            print(f"   ❌ {file_path} - Error reading file: {e}")
    
    print("\n" + "=" * 50)

def check_tests():
    """Check if tests are implemented"""
    print("🧪 Checking Test Implementation...")
    print("=" * 50)
    
    test_files = [
        "tests/test_pdf_generation.py",
        "tests/pdfService.test.ts"
    ]
    
    for file_path in test_files:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                if 'test_' in content or 'describe(' in content:
                    print(f"   ✅ {file_path} - Test file implemented")
                else:
                    print(f"   ❌ {file_path} - Invalid test file")
        except FileNotFoundError:
            print(f"   ❌ {file_path} - File not found")
        except Exception as e:
            print(f"   ❌ {file_path} - Error reading file: {e}")
    
    print("\n" + "=" * 50)

def check_documentation():
    """Check if documentation is complete"""
    print("📚 Checking Documentation...")
    print("=" * 50)
    
    doc_files = [
        "PDF_VOUCHER_SYSTEM_DOCUMENTATION.md",
        "PDF_MIGRATION_GUIDE.md"
    ]
    
    for file_path in doc_files:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                if len(content) > 1000:  # Reasonable documentation length
                    print(f"   ✅ {file_path} - Documentation complete")
                else:
                    print(f"   ⚠️  {file_path} - Documentation seems incomplete")
        except FileNotFoundError:
            print(f"   ❌ {file_path} - File not found")
        except Exception as e:
            print(f"   ❌ {file_path} - Error reading file: {e}")
    
    print("\n" + "=" * 50)

def main():
    """Main verification function"""
    print("🚀 PDF Voucher System Verification")
    print("=" * 50)
    print("This script verifies the implementation of the professional PDF voucher system.")
    print("Make sure the FastAPI server is running on localhost:8000 for API tests.\n")
    
    # Run all checks
    check_frontend_files()
    check_backend_files()
    check_tests()
    check_documentation()
    test_api_endpoints()
    
    print("🎯 Verification Summary")
    print("=" * 50)
    print("Review the results above to ensure all components are properly implemented.")
    print("Green checkmarks (✅) indicate successful implementation.")
    print("Yellow warnings (⚠️) indicate areas that may need attention.")
    print("Red X marks (❌) indicate issues that need to be resolved.")
    print("\nFor issues, refer to the PDF_VOUCHER_SYSTEM_DOCUMENTATION.md file.")

if __name__ == "__main__":
    main()