// src/utils/voucherUtils.ts

export const GST_SLABS = [0, 5, 12, 18, 28];

export const voucherTypes = {
  purchase: [
    { label: 'Purchase Order', slug: 'purchase-orders' },
    { label: 'Purchase Voucher', slug: 'purchase-vouchers' },
    { label: 'Purchase Return', slug: 'purchase-returns' },
    { label: 'GRN', slug: 'grns' },
  ],
  sales: [
    { label: 'Quotation', slug: 'quotations' },
    { label: 'Proforma Invoice', slug: 'proforma-invoices' },
    { label: 'Sales Order', slug: 'sales-orders' },
    { label: 'Delivery Challan', slug: 'delivery-challans' },
    { label: 'Sales Voucher', slug: 'sales-vouchers' },
    { label: 'Sales Return', slug: 'sales-returns' },
  ],
  financial: [
    { label: 'Payment Voucher', slug: 'payment-vouchers' },
    { label: 'Receipt Voucher', slug: 'receipt-vouchers' },
    { label: 'Journal Voucher', slug: 'journal-vouchers' },
    { label: 'Contra Voucher', slug: 'contra-vouchers' },
    { label: 'Credit Note', slug: 'credit-notes' },
    { label: 'Debit Note', slug: 'debit-notes' },
  ]
};

/**
 * Convert number to words in Indian format
 * This is the centralized implementation used across all voucher types
 */
