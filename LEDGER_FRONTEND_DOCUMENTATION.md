# Ledger Frontend Implementation Documentation

## Overview

The Ledger Frontend provides a comprehensive interface for viewing financial ledger data in the ERP system. It includes two main views: Complete Ledger and Outstanding Ledger, with advanced filtering and permission controls.

## Features

### 1. Ledger Tab
- Added as the 6th tab in the Reports page
- Accessible only to authorized users (Super Admin, Admin, Standard User)
- Permission-based access control using `canAccessLedger()` function

### 2. Complete Ledger View
Shows all debit/credit transactions with:
- **Comprehensive Transaction Data**: Displays voucher details, account information, amounts, and balances
- **Advanced Filtering**: Date range, account type, specific account ID, voucher type
- **Summary Statistics**: Total transactions, total debit/credit amounts, net balance
- **Responsive Table**: Properly formatted data with appropriate column headers

### 3. Outstanding Ledger View
Shows only open balances with:
- **Visual Distinction**: 
  - Payables (vendor balances) shown in red with "(Payable)" label
  - Receivables (customer balances) shown in green with "(Receivable)" label
- **Account Type Chips**: Different colored chips for vendors vs customers
- **Summary Metrics**: Total payable, total receivable, net outstanding
- **Contact Information**: Shows contact details for each account

### 4. User Interface Features

#### Toggle Switch
- Seamless switching between Complete and Outstanding ledger views
- Switch label updates based on current selection
- Automatic data refresh when switching views

#### Filter Controls
- **Date Range**: Start and end date inputs
- **Account Type**: Dropdown (All, Vendors, Customers)
- **Voucher Type**: Dropdown (All, Purchase, Sales, Payment, Receipt, Debit Note, Credit Note)
- **Refresh Button**: Manual data refresh capability

#### Responsive Design
- Mobile-friendly layout using Material-UI Grid system
- Proper breakpoints for different screen sizes
- Accessible form controls with proper labeling

### 5. Permission System

```typescript
export const canAccessLedger = (user: User | null): boolean => {
  if (!user) return false;
  const role = user.role || localStorage.getItem('user_role');
  // Super Admin, Admin, and authorized Standard Users can access ledger
  return user.is_super_admin === true || 
         ['super_admin', 'org_admin', 'admin', 'standard_user'].includes(role);
};
```

### 6. API Integration

#### Service Functions
```typescript
// Added to reportsService in authService.ts
getCompleteLedger: async (params?: any) => {
  try {
    const response = await api.get('/reports/complete-ledger', { params });
    return response.data;
  } catch (error: any) {
    throw new Error(error.userMessage || 'Failed to get complete ledger');
  }
},

getOutstandingLedger: async (params?: any) => {
  try {
    const response = await api.get('/reports/outstanding-ledger', { params });
    return response.data;
  } catch (error: any) {
    throw new Error(error.userMessage || 'Failed to get outstanding ledger');
  }
}
```

#### Query Integration
Uses React Query for:
- Automatic data caching
- Loading states management
- Error handling
- Conditional fetching based on tab selection and permissions

## Code Structure

### Component Architecture
```
ReportsPage
├── TabPanel[5] (Ledger)
    ├── Permission Check
    ├── Filter Controls
    ├── Complete Ledger View
    │   ├── Summary Statistics
    │   └── Transaction Table
    └── Outstanding Ledger View
        ├── Balance Summary
        └── Outstanding Balances Table
```

### State Management
```typescript
// Ledger specific state
const [ledgerType, setLedgerType] = useState<'complete' | 'outstanding'>('complete');
const [ledgerFilters, setLedgerFilters] = useState({
  start_date: dateRange.start,
  end_date: dateRange.end,
  account_type: 'all',
  account_id: '',
  voucher_type: 'all'
});
```

### Error Handling
- Network errors are caught and display appropriate messages
- Permission errors show access denied alerts
- Loading states prevent user confusion during data fetching

## Testing

### Test Coverage
The `LedgerReport.test.tsx` file covers:
- Permission-based access control
- Toggle functionality between views
- Data display and formatting
- Filter functionality
- Error handling scenarios
- User interactions

### Test Structure
```typescript
describe('Ledger Report', () => {
  describe('Ledger Tab Access', () => { /* Permission tests */ });
  describe('Ledger Type Toggle', () => { /* Toggle functionality */ });
  describe('Complete Ledger View', () => { /* Complete ledger tests */ });
  describe('Outstanding Ledger View', () => { /* Outstanding ledger tests */ });
  describe('Filter Functionality', () => { /* Filter tests */ });
  describe('Error Handling', () => { /* Error scenarios */ });
});
```

## Accessibility Features

### WCAG Compliance
- Proper ARIA labels on form controls
- Semantic HTML structure
- Color contrast for visual distinctions
- Keyboard navigation support
- Screen reader compatibility

### Material-UI Accessibility
- Uses Material-UI components with built-in accessibility
- Proper focus management
- Consistent interaction patterns

## Performance Considerations

### Optimization Strategies
- Conditional API calls (only when tab is active)
- React Query caching to prevent redundant requests
- Efficient re-rendering with proper dependency arrays
- Minimal state updates

### Data Handling
- Proper number formatting for currency display
- Date formatting for consistent display
- Safe property access with fallback values

## Backend Integration

### API Endpoints
- `GET /api/v1/reports/complete-ledger`: Complete transaction data
- `GET /api/v1/reports/outstanding-ledger`: Outstanding balance data

### Data Schema
Follows the backend schemas defined in `app/schemas/ledger.py`:
- `CompleteLedgerResponse`
- `OutstandingLedgerResponse`
- `LedgerFilters`

## Future Enhancements

### Potential Improvements
1. **Export Functionality**: Add PDF/Excel export options
2. **Advanced Filters**: Add more granular filtering options
3. **Drill-down Capability**: Click on account to see detailed transactions
4. **Real-time Updates**: WebSocket integration for live data
5. **Dashboard Integration**: Summary widgets on main dashboard
6. **Print Functionality**: Formatted print layouts

### Performance Optimizations
1. **Virtualization**: For large datasets
2. **Pagination**: Server-side pagination for better performance
3. **Search**: Full-text search across transaction data
4. **Caching**: Extended caching strategies

## Dependencies

### Required Packages
- `@mui/material`: UI components
- `@mui/icons-material`: Icons
- `@tanstack/react-query`: Data fetching and caching
- `react`: Core React library

### Development Dependencies
- `@testing-library/react`: Component testing
- `@testing-library/jest-dom`: DOM testing utilities
- `jest`: Test framework

## Installation and Setup

1. All required dependencies are already included in package.json
2. Component is integrated into existing Reports page
3. No additional configuration required
4. Backend API endpoints must be available and accessible

## Troubleshooting

### Common Issues
1. **Permission Denied**: Check user role and `canAccessLedger` function
2. **API Errors**: Verify backend endpoints are running and accessible
3. **Data Not Loading**: Check network tab for API call status
4. **Visual Issues**: Ensure Material-UI theme is properly configured

### Debug Mode
Enable React Query DevTools for debugging data fetching issues:
```typescript
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
```

## Conclusion

The Ledger Frontend provides a robust, user-friendly interface for financial data visualization with proper security, accessibility, and performance considerations. It integrates seamlessly with the existing Reports system while providing specialized functionality for ledger management.