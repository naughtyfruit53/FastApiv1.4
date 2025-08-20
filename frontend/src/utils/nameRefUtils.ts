// src/utils/nameRefUtils.ts

import { useQuery } from '@tanstack/react-query';
import api from '../lib/api';
import { getVendors, getCustomers } from '../services/masterService';

export const useNameOptions = () => {
  const { data: vendorList } = useQuery({
    queryKey: ['vendors'],
    queryFn: () => getVendors()
  });

  const { data: customerList } = useQuery({
    queryKey: ['customers'],
    queryFn: () => getCustomers()
  });

  // Future: Add more types here, e.g., employees = await getEmployees();
  return [
    ...(vendorList || []).map(v => ({ ...v, type: 'Vendor' })),
    ...(customerList || []).map(c => ({ ...c, type: 'Customer' }))
    // Future: ...(employeeList || []).map(e => ({ ...e, type: 'Employee' })),
  ];
};

export const useReferenceOptions = (selectedNameId: number | null, selectedNameType: 'Vendor' | 'Customer' | null) => {
  const { data: unpaidVouchers } = useQuery({
    queryKey: ['unpaid-vouchers', selectedNameId, selectedNameType],
    queryFn: () => {
      if (!selectedNameId || !selectedNameType) return [];
      const endpoint = selectedNameType === 'Vendor' ? '/purchase-vouchers' : '/sales-vouchers';
      return api.get(endpoint, { params: { vendor_id: selectedNameId, customer_id: selectedNameId } }).then(res => res.data);
    },
    enabled: !!selectedNameId && !!selectedNameType,
  });

  return [
    ... (unpaidVouchers || []).map(v => v.voucher_number),
    'Advance',
    'On Account'
  ];
};