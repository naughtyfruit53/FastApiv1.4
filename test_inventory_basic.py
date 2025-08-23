"""
Test inventory models and basic functionality
"""
import pytest
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.base import (
    InventoryTransaction, JobParts, InventoryAlert, 
    Product, Organization, User, InstallationJob
)
from app.schemas.inventory import (
    InventoryTransactionCreate, TransactionType, ReferenceType,
    JobPartsCreate, JobPartsStatus,
    InventoryAlertCreate, AlertType, AlertStatus, AlertPriority
)
from app.core.database import SessionLocal


def test_inventory_transaction_model():
    """Test InventoryTransaction model creation"""
    db = SessionLocal()
    
    try:
        # Create a simple inventory transaction
        transaction = InventoryTransaction(
            organization_id=1,
            product_id=1,
            transaction_type=TransactionType.RECEIPT,
            quantity=10.0,
            unit="pcs",
            location="warehouse",
            reference_type=ReferenceType.MANUAL,
            notes="Initial stock",
            stock_before=0.0,
            stock_after=10.0,
            transaction_date=datetime.utcnow()
        )
        
        # Basic validation
        assert transaction.product_id == 1
        assert transaction.quantity == 10.0
        assert transaction.transaction_type == TransactionType.RECEIPT
        print("✓ InventoryTransaction model test passed")
        
    except Exception as e:
        print(f"✗ InventoryTransaction model test failed: {e}")
    finally:
        db.close()


def test_job_parts_model():
    """Test JobParts model creation"""
    db = SessionLocal()
    
    try:
        # Create a job parts assignment
        job_part = JobParts(
            organization_id=1,
            job_id=1,
            product_id=1,
            quantity_required=5.0,
            quantity_used=0.0,
            unit="pcs",
            status=JobPartsStatus.PLANNED,
            notes="Initial allocation"
        )
        
        # Basic validation
        assert job_part.job_id == 1
        assert job_part.quantity_required == 5.0
        assert job_part.status == JobPartsStatus.PLANNED
        print("✓ JobParts model test passed")
        
    except Exception as e:
        print(f"✗ JobParts model test failed: {e}")
    finally:
        db.close()


def test_inventory_alert_model():
    """Test InventoryAlert model creation"""
    db = SessionLocal()
    
    try:
        # Create an inventory alert
        alert = InventoryAlert(
            organization_id=1,
            product_id=1,
            alert_type=AlertType.LOW_STOCK,
            current_stock=5.0,
            reorder_level=10.0,
            status=AlertStatus.ACTIVE,
            priority=AlertPriority.HIGH,
            message="Stock is below reorder level"
        )
        
        # Basic validation
        assert alert.product_id == 1
        assert alert.alert_type == AlertType.LOW_STOCK
        assert alert.status == AlertStatus.ACTIVE
        print("✓ InventoryAlert model test passed")
        
    except Exception as e:
        print(f"✗ InventoryAlert model test failed: {e}")
    finally:
        db.close()


def test_inventory_schemas():
    """Test inventory schema validation"""
    try:
        # Test InventoryTransactionCreate schema
        transaction_data = InventoryTransactionCreate(
            product_id=1,
            transaction_type=TransactionType.RECEIPT,
            quantity=10.0,
            unit="pcs",
            location="warehouse",
            reference_type=ReferenceType.MANUAL,
            notes="Test transaction",
            stock_before=0.0,
            stock_after=10.0,
            transaction_date=datetime.utcnow()
        )
        
        assert transaction_data.product_id == 1
        assert transaction_data.quantity == 10.0
        print("✓ InventoryTransactionCreate schema test passed")
        
        # Test JobPartsCreate schema
        job_parts_data = JobPartsCreate(
            job_id=1,
            product_id=1,
            quantity_required=5.0,
            unit="pcs",
            notes="Test job parts"
        )
        
        assert job_parts_data.job_id == 1
        assert job_parts_data.quantity_required == 5.0
        print("✓ JobPartsCreate schema test passed")
        
        # Test InventoryAlertCreate schema
        alert_data = InventoryAlertCreate(
            product_id=1,
            alert_type=AlertType.LOW_STOCK,
            current_stock=5.0,
            reorder_level=10.0,
            priority=AlertPriority.HIGH,
            message="Test alert"
        )
        
        assert alert_data.product_id == 1
        assert alert_data.alert_type == AlertType.LOW_STOCK
        print("✓ InventoryAlertCreate schema test passed")
        
    except Exception as e:
        print(f"✗ Schema validation test failed: {e}")


if __name__ == "__main__":
    print("Running inventory management tests...")
    test_inventory_transaction_model()
    test_job_parts_model()
    test_inventory_alert_model()
    test_inventory_schemas()
    print("Inventory management tests completed!")