# Professional PDF Voucher System Documentation

## Overview

The Professional PDF Voucher System provides a centralized, standardized approach to generating professional-looking PDFs for all voucher types in the FastAPI ERP application. The system includes company branding, authorization checks, audit logging, and consistent formatting across all voucher types.

## Features

### ✅ Professional Layout
- Clean, consistent design across all voucher types
- Company logo and branding support
- Professional header with company information
- Structured tables for item details
- Proper totals section with amount in words
- Authorized signatory section
- Footer with disclaimer and page numbers

### ✅ Company Branding
- Automatic company logo inclusion (when available)
- Company name, address, contact details
- GSTIN and other business information
- Fallback to generic branding when not configured
- Customizable color scheme support

### ✅ Authorization & Security
- Token-based authentication required
- Only logged-in users can generate PDFs
- Organization-level data scoping
- Audit logging for all PDF generation activities

### ✅ Multi-Voucher Support
- Payment Vouchers
- Receipt Vouchers  
- Sales Vouchers/Invoices
- Purchase Vouchers
- Proforma Invoices
- Journal Vouchers
- And all other voucher types

### ✅ Smart Data Handling
- Automatic party information detection
- Item tables for vouchers with line items
- Tax details and calculations
- Flexible field handling (optional fields supported)
- Meaningful PDF filenames (e.g., PaymentVoucher_001.pdf)

## Architecture

### Frontend Components

#### PDF Service (`frontend/src/services/pdfService.ts`)
- **ProfessionalPdfService**: Main class handling PDF generation
- **CompanyBranding Interface**: Type definitions for branding data
- **VoucherData Interface**: Standardized voucher data structure
- **PdfOptions Interface**: Configuration options for each voucher type

#### Key Methods
- `generateVoucherPDF()`: Main method for generating professional PDFs
- `loadCompanyBranding()`: Fetches company branding from API
- `drawHeader()`: Renders header with company info and logo
- `drawVoucherDetails()`: Renders voucher-specific information
- `drawItemsTable()`: Renders itemized table using autoTable
- `drawTotals()`: Renders total amounts and amount in words
- `numberToWords()`: Converts numbers to words in Indian format

### Backend Components

#### Company Branding API (`app/api/v1/company_branding.py`)
- `GET /api/v1/company/branding`: Returns company branding information
- `POST /api/v1/audit/pdf-generation`: Logs PDF generation for audit

#### Features
- Organization-scoped data access
- Fallback branding when company not configured
- Secure authentication requirement
- Comprehensive error handling

## Usage

### Basic Implementation

```typescript
import pdfService from '../../../services/pdfService';

const generatePDF = async (voucherData: any) => {
  try {
    const pdfVoucherData = {
      voucher_number: voucherData.voucher_number,
      date: voucherData.date,
      reference: voucherData.reference,
      notes: voucherData.notes,
      total_amount: voucherData.total_amount || 0,
      // Add voucher-specific fields
      payment_method: voucherData.payment_method,
      items: voucherData.items || [],
      party: voucherData.customer || voucherData.vendor
    };

    const pdfOptions = {
      voucherType: 'payment-voucher',
      voucherTitle: 'PAYMENT VOUCHER',
      filename: `PaymentVoucher_${voucherData.voucher_number}.pdf`,
      showItems: false,
      showTaxDetails: false
    };

    await pdfService.generateVoucherPDF(pdfVoucherData, pdfOptions);
  } catch (error) {
    console.error('Error generating PDF:', error);
    alert('Failed to generate PDF. Please try again.');
  }
};
```

### Voucher Types Configuration

| Voucher Type | showItems | showTaxDetails | Typical Use Case |
|--------------|-----------|----------------|------------------|
| Payment Voucher | false | false | Simple payment records |
| Receipt Voucher | false | false | Simple receipt records |
| Sales Voucher | true | true | Item sales with tax |
| Purchase Voucher | true | true | Item purchases with tax |
| Proforma Invoice | true | true | Quotations with items |
| Journal Voucher | false | false | Accounting entries |

## Customization

### Company Branding Setup

1. **Logo Upload**: Upload company logo to display in PDF header
2. **Company Information**: Configure company name, address, contact details
3. **GSTIN**: Add GST registration number
4. **Color Scheme**: Customize colors (future enhancement)

### Custom Fields

Add voucher-specific fields to the `VoucherData` interface:

