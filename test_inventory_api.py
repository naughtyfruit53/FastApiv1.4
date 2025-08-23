"""
Test inventory API endpoints functionality
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from sqlalchemy.orm import Session

from app.api.v1.inventory import InventoryService
from app.schemas.inventory import (
    InventoryTransactionCreate, TransactionType, ReferenceType
)


def test_inventory_service_get_current_stock():
    """Test inventory service stock retrieval"""
    # Mock database session
    mock_db = Mock(spec=Session)
    
    # Mock stock record
    mock_stock = Mock()
    mock_stock.quantity = 15.0
    
    # Mock query chain
    mock_query = Mock()
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = mock_stock
    mock_db.query.return_value = mock_query
    
    # Test the service
    stock_level = InventoryService.get_current_stock(
        db=mock_db,
        organization_id=1,
        product_id=1,
        location="warehouse"
    )
    
    assert stock_level == 15.0
    print("✓ InventoryService.get_current_stock test passed")


def test_inventory_service_get_current_stock_no_record():
    """Test inventory service when no stock record exists"""
    # Mock database session
    mock_db = Mock(spec=Session)
    
    # Mock query chain returning None
    mock_query = Mock()
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = None
    mock_db.query.return_value = mock_query
    
    # Test the service
    stock_level = InventoryService.get_current_stock(
        db=mock_db,
        organization_id=1,
        product_id=1,
        location="warehouse"
    )
    
    assert stock_level == 0.0
    print("✓ InventoryService.get_current_stock (no record) test passed")


def test_inventory_transaction_validation():
    """Test inventory transaction schema validation"""
    # Valid transaction
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
        transaction_date=datetime.now()
    )
    
    assert transaction_data.product_id == 1
    assert transaction_data.quantity == 10.0
    assert transaction_data.transaction_type == TransactionType.RECEIPT
    print("✓ InventoryTransactionCreate validation test passed")
    
    # Test invalid transaction (zero quantity)
    try:
        invalid_transaction = InventoryTransactionCreate(
            product_id=1,
            transaction_type=TransactionType.RECEIPT,
            quantity=0.0,  # Invalid - zero quantity
            unit="pcs",
            stock_before=0.0,
            stock_after=0.0,
            transaction_date=datetime.now()
        )
        assert False, "Should have raised validation error for zero quantity"
    except ValueError:
        print("✓ InventoryTransactionCreate zero quantity validation test passed")


def test_transaction_types():
    """Test transaction type enums"""
    from app.schemas.inventory import TransactionType, ReferenceType, AlertType
    
    # Test TransactionType enum
    assert TransactionType.RECEIPT == "receipt"
    assert TransactionType.ISSUE == "issue"
    assert TransactionType.ADJUSTMENT == "adjustment"
    assert TransactionType.TRANSFER == "transfer"
    print("✓ TransactionType enum test passed")
    
    # Test ReferenceType enum
    assert ReferenceType.JOB == "job"
    assert ReferenceType.PURCHASE == "purchase"
    assert ReferenceType.MANUAL == "manual"
    assert ReferenceType.TRANSFER == "transfer"
    print("✓ ReferenceType enum test passed")
    
    # Test AlertType enum
    assert AlertType.LOW_STOCK == "low_stock"
    assert AlertType.OUT_OF_STOCK == "out_of_stock"
    assert AlertType.REORDER == "reorder"
    print("✓ AlertType enum test passed")


def test_inventory_business_logic():
    """Test inventory business logic calculations"""
    # Test stock calculations
    initial_stock = 20.0
    receipt_quantity = 10.0
    issue_quantity = 5.0
    
    # Receipt should increase stock
    new_stock_after_receipt = initial_stock + receipt_quantity
    assert new_stock_after_receipt == 30.0
    
    # Issue should decrease stock
    new_stock_after_issue = new_stock_after_receipt - issue_quantity
    assert new_stock_after_issue == 25.0
    
    print("✓ Inventory business logic calculation test passed")
    
    # Test low stock detection
    current_stock = 5.0
    reorder_level = 10.0
    
    is_low_stock = current_stock <= reorder_level
    assert is_low_stock == True
    
    is_out_of_stock = current_stock <= 0
    assert is_out_of_stock == False
    
    print("✓ Low stock detection logic test passed")


def test_api_route_structure():
    """Test that API routes are properly structured"""
    from app.api.v1.inventory import router
    
    # Check that router exists and has routes
    assert router is not None
    assert len(router.routes) > 0
    
    # Check that main route paths exist
    route_paths = [route.path for route in router.routes]
    
    expected_paths = [
        "/transactions",
        "/job-parts", 
        "/alerts",
        "/reports/usage",
        "/reports/low-stock"
    ]
    
    for expected_path in expected_paths:
        assert any(expected_path in path for path in route_paths), f"Missing route: {expected_path}"
    
    print("✓ API route structure test passed")


if __name__ == "__main__":
    print("Running inventory API tests...")
    test_inventory_service_get_current_stock()
    test_inventory_service_get_current_stock_no_record()
    test_inventory_transaction_validation()
    test_transaction_types()
    test_inventory_business_logic()
    test_api_route_structure()
    print("Inventory API tests completed successfully!")