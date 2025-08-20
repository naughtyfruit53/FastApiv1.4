# PDF Migration Utility for Remaining Voucher Types

This utility helps identify and migrate remaining voucher types to use the new professional PDF system.

## Voucher Types Status

### ✅ Completed
- Payment Voucher (`payment-voucher.tsx`)
- Receipt Voucher (`receipt-voucher.tsx`)
- Sales Voucher (`sales-voucher.tsx`)
- Proforma Invoice (`proforma-invoice.tsx`)
- Journal Voucher (`journal-voucher.tsx`)
- Purchase Voucher (`purchase-voucher.tsx`)
- Contra Voucher (`contra-voucher.tsx`)
- Non-Sales Credit Note (`non-sales-credit-note.tsx`)
- Purchase Order (`purchase-order.tsx`)
- GRN (`grn.tsx`)
- Purchase Return (`purchase-return.tsx`)
- Quotation (`quotation.tsx`)
- Sales Order (`sales-order.tsx`)
- Delivery Challan (`delivery-challan.tsx`)
- Sales Return (`sales-return.tsx`)

### 🎉 All voucher types have been successfully migrated to the professional PDF system!

## Quick Migration Steps

For each remaining voucher type:

### 1. Update Imports
Replace:
```typescript
import jsPDF from 'jspdf';
```

With:
```typescript
import pdfService from '../../../services/pdfService';
```

### 2. Replace generatePDF Function
Replace the existing `generatePDF` function with:

```typescript
const generatePDF = async (voucherData: any) => {
  try {
    // Check authorization before generating PDF
    const token = localStorage.getItem('token');
    if (!token) {
      alert('You must be logged in to generate PDFs');
      return;
    }

    // Prepare voucher data for the professional PDF service
    const pdfVoucherData = {
      voucher_number: voucherData.voucher_number,
      date: voucherData.date,
      reference: voucherData.reference,
      notes: voucherData.notes,
      total_amount: voucherData.total_amount || 0,
      // Add voucher-specific fields here
      items: voucherData.items || [], // Include if voucher has items
      party: voucherData.customer || voucherData.vendor // Include party info
    };

    const pdfOptions = {
      voucherType: 'voucher-type-slug', // Replace with actual voucher type
      voucherTitle: 'VOUCHER TITLE', // Replace with display title
      filename: `VoucherName_${voucherData.voucher_number?.replace(/[^a-zA-Z0-9]/g, '_') || 'Unknown'}.pdf`,
      showItems: true, // Set to true if voucher has line items
      showTaxDetails: true // Set to true if voucher has tax calculations
    };

    await pdfService.generateVoucherPDF(pdfVoucherData, pdfOptions);
  } catch (error) {
    console.error('Error generating PDF:', error);
    alert('Failed to generate PDF. Please try again.');
  }
};
```

### 3. Voucher-Specific Configuration

#### For Vouchers with Items (Sales, Purchase, Orders)
```typescript
showItems: true,
showTaxDetails: true,
items: voucherData.items || []
```

#### For Simple Vouchers (Payments, Receipts)
```typescript
showItems: false,
showTaxDetails: false
```

#### For Journal/Accounting Vouchers
```typescript
showItems: true, // Convert journal entries to items format
showTaxDetails: false,
items: journalEntries.map((entry, index) => ({
  description: entry.account || `Entry ${index + 1}`,
  quantity: 1,
  unit: 'Entry',
  unit_price: entry.debit || entry.credit || 0,
  total_amount: entry.debit || entry.credit || 0,
  hsn_code: entry.debit ? 'DR' : 'CR'
}))
```

## Voucher Type Configuration Reference

| Voucher Type | showItems | showTaxDetails | voucherType | voucherTitle |
|--------------|-----------|----------------|-------------|--------------|
| Contra Voucher | false | false | 'contra-voucher' | 'CONTRA VOUCHER' |
| Credit Note | true | true | 'credit-note' | 'CREDIT NOTE' |
| Purchase Order | true | true | 'purchase-order' | 'PURCHASE ORDER' |
| GRN | true | false | 'grn' | 'GOODS RECEIPT NOTE' |
| Purchase Return | true | true | 'purchase-return' | 'PURCHASE RETURN' |
| Quotation | true | true | 'quotation' | 'QUOTATION' |
| Sales Order | true | true | 'sales-order' | 'SALES ORDER' |
| Delivery Challan | true | false | 'delivery-challan' | 'DELIVERY CHALLAN' |
| Sales Return | true | true | 'sales-return' | 'SALES RETURN' |

## Testing Migration

After migrating each voucher type:

1. **Test PDF Generation**: Create a test voucher and generate PDF
2. **Verify Content**: Check that all relevant information appears correctly
3. **Test Authorization**: Ensure PDF generation requires login
4. **Check Filename**: Verify meaningful filename is generated
5. **Review Layout**: Ensure professional appearance

## Batch Migration Script

For quick migration of multiple files:

```bash
#!/bin/bash
# migrate_vouchers.sh

VOUCHER_TYPES=(
  "contra-voucher"
  "non-sales-credit-note"
  "purchase-order"
  "grn"
  "purchase-return"
  "quotation"
  "sales-order"
  "delivery-challan"
  "sales-return"
)

for voucher in "${VOUCHER_TYPES[@]}"; do
  echo "Migrating $voucher..."
  # Add migration logic here
  # This would be customized based on specific needs
done
```

## Validation Checklist

For each migrated voucher:

- [ ] Import statement updated
- [ ] generatePDF function replaced with async version
- [ ] Authorization check added
- [ ] Voucher data properly mapped
- [ ] PDF options configured correctly
- [ ] Error handling in place
- [ ] Testing completed
- [ ] Documentation updated

## Support

If you encounter issues during migration:
1. Check the completed voucher types as examples
2. Verify the PDF service import path is correct
3. Ensure voucher data structure matches expected format
4. Test with sample data first
5. Check browser console for error messages

The professional PDF system is designed to be flexible and work with various voucher structures while maintaining consistent professional appearance across all document types.