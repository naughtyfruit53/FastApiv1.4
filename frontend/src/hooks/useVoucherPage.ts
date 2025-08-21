// src/hooks/useVoucherPage.ts
// Comprehensive hook for voucher page logic - centralized DRY solution

import { useState, useCallback, useEffect, useMemo } from 'react';
import { useRouter } from 'next/router';
import { useForm, useFieldArray, useWatch } from 'react-hook-form';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { voucherService } from '../services/vouchersService';
import { getVendors, getProducts, getCustomers } from '../services/masterService';
import { useAuth } from '../context/AuthContext';
import { calculateVoucherTotals, getDefaultVoucherValues, numberToWords } from '../utils/voucherUtils';
import { generateVoucherPDF, getVoucherPdfConfig, VoucherPdfData } from '../utils/pdfUtils';
import { VoucherPageConfig } from '../types/voucher.types';
import api from '../lib/api';  // Direct import for list fetch

export const useVoucherPage = (config: VoucherPageConfig) => {
  const router = useRouter();
  const { id, mode: queryMode } = router.query;
  const { isOrgContextReady } = useAuth();
  const queryClient = useQueryClient();

  console.log('[useVoucherPage] Hook initialized for:', config.voucherType);
  console.log('[useVoucherPage] config.endpoint:', config.endpoint);
  console.log('[useVoucherPage] isOrgContextReady:', isOrgContextReady);

  const [mode, setMode] = useState<'create' | 'edit' | 'view'>((queryMode as 'create' | 'edit' | 'view') || 'create');
  const [selectedId, setSelectedId] = useState<number | null>(id ? Number(id) : null);
  const [showAddVendorModal, setShowAddVendorModal] = useState(false);
  const [showAddCustomerModal, setShowAddCustomerModal] = useState(false);
  const [showAddProductModal, setShowAddProductModal] = useState(false);
  const [showShippingModal, setShowShippingModal] = useState(false);
  const [showFullModal, setShowFullModal] = useState(false);
  const [addVendorLoading, setAddVendorLoading] = useState(false);
  const [addCustomerLoading, setAddCustomerLoading] = useState(false);
  const [addProductLoading, setAddProductLoading] = useState(false);
  const [addShippingLoading, setAddShippingLoading] = useState(false);
  const [addingItemIndex, setAddingItemIndex] = useState(-1);
  const [contextMenu, setContextMenu] = useState<{ mouseX: number; mouseY: number; voucher: any } | null>(null);
  const [selectedReferenceType, setSelectedReferenceType] = useState<string | null>(null);
  const [selectedReferenceId, setSelectedReferenceId] = useState<number | null>(null);
  const [useDifferentShipping, setUseDifferentShipping] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');
  const [filteredVouchers, setFilteredVouchers] = useState<any[]>([]);

  // Form management
  const defaultValues = useMemo(() => {
    if (config.hasItems === false) {
      // Financial vouchers - use financial defaults
      return {
        voucher_number: '',
        date: new Date().toISOString().slice(0, 10),
        reference: '',
        notes: '',
        total_amount: 0,
        from_account: '',
        to_account: '',
        payment_method: '',
        receipt_method: '',
        name_id: null as number | null,
        name_type: '' as 'Vendor' | 'Customer'
      };
    } else {
      // Vouchers with items - use standard defaults
      const baseDefaults = getDefaultVoucherValues(config.entityType === 'purchase' ? 'purchase' : 'sales');
      return baseDefaults;
    }
  }, [config.entityType, config.hasItems]);

  const { control, handleSubmit, reset, setValue, watch, formState: { errors } } = useForm({
    defaultValues
  });

  // Always create field array and watch, but use conditionally
  const { fields, append, remove } = useFieldArray({
    control,
    name: 'items'
  });

  const itemsWatch = useWatch({ control, name: 'items' });

  // Computed values (only if voucher has items)
  const { computedItems, totalAmount, totalSubtotal, totalGst } = useMemo(() => {
    if (config.hasItems === false || !itemsWatch) {
      return {
        computedItems: [],
        totalAmount: watch('total_amount') || 0,
        totalSubtotal: 0,
        totalGst: 0,
      };
    }
    return calculateVoucherTotals(itemsWatch);
  }, [itemsWatch, config.hasItems, watch]);

  // Queries
  const { data: voucherList, isLoading: isLoadingList, refetch: refetchVoucherList } = useQuery({
    queryKey: [config.voucherType],
    queryFn: () => voucherService.getVouchers(config.voucherType, { skip: 0, limit: 100 }),  // Add default params
    enabled: isOrgContextReady,
    onSuccess: (data) => {
      console.log(`[useVoucherPage] Successfully fetched vouchers for ${config.voucherType}:`, data);
    },
    onError: (error: any) => {
      console.error(`[useVoucherPage] Error fetching vouchers for ${config.voucherType}:`, error);
    },
  });

  const { data: vendorList } = useQuery({
    queryKey: ['vendors'],
    queryFn: getVendors,
    enabled: isOrgContextReady && (config.entityType === 'purchase' || config.entityType === 'financial'),
  });

  const { data: customerList } = useQuery({
    queryKey: ['customers'],
    queryFn: getCustomers,
    enabled: isOrgContextReady && (config.entityType === 'sales' || config.entityType === 'financial'),
  });

  const { data: productList } = useQuery({
    queryKey: ['products'],
    queryFn: getProducts,
    enabled: isOrgContextReady && config.hasItems !== false,
  });

  const { data: voucherData, isLoading: isFetching } = useQuery({
    queryKey: [config.voucherType, selectedId],
    queryFn: () => voucherService.getVoucherById(config.apiEndpoint || config.voucherType, selectedId!),
    enabled: !!selectedId && isOrgContextReady
  });

  const { data: nextVoucherNumber, isLoading: isNextNumberLoading, refetch: refetchNextNumber } = useQuery({
    queryKey: [`next${config.voucherType}Number`],
    queryFn: () => voucherService.getNextVoucherNumber(config.nextNumberEndpoint),
    enabled: mode === 'create' && isOrgContextReady,
  });

  // Mutations
  const createMutation = useMutation({
    mutationFn: (data: any) => voucherService.createVoucher(config.apiEndpoint || config.voucherType, data),
    onSuccess: async (newVoucher) => {
      console.log('[useVoucherPage] Voucher created successfully:', newVoucher);
      queryClient.invalidateQueries({ queryKey: [config.voucherType] });
      await refetchVoucherList();  // Explicit refetch after invalidation
      setMode('create');
      setSelectedId(null);
      reset(defaultValues);
      const { data: newNextNumber } = await refetchNextNumber();
      setValue('voucher_number', newNextNumber);
    },
    onError: (error: any) => {
      console.error('[useVoucherPage] Error creating voucher:', error);
      alert(error.response?.data?.detail || 'Failed to create voucher');
    }
  });

  const updateMutation = useMutation({
    mutationFn: (data: any) => voucherService.updateVoucher(config.apiEndpoint || config.voucherType, selectedId!, data),
    onSuccess: () => {
      console.log('[useVoucherPage] Voucher updated successfully');
      queryClient.invalidateQueries({ queryKey: [config.voucherType] });
      queryClient.invalidateQueries({ queryKey: [config.voucherType, selectedId] });
      refetchVoucherList();  // Explicit refetch after invalidation
    },
    onError: (error: any) => {
      console.error('[useVoucherPage] Error updating voucher:', error);
      alert(error.response?.data?.detail || 'Failed to update voucher');
    }
  });

  // Event handlers
  const handleCreate = () => {
    setSelectedId(null);
    setMode('create');
    router.push({ query: { mode: 'create' } }, undefined, { shallow: true });
  };

  const handleEdit = (voucherId: number) => {
    setSelectedId(voucherId);
    setMode('edit');
    router.push({ query: { id: voucherId, mode: 'edit' } }, undefined, { shallow: true });
  };

  const handleView = (voucherId: number) => {
    setSelectedId(voucherId);
    setMode('view');
    router.push({ query: { id: voucherId, mode: 'view' } }, undefined, { shallow: true });
  };

  const handleSubmitForm = (data: any) => {
    // Prepare data with computed items and totals (only if voucher has items)
    if (config.hasItems !== false) {
      data.items = computedItems;
      data.total_amount = totalAmount;
    }

    if (mode === 'create') {
      createMutation.mutate(data);
    } else if (mode === 'edit') {
      updateMutation.mutate(data);
    }
  };

  const handleContextMenu = (event: React.MouseEvent, voucher: any) => {
    event.preventDefault();
    setContextMenu({
      mouseX: event.clientX + 2,
      mouseY: event.clientY - 6,
      voucher,
    });
  };

  const handleCloseContextMenu = () => {
    setContextMenu(null);
  };

  // Search and filter functionality
  const sortedVouchers = useMemo(() => {
    if (!Array.isArray(voucherList)) {
      console.warn('[useVoucherPage] voucherList is not an array:', voucherList);
      return [];
    }
    // Sort by voucher number descending (newest voucher numbers at top)
    return [...voucherList].sort((a, b) => {
      const aNum = parseInt(a.voucher_number?.toString().replace(/\D/g, '') || '0');
      const bNum = parseInt(b.voucher_number?.toString().replace(/\D/g, '') || '0');
      return bNum - aNum;
    });
  }, [voucherList]);

  const latestVouchers = useMemo(() => sortedVouchers.slice(0, 5), [sortedVouchers]);

  const handleSearch = () => {
    if (fromDate && toDate && new Date(toDate) < new Date(fromDate)) {
      alert('To date cannot be earlier than from date');
      return;
    }
    
    const filtered = sortedVouchers.filter(v => {
      const lowerSearch = searchTerm.toLowerCase();
      
      // Search in voucher number
      let matchesSearch = v.voucher_number.toLowerCase().includes(lowerSearch);
      
      // Search in entity name based on voucher type
      if (config.entityType === 'purchase' && vendorList) {
        const vendor = vendorList.find((vendor: any) => vendor.id === v.vendor_id);
        if (vendor) matchesSearch = matchesSearch || vendor.name.toLowerCase().includes(lowerSearch);
      } else if (config.entityType === 'sales' && customerList) {
        const customer = customerList.find((customer: any) => customer.id === v.customer_id);
        if (customer) matchesSearch = matchesSearch || customer.name.toLowerCase().includes(lowerSearch);
      }
      
      // Date filtering
      const vDate = new Date(v.date);
      const matchesFrom = !fromDate || vDate >= new Date(fromDate);
      const matchesTo = !toDate || vDate <= new Date(toDate);
      
      return matchesSearch && matchesFrom && matchesTo;
    });
    setFilteredVouchers(filtered);
  };

  const handleModalOpen = () => {
    setShowFullModal(true);
    setFilteredVouchers(sortedVouchers);
  };

  const handleModalClose = () => {
    setShowFullModal(false);
    setSearchTerm('');
    setFromDate('');
    setToDate('');
    setFilteredVouchers([]);
  };

  // PDF generation using unified utility
  const handleGeneratePDF = useCallback(async (voucher?: any) => {
    const voucherToUse = voucher || watch();
    const pdfConfig = getVoucherPdfConfig(config.voucherType);
    
    const pdfData: VoucherPdfData = {
      voucher_number: voucherToUse.voucher_number,
      date: voucherToUse.date,
      reference: voucherToUse.reference,
      notes: voucherToUse.notes,
      total_amount: voucherToUse.total_amount || 0,
      items: voucherToUse.items || [],
      vendor: voucherToUse.vendor,
      customer: voucherToUse.customer,
      payment_method: voucherToUse.payment_method,
      receipt_method: voucherToUse.receipt_method,
      payment_terms: voucherToUse.payment_terms,
      from_account: voucherToUse.from_account,
      to_account: voucherToUse.to_account,
      ...voucherToUse
    };
    
    await generateVoucherPDF(pdfData, pdfConfig);
  }, [config.voucherType, watch]);

  // Delete functionality
  const handleDelete = useCallback(async (voucher: any) => {
    if (window.confirm(`Are you sure you want to delete voucher {voucher.voucher_number}?`)) {
      try {
        await voucherService.deleteVoucher(config.apiEndpoint || config.voucherType, voucher.id);
        queryClient.invalidateQueries({ queryKey: [config.voucherType] });
        refetchVoucherList();  // Explicit refetch after deletion
        console.log('Voucher deleted successfully');
      } catch (error: any) {
        console.error('Error deleting voucher:', error);
        alert(error.response?.data?.detail || 'Failed to delete voucher');
      }
    }
  }, [config.voucherType, config.apiEndpoint, queryClient]);

  // Number to words utility
  const getAmountInWords = useCallback((amount: number) => {
    return numberToWords(amount);
  }, []);

  // Master data refresh functionality
  const refreshMasterData = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ['vendors'] });
    queryClient.invalidateQueries({ queryKey: ['customers'] });
    queryClient.invalidateQueries({ queryKey: ['products'] });
  }, [queryClient]);

  // Customer add handler with auto-selection
  const handleAddCustomer = useCallback(async (customerData: any) => {
    setAddCustomerLoading(true);
    try {
      const response = await masterDataService.createCustomer(customerData);
      const newCustomer = response;
      
      // Update query data immediately
      queryClient.setQueryData(['customers'], (old: any) => old ? [...old, newCustomer] : [newCustomer]);
      queryClient.invalidateQueries({ queryKey: ['customers'] });
      
      // Auto-select the new customer (conditional on entity type)
      if (config.entityType === 'sales') {
        setValue('customer_id', newCustomer.id);
      }
      
      setShowAddCustomerModal(false);
      alert('Customer added successfully!');
    } catch (error: any) {
      console.error('Error adding customer:', error);
      let errorMsg = 'Error adding customer';
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        if (Array.isArray(detail)) {
          errorMsg = detail.map((err: any) => err.msg || err).join(', ');
        } else if (typeof detail === 'string') {
          errorMsg = detail;
        }
      }
      alert(errorMsg);
    } finally {
      setAddCustomerLoading(false);
    }
  }, [queryClient, setValue, setAddCustomerLoading, setShowAddCustomerModal]);

  // Vendor add handler with auto-selection
  const handleAddVendor = useCallback(async (vendorData: any) => {
    setAddVendorLoading(true);
    try {
      const response = await masterDataService.createVendor(vendorData);
      const newVendor = response;
      
      // Update query data immediately
      queryClient.setQueryData(['vendors'], (old: any) => old ? [...old, newVendor] : [newVendor]);
      queryClient.invalidateQueries({ queryKey: ['vendors'] });
      
      // Auto-select the new vendor (conditional on entity type)  
      if (config.entityType === 'purchase') {
        setValue('vendor_id', newVendor.id);
      }
      
      setShowAddVendorModal(false);
      alert('Vendor added successfully!');
    } catch (error: any) {
      console.error('Error adding vendor:', error);
      let errorMsg = 'Error adding vendor';
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        if (Array.isArray(detail)) {
          errorMsg = detail.map((err: any) => err.msg || err).join(', ');
        } else if (typeof detail === 'string') {
          errorMsg = detail;
        }
      }
      alert(errorMsg);
    } finally {
      setAddVendorLoading(false);
    }
  }, [queryClient, setValue, setAddVendorLoading, setShowAddVendorModal]);

  // Product add handler  
  const handleAddProduct = useCallback(async (productData: any) => {
    setAddProductLoading(true);
    try {
      const response = await masterDataService.createProduct(productData);
      const newProduct = response;
      
      // Update query data immediately
      queryClient.setQueryData(['products'], (old: any) => old ? [...old, newProduct] : [newProduct]);
      queryClient.invalidateQueries({ queryKey: ['products'] });
      
      setShowAddProductModal(false);
      alert('Product added successfully!');
    } catch (error: any) {
      console.error('Error adding product:', error);
      alert(error.response?.data?.detail || 'Error adding product');
    } finally {
      setAddProductLoading(false);
    }
  }, [queryClient, setAddProductLoading, setShowAddProductModal]);

  // Shipping address add handler
  const handleAddShipping = useCallback(async (shippingData: any) => {
    setAddShippingLoading(true);
    try {
      // Add shipping logic here
      setShowShippingModal(false);
      alert('Shipping address added successfully!');
    } catch (error: any) {
      console.error('Error adding shipping address:', error);
      alert('Error adding shipping address');
    } finally {
      setAddShippingLoading(false);
    }
  }, [setAddShippingLoading, setShowShippingModal]);

  // Effects
  useEffect(() => {
    if (mode === 'create' && nextVoucherNumber) {
      setValue('voucher_number', nextVoucherNumber);
    } else if (voucherData) {
      reset(voucherData);
    } else if (mode === 'create') {
      reset(defaultValues);
    }
  }, [voucherData, mode, reset, nextVoucherNumber, setValue, defaultValues]);

  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'refreshMasterData') {
        refreshMasterData();
        localStorage.removeItem('refreshMasterData');
      }
    };
    
    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [refreshMasterData]);

  useEffect(() => {
    if (mode === 'create' && isOrgContextReady) {
      refetchNextNumber();
    }
  }, [mode, isOrgContextReady, refetchNextNumber]);

  useEffect(() => {
    console.log('Next Voucher Number:', nextVoucherNumber);
    console.log('Is Next Number Loading:', isNextNumberLoading);
    console.log('Is Org Context Ready:', isOrgContextReady);
    console.log('Mode:', mode);
  }, [nextVoucherNumber, isNextNumberLoading, isOrgContextReady, mode]);

  // Loading state
  const isLoading = isLoadingList || isFetching || !isOrgContextReady;

  // Refetch voucher list when org context becomes ready
  useEffect(() => {
    if (isOrgContextReady) {
      console.log('[useVoucherPage] Org context ready - refetching voucher list');
      refetchVoucherList();
    }
  }, [isOrgContextReady, refetchVoucherList]);

  // Refetch list after create/update
  useEffect(() => {
    if (createMutation.isSuccess || updateMutation.isSuccess) {
      queryClient.invalidateQueries({ queryKey: [config.voucherType] });
      refetchVoucherList();
    }
  }, [createMutation.isSuccess, updateMutation.isSuccess, queryClient, config.voucherType, refetchVoucherList]);

  return {
    // State
    mode,
    setMode,
    selectedId,
    isLoading,
    showAddVendorModal,
    setShowAddVendorModal,
    showAddCustomerModal,
    setShowAddCustomerModal,
    showAddProductModal,
    setShowAddProductModal,
    showShippingModal,
    setShowShippingModal,
    showFullModal,
    addVendorLoading,
    setAddVendorLoading,
    addCustomerLoading,
    setAddCustomerLoading,
    addProductLoading,
    setAddProductLoading,
    addShippingLoading,
    setAddShippingLoading,
    addingItemIndex,
    setAddingItemIndex,
    contextMenu,
    selectedReferenceType,
    setSelectedReferenceType,
    selectedReferenceId,
    setSelectedReferenceId,
    useDifferentShipping,
    setUseDifferentShipping,
    searchTerm,
    setSearchTerm,
    fromDate,
    setFromDate,
    toDate,
    setToDate,
    filteredVouchers,

    // Form
    control,
    handleSubmit,
    reset,
    setValue,
    watch,
    errors,
    fields,
    append,
    remove,

    // Data
    voucherList,
    vendorList,
    customerList,
    productList,
    voucherData,
    nextVoucherNumber,
    sortedVouchers,
    latestVouchers,

    // Computed
    computedItems,
    totalAmount,
    totalSubtotal,
    totalGst,

    // Mutations
    createMutation,
    updateMutation,

    // Event handlers
    handleCreate,
    handleEdit,
    handleView,
    handleSubmitForm,
    handleContextMenu,
    handleCloseContextMenu,
    handleSearch,
    handleModalOpen,
    handleModalClose,
    handleGeneratePDF,
    handleDelete,
    handleAddCustomer,
    handleAddVendor,
    handleAddProduct,
    handleAddShipping,
    refreshMasterData,
    getAmountInWords,

    // Utilities
    isViewMode: mode === 'view',
  };
};