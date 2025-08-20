# Simple syntax validation test for ledger implementation
print("Testing ledger implementation syntax...")

# Check that files exist and have basic syntax
import os

ledger_files = [
    "app/schemas/ledger.py",
    "app/services/ledger_service.py", 
    "tests/test_ledger_endpoints.py",
    "tests/test_ledger_service.py"
]

for file_path in ledger_files:
    if os.path.exists(file_path):
        print(f"✅ {file_path} exists")
        # Basic syntax check by attempting to compile
        try:
            with open(file_path, 'r') as f:
                compile(f.read(), file_path, 'exec')
            print(f"✅ {file_path} has valid syntax")
        except SyntaxError as e:
            print(f"❌ {file_path} has syntax error: {e}")
            exit(1)
    else:
        print(f"❌ {file_path} not found")
        exit(1)

print("✅ All ledger implementation files have valid syntax!")

# Check API endpoints are added to reports.py
with open("app/api/reports.py", 'r') as f:
    content = f.read()
    if "/complete-ledger" in content and "/outstanding-ledger" in content:
        print("✅ Ledger endpoints added to reports.py")
    else:
        print("❌ Ledger endpoints not found in reports.py")
        exit(1)

print("🎉 Ledger implementation syntax validation passed!")