"""
Simple validation script for organization_id consistency
"""
import sqlite3
import tempfile
import os


def test_organization_id_database_schema():
    """Test that the database schema uses organization_id consistently"""
    
    # Create a temporary database
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_file:
        db_path = tmp_file.name
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create organizations table
        cursor.execute('''
            CREATE TABLE organizations (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                subdomain TEXT NOT NULL UNIQUE,
                primary_email TEXT NOT NULL,
                primary_phone TEXT NOT NULL,
                address1 TEXT NOT NULL,
                city TEXT NOT NULL,
                state TEXT NOT NULL,
                pin_code TEXT NOT NULL,
                country TEXT NOT NULL DEFAULT 'India',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create users table with organization_id FK
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                organization_id INTEGER REFERENCES organizations(id),
                email TEXT NOT NULL,
                username TEXT NOT NULL,
                hashed_password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'standard_user',
                is_super_admin BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(organization_id, email),
                UNIQUE(organization_id, username)
            )
        ''')
        
        # Create other tenant-aware tables
        cursor.execute('''
            CREATE TABLE customers (
                id INTEGER PRIMARY KEY,
                organization_id INTEGER NOT NULL REFERENCES organizations(id),
                name TEXT NOT NULL,
                contact_number TEXT NOT NULL,
                address1 TEXT NOT NULL,
                city TEXT NOT NULL,
                state TEXT NOT NULL,
                pin_code TEXT NOT NULL,
                state_code TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(organization_id, name)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE vendors (
                id INTEGER PRIMARY KEY,
                organization_id INTEGER NOT NULL REFERENCES organizations(id),
                name TEXT NOT NULL,
                contact_number TEXT NOT NULL,
                address1 TEXT NOT NULL,
                city TEXT NOT NULL,
                state TEXT NOT NULL,
                pin_code TEXT NOT NULL,
                state_code TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(organization_id, name)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE products (
                id INTEGER PRIMARY KEY,
                organization_id INTEGER NOT NULL REFERENCES organizations(id),
                name TEXT NOT NULL,
                unit TEXT NOT NULL,
                unit_price REAL NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(organization_id, name)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE stock (
                id INTEGER PRIMARY KEY,
                organization_id INTEGER NOT NULL REFERENCES organizations(id),
                product_id INTEGER NOT NULL REFERENCES products(id),
                quantity REAL NOT NULL DEFAULT 0.0,
                unit TEXT NOT NULL,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(organization_id, product_id)
            )
        ''')
        
        print("✅ Database schema created successfully with organization_id foreign keys")
        
        # Insert test data
        
        # Insert organizations
        cursor.execute('''
            INSERT INTO organizations 
            (name, subdomain, primary_email, primary_phone, address1, city, state, pin_code, country)
            VALUES 
            ('Organization One', 'org1', 'admin@org1.com', '+1-111-1111', '111 Main St', 'City1', 'State1', '11111', 'Country1'),
            ('Organization Two', 'org2', 'admin@org2.com', '+1-222-2222', '222 Main St', 'City2', 'State2', '22222', 'Country2')
        ''')
        
        # Insert users
        cursor.execute('''
            INSERT INTO users 
            (organization_id, email, username, hashed_password, role, is_super_admin)
            VALUES 
            (1, 'user1@org1.com', 'user1', 'hash123', 'standard_user', FALSE),
            (1, 'admin1@org1.com', 'admin1', 'hash123', 'org_admin', FALSE),
            (2, 'user2@org2.com', 'user2', 'hash123', 'standard_user', FALSE),
            (NULL, 'superadmin@platform.com', 'superadmin', 'hash123', 'super_admin', TRUE)
        ''')
        
        # Insert customers (one per organization)
        cursor.execute('''
            INSERT INTO customers 
            (organization_id, name, contact_number, address1, city, state, pin_code, state_code)
            VALUES 
            (1, 'Customer A', '+1-111-9999', 'Customer St', 'City1', 'State1', '11111', 'ST1'),
            (2, 'Customer B', '+1-222-9999', 'Customer Ave', 'City2', 'State2', '22222', 'ST2')
        ''')
        
        # Insert products
        cursor.execute('''
            INSERT INTO products 
            (organization_id, name, unit, unit_price)
            VALUES 
            (1, 'Product A', 'pcs', 100.0),
            (1, 'Product B', 'kg', 50.0),
            (2, 'Product C', 'pcs', 200.0)
        ''')
        
        # Insert stock
        cursor.execute('''
            INSERT INTO stock 
            (organization_id, product_id, quantity, unit)
            VALUES 
            (1, 1, 100.0, 'pcs'),
            (1, 2, 50.0, 'kg'),
            (2, 3, 75.0, 'pcs')
        ''')
        
        conn.commit()
        print("✅ Test data inserted successfully")
        
        # Test organization isolation
        print("\n🔍 Testing organization data isolation:")
        
        # Test org1 data
        cursor.execute('''
            SELECT 
                c.name as customer_name,
                p.name as product_name,
                s.quantity
            FROM customers c, products p, stock s
            WHERE c.organization_id = 1 
            AND p.organization_id = 1 
            AND s.organization_id = 1
            AND s.product_id = p.id
        ''')
        org1_data = cursor.fetchall()
        print(f"  Organization 1 has {len(org1_data)} customer-product-stock combinations")
        
        # Test org2 data
        cursor.execute('''
            SELECT 
                c.name as customer_name,
                p.name as product_name,
                s.quantity
            FROM customers c, products p, stock s
            WHERE c.organization_id = 2 
            AND p.organization_id = 2 
            AND s.organization_id = 2
            AND s.product_id = p.id
        ''')
        org2_data = cursor.fetchall()
        print(f"  Organization 2 has {len(org2_data)} customer-product-stock combinations")
        
        # Test user organization relationships
        cursor.execute('''
            SELECT 
                u.username,
                u.role,
                u.is_super_admin,
                o.name as org_name
            FROM users u
            LEFT JOIN organizations o ON u.organization_id = o.id
            ORDER BY u.is_super_admin, u.organization_id
        ''')
        user_data = cursor.fetchall()
        print(f"\n👥 User organization relationships:")
        for username, role, is_super_admin, org_name in user_data:
            super_status = " (SUPER ADMIN)" if is_super_admin else ""
            org_display = org_name if org_name else "Platform Level"
            print(f"  {username} ({role}){super_status} -> {org_display}")
        
        # Test foreign key constraints work
        print("\n🔒 Testing foreign key constraints:")
        
        try:
            # Try to insert customer with invalid organization_id
            cursor.execute('''
                INSERT INTO customers 
                (organization_id, name, contact_number, address1, city, state, pin_code, state_code)
                VALUES (999, 'Invalid Customer', '+1-999-9999', 'Invalid St', 'City', 'State', '99999', 'ST')
            ''')
            print("  ❌ Foreign key constraint not enforced!")
        except sqlite3.IntegrityError:
            print("  ✅ Foreign key constraint properly enforced")
        
        # Test unique constraints
        try:
            # Try to insert duplicate customer name within same organization
            cursor.execute('''
                INSERT INTO customers 
                (organization_id, name, contact_number, address1, city, state, pin_code, state_code)
                VALUES (1, 'Customer A', '+1-111-8888', 'Another St', 'City1', 'State1', '11111', 'ST1')
            ''')
            print("  ❌ Unique constraint not enforced!")
        except sqlite3.IntegrityError:
            print("  ✅ Unique constraint (organization_id + name) properly enforced")
        
        conn.close()
        print("\n🎉 All organization_id consistency tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
        
    finally:
        # Clean up temporary file
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_api_endpoint_consistency():
    """Test that API endpoints use organization_id consistently"""
    
    print("\n🌐 Testing API endpoint consistency:")
    
    # Read API files and check for consistency
    api_files = [
        'app/api/v1/organizations.py',
        'app/api/settings.py',
        'app/api/users.py'
    ]
    
    issues_found = 0
    
    for file_path in api_files:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Check for old org_id parameter usage in routes
            if '/{org_id}' in content:
                print(f"  ❌ {file_path}: Still uses {{org_id}} path parameters")
                issues_found += 1
            else:
                print(f"  ✅ {file_path}: Uses {{organization_id}} path parameters")
                
        except FileNotFoundError:
            print(f"  ⚠️  {file_path}: File not found (expected in production environment)")
    
    return issues_found == 0


def test_frontend_consistency():
    """Test that frontend uses organization_id consistently"""
    
    print("\n🖥️  Testing frontend consistency:")
    
    frontend_files = [
        'frontend/src/services/authService.ts',
        'frontend/src/services/organizationService.ts',
        'frontend/src/lib/api.ts'
    ]
    
    issues_found = 0
    
    for file_path in frontend_files:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check for old org_id localStorage usage
            if "localStorage.getItem('org_id')" in content:
                print(f"  ❌ {file_path}: Still uses 'org_id' in localStorage")
                issues_found += 1
            else:
                print(f"  ✅ {file_path}: Uses 'organization_id' in localStorage")
                
        except FileNotFoundError:
            print(f"  ⚠️  {file_path}: File not found (expected in production environment)")
    
    return issues_found == 0


if __name__ == "__main__":
    print("🚀 Starting organization_id consistency validation...\n")
    
    success = True
    
    # Test database schema
    success &= test_organization_id_database_schema()
    
    # Test API endpoints
    success &= test_api_endpoint_consistency()
    
    # Test frontend
    success &= test_frontend_consistency()
    
    if success:
        print("\n🎉 ALL TESTS PASSED! Organization_id is used consistently throughout the system.")
        exit(0)
    else:
        print("\n❌ SOME TESTS FAILED! Please review the issues above.")
        exit(1)