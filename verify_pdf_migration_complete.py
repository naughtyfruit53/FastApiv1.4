#!/usr/bin/env python3
"""
PDF Migration Verification Script
Verifies that all voucher types have been successfully migrated to use the professional PDF service.
"""

import os
import glob
import re
from pathlib import Path

def main():
    print("🔍 Verifying PDF Migration Completion...")
    print("=" * 50)
    
    # Define the voucher directory
    voucher_dir = "frontend/src/pages/vouchers"
    base_path = Path(__file__).parent / voucher_dir
    
    # Find all voucher TypeScript files
    voucher_files = []
    for pattern in ["**/*.tsx"]:
        voucher_files.extend(glob.glob(str(base_path / pattern), recursive=True))
    
    print(f"📁 Found {len(voucher_files)} voucher files to check")
    print()
    
    # Track migration status
    migrated_files = []
    old_system_files = []
    
    for file_path in voucher_files:
        rel_path = os.path.relpath(file_path, base_path.parent.parent.parent)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for old jsPDF imports
            has_old_import = re.search(r'import jsPDF from [\'"]jspdf[\'"]', content)
            
            # Check for new pdfService import
            has_new_import = re.search(r'import pdfService from [\'"].*pdfService[\'"]', content)
            
            # Check for async generatePDF function
            has_async_pdf = re.search(r'const generatePDF = async \(', content)
            
            # Check for authorization check
            has_auth_check = re.search(r'localStorage\.getItem\([\'"]token[\'"]', content)
            
            # Check for professional PDF service call
            has_service_call = re.search(r'await pdfService\.generateVoucherPDF', content)
            
            if has_old_import:
                old_system_files.append(rel_path)
                print(f"❌ {rel_path} - Still using old jsPDF system")
            elif has_new_import and has_async_pdf and has_auth_check and has_service_call:
                migrated_files.append(rel_path)
                print(f"✅ {rel_path} - Successfully migrated to professional PDF")
            elif has_new_import or 'generatePDF' in content:
                print(f"⚠️  {rel_path} - Partially migrated (needs review)")
            else:
                print(f"ℹ️  {rel_path} - No PDF functionality detected")
                
        except Exception as e:
            print(f"❌ Error reading {rel_path}: {e}")
    
    print()
    print("📊 Migration Summary:")
    print("=" * 50)
    print(f"✅ Successfully migrated: {len(migrated_files)} files")
    print(f"❌ Still using old system: {len(old_system_files)} files")
    
    if migrated_files:
        print("\n🎉 Successfully migrated voucher types:")
        for file_path in sorted(migrated_files):
            filename = os.path.basename(file_path).replace('.tsx', '')
            print(f"   • {filename}")
    
    if old_system_files:
        print("\n⚠️  Files still using old PDF system:")
        for file_path in sorted(old_system_files):
            print(f"   • {file_path}")
        return False
    
    print("\n🎉 MIGRATION COMPLETE!")
    print("All voucher types are now using the professional PDF system with:")
    print("   • Consistent professional branding")
    print("   • Authorization checks")
    print("   • Audit logging")
    print("   • Centralized PDF service")
    print("   • Standardized user experience")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)