```typescript
interface CustomVoucherData extends VoucherData {
  custom_field: string;
  special_instructions: string;
}
```

### Template Modifications

The PDF service supports template modifications through:
- Header customization
- Footer modifications  
- Color scheme changes
- Logo positioning adjustments

## API Endpoints

### Company Branding
```
GET /api/v1/company/branding
Authorization: Bearer <token>

Response:
{
  "name": "Company Name",
  "address": "Company Address",
  "contact_number": "1234567890",
  "email": "company@email.com",
  "website": "www.company.com",
  "logo_path": "/uploads/logo.png",
  "gstin": "GST123456789"
}
```

### Audit Logging
```
POST /api/v1/audit/pdf-generation
Authorization: Bearer <token>

Request:
{
  "action": "pdf_generated",
  "voucher_type": "payment-voucher",
  "voucher_number": "PV/2526/00000001",
  "timestamp": "2024-01-01T00:00:00Z"
}

Response:
{
  "status": "logged"
}
```

## Security Features

### Authorization
- JWT token validation required
- Organization-level data scoping
- User session verification

### Audit Trail
- All PDF generation activities logged
- User identification tracking
- Timestamp recording
- Voucher type and number logging

### Data Protection
- No sensitive data exposure in client code
- Secure API communication
- Organization data isolation

## Error Handling

### Frontend Error Handling
- Authentication token validation
- Network error recovery
- User-friendly error messages
- Graceful degradation

### Backend Error Handling
- Invalid request handling
- Database connection issues
- Missing company data fallback
- Audit logging failure tolerance

## Testing

### Automated Tests

#### Frontend Tests (`tests/pdfService.test.ts`)
- PDF generation functionality
- Company branding API integration
- Error handling scenarios
- Number-to-words conversion
- Authentication checks

#### Backend Tests (`tests/test_pdf_generation.py`)
- Company branding endpoint testing
- Authentication requirement verification
- Audit logging functionality
- Error response validation

### Manual Testing Checklist

- [ ] Generate PDF for each voucher type
- [ ] Verify company branding appears correctly
- [ ] Test with and without company logo
- [ ] Verify item tables render properly
- [ ] Check amount in words conversion
- [ ] Test authorization requirements
- [ ] Verify audit logging
- [ ] Test error scenarios

## Migration from Old System

### Updated Voucher Components
- `payment-voucher.tsx`: ✅ Updated to use professional PDF service
- `receipt-voucher.tsx`: ✅ Updated to use professional PDF service
- `sales-voucher.tsx`: ✅ Updated to use professional PDF service
- `proforma-invoice.tsx`: ✅ Updated to use professional PDF service
- `journal-voucher.tsx`: ✅ Updated to use professional PDF service
- `purchase-voucher.tsx`: ✅ Updated to use professional PDF service
- `contra-voucher.tsx`: ✅ Updated to use professional PDF service
- `non-sales-credit-note.tsx`: ✅ Updated to use professional PDF service
- `purchase-order.tsx`: ✅ Updated to use professional PDF service
- `grn.tsx`: ✅ Updated to use professional PDF service
- `purchase-return.tsx`: ✅ Updated to use professional PDF service
- `quotation.tsx`: ✅ Updated to use professional PDF service
- `sales-order.tsx`: ✅ Updated to use professional PDF service
- `delivery-challan.tsx`: ✅ Updated to use professional PDF service
- `sales-return.tsx`: ✅ Updated to use professional PDF service

### 🎉 Migration Complete!
All voucher types have been successfully migrated to use the professional PDF system.

## Future Enhancements

### Planned Features
- [ ] Custom PDF templates
- [ ] Multiple language support
- [ ] Advanced branding options
- [ ] Batch PDF generation
- [ ] Email integration
- [ ] Digital signatures
- [ ] QR code integration

### Performance Optimizations
- [ ] PDF caching
- [ ] Async generation for large documents
- [ ] Image optimization
- [ ] Template pre-compilation

## Support

For issues or questions regarding the Professional PDF Voucher System:
1. Check the error logs for detailed error messages
2. Verify authentication tokens are valid
3. Ensure company branding is properly configured
4. Review the test cases for usage examples
5. Check API endpoint availability

## Changelog

### v1.0.0 (Current)
- ✅ Initial implementation of professional PDF system
- ✅ Company branding integration
- ✅ Authorization and audit logging
- ✅ Support for major voucher types
- ✅ Comprehensive test coverage
- ✅ Documentation and migration guide