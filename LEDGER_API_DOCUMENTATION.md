# Ledger API Documentation

## Overview

The Ledger API provides comprehensive financial reporting capabilities for the ERP system, allowing users to view complete transaction histories and outstanding balances across vendors and customers.

## Endpoints

### 1. Complete Ledger

**Endpoint:** `GET /api/v1/reports/complete-ledger`

**Description:** Returns all debit/credit account transactions for the organization with detailed filtering capabilities.

**Access Control:** Super Admin, Admin, and Standard User (with access)

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `start_date` | date | No | None | Start date for filtering (YYYY-MM-DD) |
| `end_date` | date | No | None | End date for filtering (YYYY-MM-DD) |
| `account_type` | string | No | "all" | Account type filter: "vendor", "customer", "all" |
| `account_id` | integer | No | None | Specific vendor/customer ID |
| `voucher_type` | string | No | "all" | Voucher type: "purchase_voucher", "sales_voucher", "payment_voucher", "receipt_voucher", "debit_note", "credit_note", "all" |

#### Example Request

```bash
GET /api/v1/reports/complete-ledger?start_date=2024-01-01&end_date=2024-12-31&account_type=vendor&voucher_type=payment_voucher
Authorization: Bearer <token>
```

#### Example Response

```json
{
  "transactions": [
    {
      "id": 1,
      "voucher_type": "purchase_voucher",
      "voucher_number": "PV001",
      "date": "2024-06-15T10:30:00Z",
      "account_type": "vendor",
      "account_id": 1,
      "account_name": "ABC Suppliers",
      "debit_amount": 10000.00,
      "credit_amount": 0.00,
      "balance": 10000.00,
      "description": "Purchase of raw materials",
      "reference": "PO-2024-001",
      "status": "confirmed"
    },
    {
      "id": 2,
      "voucher_type": "payment_voucher",
      "voucher_number": "PAY001",
      "date": "2024-06-20T14:15:00Z",
      "account_type": "vendor",
      "account_id": 1,
      "account_name": "ABC Suppliers",
      "debit_amount": 0.00,
      "credit_amount": 6000.00,
      "balance": 4000.00,
      "description": "Partial payment",
      "reference": "BANK-TXN-001",
      "status": "confirmed"
    }
  ],
  "summary": {
    "transaction_count": 2,
    "accounts_involved": 1,
    "date_range": {
      "start_date": "2024-06-15T10:30:00Z",
      "end_date": "2024-06-20T14:15:00Z"
    },
    "currency": "INR"
  },
  "filters_applied": {
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "account_type": "vendor",
    "account_id": null,
    "voucher_type": "all"
  },
  "total_debit": 10000.00,
  "total_credit": 6000.00,
  "net_balance": -4000.00
}
```

### 2. Outstanding Ledger

**Endpoint:** `GET /api/v1/reports/outstanding-ledger`

**Description:** Returns only open balances (payable or receivable) by account with proper sign convention.

**Access Control:** Super Admin, Admin, and Standard User (with access)

**Sign Convention:**
- **Negative amounts (-) **: Money payable TO vendors
- **Positive amounts (+) **: Money receivable FROM customers

#### Parameters

Same as Complete Ledger endpoint.

#### Example Request

```bash
GET /api/v1/reports/outstanding-ledger?account_type=all
Authorization: Bearer <token>
```

#### Example Response

```json
{
  "outstanding_balances": [
    {
      "account_type": "vendor",
      "account_id": 1,
      "account_name": "ABC Suppliers",
      "outstanding_amount": -4000.00,
      "last_transaction_date": "2024-06-20T14:15:00Z",
      "transaction_count": 5,
      "contact_info": "9876543210"
    },
    {
      "account_type": "customer", 
      "account_id": 1,
      "account_name": "XYZ Industries",
      "outstanding_amount": 15000.00,
      "last_transaction_date": "2024-06-18T09:45:00Z",
      "transaction_count": 3,
      "contact_info": "8765432109"
    }
  ],
  "summary": {
    "total_accounts": 2,
    "accounts_with_balance": 2,
    "vendor_accounts": 1,
    "customer_accounts": 1,
    "currency": "INR"
  },
  "filters_applied": {
    "start_date": null,
    "end_date": null,
    "account_type": "all",
    "account_id": null,
    "voucher_type": "all"
  },
  "total_payable": -4000.00,
  "total_receivable": 15000.00,
  "net_outstanding": 11000.00
}
```

## Business Logic

### Complete Ledger Calculations

The complete ledger shows the running balance for each account based on transaction types:

**For Vendors:**
- **Debit entries** (increase payable): Purchase vouchers, vendor debit notes
- **Credit entries** (decrease payable): Payment vouchers, vendor credit notes

**For Customers:**
- **Credit entries** (increase receivable): Sales vouchers, customer credit notes  
- **Debit entries** (decrease receivable): Receipt vouchers, customer debit notes

### Outstanding Balance Calculations

Outstanding balances are calculated by summing all transactions for each account:

**Vendor Balances:**
- Positive internal balance = Amount payable to vendor
- Displayed as negative value to indicate money owed TO vendor

**Customer Balances:**
- Positive internal balance = Amount receivable from customer
- Displayed as positive value to indicate money owed BY customer

### Multi-Tenant Security

All ledger endpoints enforce strict organization-level data isolation:

- Users can only access their organization's data
- App Super Admins are blocked from accessing organization data
- Tenant filtering applied to all database queries
- Permission validation for role-based access

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Insufficient permissions to access ledger reports"
}
```

### 403 Organization Access Denied
```json
{
  "detail": "App super administrators cannot access organization-specific data. Use license management features instead."
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["query", "account_type"],
      "msg": "value is not a valid enumeration member",
      "type": "type_error.enum"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Failed to generate complete ledger report"
}
```

## Usage Examples

### Get All Vendor Transactions
```bash
curl -X GET "/api/v1/reports/complete-ledger?account_type=vendor" \
  -H "Authorization: Bearer <token>"
```

### Get Outstanding Customer Balances
```bash
curl -X GET "/api/v1/reports/outstanding-ledger?account_type=customer" \
  -H "Authorization: Bearer <token>"
```

### Get Specific Account History
```bash
curl -X GET "/api/v1/reports/complete-ledger?account_type=vendor&account_id=5&start_date=2024-01-01" \
  -H "Authorization: Bearer <token>"
```

### Get Payment Vouchers Only
```bash
curl -X GET "/api/v1/reports/complete-ledger?voucher_type=payment_voucher" \
  -H "Authorization: Bearer <token>"
```

## Implementation Notes

- All amounts are returned as decimal values for precision
- Dates are in ISO 8601 format with timezone information
- Currency is fixed to INR but extensible for future multi-currency support
- Running balances are calculated in chronological order
- Outstanding balances include contact information for easy follow-up
- Transaction counts help identify account activity levels

## Performance Considerations

- Large date ranges may impact performance
- Consider pagination for organizations with high transaction volumes
- Database indexes on organization_id, date, and account fields optimize query performance
- Caching can be implemented for frequently accessed outstanding balances