export const numberToWordsInteger = (num: number): string => {
  if (num === 0 || isNaN(num)) return '';
  const belowTwenty = [' ', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen'];
  const tens = [' ', ' ', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety'];
  const thousands = ['', 'Thousand', 'Million', 'Billion'];
  let word = '';
  let i = 0;
  while (num > 0) {
    const chunk = num % 1000;
    if (chunk) {
      let chunkWord = '';
      if (chunk >= 100) {
        chunkWord += belowTwenty[Math.floor(chunk / 100)] + ' Hundred ';
      }
      let remain = chunk % 100;
      if (remain >= 20) {
        chunkWord += tens[Math.floor(remain / 10)] + ' ';
        remain %= 10;
      }
      if (remain > 0) {
        chunkWord += belowTwenty[remain] + ' ';
      }
      word = chunkWord + thousands[i] + ' ' + word;
    }
    num = Math.floor(num / 1000);
    i++;
  }
  return word.trim();
};

/**
 * Convert number to words with decimal support
 * This is the the centralized implementation used across all voucher types
 */
export const numberToWords = (num: number): string => {
  if (num === 0 || isNaN(num)) return 'Zero only';
  const integer = Math.floor(num);
  const decimal = Math.round((num - integer) * 100);
  let word = numberToWordsInteger(integer);
  if (decimal > 0) {
    word += ' point ' + numberToWordsInteger(decimal);
  }
  return word ? word + ' only' : '';
};

// Common voucher item calculation utilities
export const calculateItemTotals = (item: any) => {
  const subtotal = (item.quantity || 0) * (item.unit_price || 0);
  const discountAmount = subtotal * ((item.discount_percentage || 0) / 100);
  const taxableAmount = subtotal - discountAmount;
  const gstAmount = taxableAmount * ((item.gst_rate || 0) / 100);
  const cgstAmount = gstAmount / 2;
  const sgstAmount = gstAmount / 2;
  const igstAmount = 0; // Assuming intrastate transactions
  const totalAmount = taxableAmount + gstAmount;

  return {
    ...item,
    discount_amount: discountAmount,
    taxable_amount: taxableAmount,
    cgst_amount: cgstAmount,
    sgst_amount: sgstAmount,
    igst_amount: igstAmount,
    total_amount: totalAmount,
  };
};

export const calculateVoucherTotals = (items: any[]) => {
  const computedItems = items.map(calculateItemTotals);
  
  const totalAmount = computedItems.reduce((sum, item) => sum + item.total_amount, 0);
  const totalSubtotal = computedItems.reduce((sum, item) => sum + (item.quantity || 0) * (item.unit_price || 0), 0);
  const totalGst = computedItems.reduce((sum, item) => sum + item.taxable_amount * ((item.gst_rate || 0) / 100), 0);
  
  return {
    computedItems,
    totalAmount,
    totalSubtotal,
    totalGst,
  };
};

// Common default values for voucher forms
export const getDefaultVoucherValues = (type: 'purchase' | 'sales') => {
  const baseValues = {
    voucher_number: '',
    date: new Date().toISOString().slice(0, 10),
    reference: '',
    payment_terms: '',
    notes: '',
    items: [{ 
      product_id: null as number | null, 
      hsn_code: '', 
      quantity: 0, 
      unit: '', 
      unit_price: 0, 
      original_unit_price: 0, 
      discount_percentage: 0, 
      discount_amount: 0, 
      taxable_amount: 0, 
      gst_rate: 0, 
      cgst_amount: 0, 
      sgst_amount: 0, 
      igst_amount: 0, 
      total_amount: 0 
    }],
    total_amount: 0,
  };

  if (type === 'purchase') {
    return {
      ...baseValues,
      vendor_id: null as number | null,
    };
  } else {
    return {
      ...baseValues,
      customer_id: null as number | null,
    };
  }
};

/**
 * Get financial voucher default values (no items array)
 */
export const getFinancialVoucherDefaults = () => ({
  voucher_number: '',
  date: new Date().toISOString().slice(0, 10),
  reference: '',
  notes: '',
  total_amount: 0,
  from_account: '',
  to_account: '',
  payment_method: '',
  receipt_method: ''
});

/**
 * Voucher configuration presets for common voucher types
 */
export const VOUCHER_CONFIGS = {
  'payment-voucher': {
    voucherType: 'payment-vouchers',
    entityType: 'financial' as const,
    endpoint: '/payment-vouchers',
    nextNumberEndpoint: '/payment-vouchers/next-number',
    hasItems: false,
    voucherTitle: 'Payment Voucher'
  },
  'receipt-voucher': {
    voucherType: 'receipt-vouchers',
    entityType: 'financial' as const,
    endpoint: '/receipt-vouchers',
    nextNumberEndpoint: '/receipt-vouchers/next-number',
    hasItems: false,
    voucherTitle: 'Receipt Voucher'
  },
  'journal-voucher': {
    voucherType: 'journal-vouchers',
    entityType: 'financial' as const,
    endpoint: '/journal-vouchers',
    nextNumberEndpoint: '/journal-vouchers/next-number',
    hasItems: false,
    voucherTitle: 'Journal Voucher'
  },
  'contra-voucher': {
    voucherType: 'contra-vouchers',
    entityType: 'financial' as const,
    endpoint: '/contra-vouchers',
    nextNumberEndpoint: '/contra-vouchers/next-number',
    hasItems: false,
    voucherTitle: 'Contra Voucher'
  },
  'purchase-voucher': {
    voucherType: 'purchase-vouchers',
    entityType: 'purchase' as const,
    endpoint: '/purchase-vouchers',
    nextNumberEndpoint: '/purchase-vouchers/next-number',
    hasItems: true,
    voucherTitle: 'Purchase Voucher'
  },
  'purchase-order': {
    voucherType: 'purchase-orders',
    entityType: 'purchase' as const,
    endpoint: '/purchase-orders',
    nextNumberEndpoint: '/purchase-orders/next-number',
    hasItems: true,
    voucherTitle: 'Purchase Order'
  },
  'purchase-return': {
    voucherType: 'purchase-returns',
    entityType: 'purchase' as const,
    endpoint: '/purchase-returns',
    nextNumberEndpoint: '/purchase-returns/next-number',
    hasItems: true,
    voucherTitle: 'Purchase Return'
  },
  'grn': {
    voucherType: 'goods-receipt-notes',
    entityType: 'purchase' as const,
    endpoint: '/goods-receipt-notes',
    nextNumberEndpoint: '/goods-receipt-notes/next-number',
    hasItems: true,
    voucherTitle: 'GRN'
  },
  'sales-voucher': {
    voucherType: 'sales-vouchers',
    entityType: 'sales' as const,
    endpoint: '/sales-vouchers',
    nextNumberEndpoint: '/sales-vouchers/next-number',
    hasItems: true,
    voucherTitle: 'Sales Voucher'
  },
  'quotation': {
    voucherType: 'quotations',
    entityType: 'sales' as const,
    endpoint: '/quotations',
    nextNumberEndpoint: '/quotations/next-number',
    hasItems: true,
    voucherTitle: 'Quotation'
  },
  'proforma-invoice': {
    voucherType: 'proforma-invoices',
    entityType: 'sales' as const,
    endpoint: '/proforma-invoices',
    nextNumberEndpoint: '/proforma-invoices/next-number',
    hasItems: true,
    voucherTitle: 'Proforma Invoice'
  },
  'sales-order': {
    voucherType: 'sales-orders',
    entityType: 'sales' as const,
    endpoint: '/sales-orders',
    nextNumberEndpoint: '/sales-orders/next-number',
    hasItems: true,
    voucherTitle: 'Sales Order'
  },
  'delivery-challan': {
    voucherType: 'delivery-challans',
    entityType: 'sales' as const,
    endpoint: '/delivery-challans',
    nextNumberEndpoint: '/delivery-challans/next-number',
    hasItems: true,
    voucherTitle: 'Delivery Challan'
  },
  'sales-return': {
    voucherType: 'sales-returns',
    entityType: 'sales' as const,
    endpoint: '/sales-returns',
    nextNumberEndpoint: '/sales-returns/next-number',
    hasItems: true,
    voucherTitle: 'Sales Return'
  },
  'credit-note': {
    voucherType: 'credit-notes',
    entityType: 'financial' as const,
    endpoint: '/credit-notes',
    nextNumberEndpoint: '/credit-notes/next-number',
    hasItems: false,
    voucherTitle: 'Credit Note'
  },
  'debit-note': {
    voucherType: 'debit-notes',
    entityType: 'financial' as const,
    endpoint: '/debit-notes',
    nextNumberEndpoint: '/debit-notes/next-number',
    hasItems: false,
    voucherTitle: 'Debit Note'
  },
  'non-sales-credit-note': {
    voucherType: 'non-sales-credit-notes',
    entityType: 'financial' as const,
    endpoint: '/non-sales-credit-notes',
    nextNumberEndpoint: '/non-sales-credit-notes/next-number',
    hasItems: false,
    voucherTitle: 'Non-Sales Credit Note'
  },
  // Manufacturing Vouchers
  'job-card': {
    voucherType: 'job-cards',
    entityType: 'purchase' as const,
    endpoint: '/job-cards',
    nextNumberEndpoint: '/job-cards/next-number',
    hasItems: true,
    voucherTitle: 'Job Card'
  },
  'production-order': {
    voucherType: 'production-orders',
    entityType: 'purchase' as const,
    endpoint: '/production-orders',
    nextNumberEndpoint: '/production-orders/next-number',
    hasItems: true,
    voucherTitle: 'Production Order'
  },
  'work-order': {
    voucherType: 'work-orders',
    entityType: 'purchase' as const,
    endpoint: '/work-orders',
    nextNumberEndpoint: '/work-orders/next-number',
    hasItems: true,
    voucherTitle: 'Work Order'
  },
  'material-receipt': {
    voucherType: 'material-receipts',
    entityType: 'purchase' as const,
    endpoint: '/material-receipts',
    nextNumberEndpoint: '/material-receipts/next-number',
    hasItems: true,
    voucherTitle: 'Material Receipt'
  },
  'material-requisition': {
    voucherType: 'material-requisitions',
    entityType: 'purchase' as const,
    endpoint: '/material-requisitions',
    nextNumberEndpoint: '/material-requisitions/next-number',
    hasItems: true,
    voucherTitle: 'Material Requisition'
  },
  'finished-good-receipt': {
    voucherType: 'finished-good-receipts',
    entityType: 'purchase' as const,
    endpoint: '/finished-good-receipts',
    nextNumberEndpoint: '/finished-good-receipts/next-number',
    hasItems: true,
    voucherTitle: 'Finished Good Receipt'
  },
  'manufacturing-journal': {
    voucherType: 'manufacturing-journals',
    entityType: 'financial' as const,
    endpoint: '/manufacturing-journals',
    nextNumberEndpoint: '/manufacturing-journals/next-number',
    hasItems: false,
    voucherTitle: 'Manufacturing Journal'
  },
  'stock-journal': {
    voucherType: 'stock-journals',
    entityType: 'financial' as const,
    endpoint: '/stock-journals',
    nextNumberEndpoint: '/stock-journals/next-number',
    hasItems: true,
    voucherTitle: 'Stock Journal'
  }
} as const;

/**
 * Get voucher configuration by type
 */
export const getVoucherConfig = (voucherType: keyof typeof VOUCHER_CONFIGS) => {
  return VOUCHER_CONFIGS[voucherType];
};