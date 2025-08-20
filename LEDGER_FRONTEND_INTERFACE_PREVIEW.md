# Ledger Frontend Interface Preview

## Tab Structure (Reports Page)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Reports & Analytics                                                         │
│                                                                             │
│ ┌─Overview─┐ ┌─Sales Report─┐ ┌─Purchase Report─┐ ┌─Inventory─┐ ┌─Pending─┐ ┌─Ledger─┐ │
│ │          │ │              │ │                │ │ Report    │ │ Orders  │ │(Active)│ │
│ └──────────┘ └──────────────┘ └────────────────┘ └───────────┘ └─────────┘ └────────┘ │
└─────────────────────────────────────────────────────────────────────────────┐

## Ledger Tab Interface

┌─────────────────────────────────────────────────────────────────────────────┐
│ 🔍 Ledger Report                                                            │
│                                                                             │
│ ┌─[ Complete Ledger  🔘─○  Outstanding Ledger ]─┐                          │
│                                                                             │
│ Filters:                                                                    │
│ ┌─Start Date─┐ ┌─End Date───┐ ┌─Account Type─┐ ┌─Voucher Type─┐ ┌─Refresh─┐ │
│ │2024-01-01  │ │2024-12-31  │ │All ▼        │ │All ▼        │ │🔄      │ │
│ └────────────┘ └────────────┘ └─────────────┘ └─────────────┘ └────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘

## Complete Ledger View
┌─────────────────────────────────────────────────────────────────────────────┐
│ Summary                                                                     │
│ Total Transactions: 245  |  Total Debit: ₹1,25,000  |  Total Credit: ₹98,000│
│ Net Balance: ₹27,000                                                        │
│                                                                             │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ Date      │Voucher Type│Voucher # │Account      │Debit   │Credit  │Balance│ │
│ ├─────────────────────────────────────────────────────────────────────────┤ │
│ │15/01/24   │SALES       │SV001     │ABC Corp     │   -    │ ₹5,000 │₹5,000 │ │
│ │12/01/24   │PURCHASE    │PV002     │XYZ Vendor   │₹3,000  │   -    │₹2,000 │ │
│ │10/01/24   │PAYMENT     │PY003     │Bank Account │   -    │₹1,500  │₹3,500 │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘

## Outstanding Ledger View  
┌─────────────────────────────────────────────────────────────────────────────┐
│ Outstanding Balances Summary                                                │
│ Total Accounts: 15  |  🔴 Total Payable: ₹45,000  |  🟢 Total Receivable: ₹67,000│
│ Net Outstanding: ₹22,000                                                    │
│                                                                             │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │Account Type│Account Name    │Outstanding Amount   │Last Transaction│Count│ │
│ ├─────────────────────────────────────────────────────────────────────────┤ │
│ │[CUSTOMER] │ABC Corporation │🟢 ₹15,000 (Receivable)│   15/01/24    │  5  │ │
│ │[VENDOR]   │XYZ Supplies   │🔴 ₹8,000 (Payable)    │   12/01/24    │  3  │ │
│ │[CUSTOMER] │DEF Industries  │🟢 ₹22,000 (Receivable)│   18/01/24    │  8  │ │
│ │[VENDOR]   │PQR Traders     │🔴 ₹12,000 (Payable)   │   10/01/24    │  2  │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘

## Permission Denied View (for unauthorized users)
┌─────────────────────────────────────────────────────────────────────────────┐
│ ⚠️  You don't have permission to access the Ledger report.                 │
│     Contact your administrator for access.                                 │
└─────────────────────────────────────────────────────────────────────────────┘

## Key Features Highlighted:

1. **Toggle Switch**: 🔘─○ Easy switching between Complete and Outstanding views
2. **Color Coding**: 
   - 🟢 Green for Receivables (money owed TO company)
   - 🔴 Red for Payables (money owed BY company)
3. **Responsive Filters**: All filters update data in real-time
4. **Visual Chips**: [CUSTOMER] and [VENDOR] badges for easy identification
5. **Currency Formatting**: Proper ₹ symbol and comma separators
6. **Date Formatting**: Consistent DD/MM/YY format
7. **Summary Stats**: Clear financial overview at the top
8. **Accessibility**: Proper labels and screen reader support

## Mobile Responsive Behavior:
- Filters stack vertically on smaller screens
- Tables become horizontally scrollable
- Touch-friendly toggle switches and buttons
- Simplified column layout for mobile viewing

## Error States:
- "Loading..." messages during API calls
- "No data available" when no results found
- Network error messages with retry options
- Permission denied alerts for unauthorized access