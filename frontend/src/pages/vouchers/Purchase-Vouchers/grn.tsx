// frontend/src/pages/vouchers/Purchase-Vouchers/grn.tsx
// Goods Receipt Note Page - Refactored using shared DRY logic
import React, { useMemo, useState, useEffect } from 'react';
import { Box, Button, TextField, Typography, Grid, IconButton, CircularProgress, Container, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Autocomplete, InputAdornment, Tooltip, Modal, Alert, Chip, Fab } from '@mui/material';
import { Add, Remove, Visibility, Edit, CloudUpload, CheckCircle, Description } from '@mui/icons-material';
import AddVendorModal from '../../../components/AddVendorModal';
import AddProductModal from '../../../components/AddProductModal';
import AddShippingAddressModal from '../../../components/AddShippingAddressModal';
import VoucherContextMenu from '../../../components/VoucherContextMenu';
import VoucherLayout from '../../../components/VoucherLayout';
import VoucherHeaderActions from '../../../components/VoucherHeaderActions';
import VoucherListModal from '../../../components/VoucherListModal';
import BalanceDisplay from '../../../components/BalanceDisplay';
import StockDisplay from '../../../components/StockDisplay';
import ProductAutocomplete from '../../../components/ProductAutocomplete';
import { useVoucherPage } from '../../../hooks/useVoucherPage';
import { getVoucherConfig, numberToWords, GST_SLABS, parseRateField, formatRateField, getVoucherStyles } from '../../../utils/voucherUtils';
import { getStock } from '../../../services/masterService';
import { voucherService } from '../../../services/vouchersService';
import api from '../../../lib/api';  // Import api for direct call
import { useAuth } from '../../../context/AuthContext';
import { useQuery } from '@tanstack/react-query';

const GoodsReceiptNotePage: React.FC = () => {
  const { isOrgContextReady } = useAuth();
  const config = getVoucherConfig('grn');
  const voucherStyles = getVoucherStyles();
  const {
    // State
    mode,
    setMode,
    isLoading,
    showAddCustomerModal,
    setShowAddCustomerModal,
    showAddProductModal,
    setShowAddProductModal,
    showShippingModal,
    setShowShippingModal,
    addCustomerLoading,
    setAddCustomerLoading,
    addProductLoading,
    setAddProductLoading,
    addShippingLoading,
    setAddShippingLoading,
    addingItemIndex,
    setAddingItemIndex,
    showFullModal,
    contextMenu,
    useDifferentShipping,
    setUseDifferentShipping,
    searchTerm,
    setSearchTerm,
    fromDate,
    setFromDate,
    toDate,
    setToDate,
    filteredVouchers,

    // Enhanced pagination
    currentPage,
    pageSize,
    paginationData,
    handlePageChange,

    // Reference document handling
    referenceDocument,
    handleReferenceSelected,

    // Form
    control,
    handleSubmit,
    watch,
    setValue,
    errors,
    fields,
    append,
    remove,
    reset,

    // Data
    voucherList,
    customerList: vendorList,
    productList,
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
    handleSubmitForm: _handleSubmitForm, // Rename to avoid conflict
    handleContextMenu,
    handleCloseContextMenu,
    handleSearch,
    handleModalOpen,
    handleModalClose,
    handleGeneratePDF,
    handleDelete,
    refreshMasterData,
    getAmountInWords,

    // Utilities
    isViewMode,
  } = useVoucherPage(config);

  // Additional state for voucher list modal
  const [showVoucherListModal, setShowVoucherListModal] = useState(false);

  // Goods Receipt Note specific state
  const selectedVendorId = watch('vendor_id');
  const selectedVendor = vendorList?.find((v: any) => v.id === selectedVendorId);

  // Enhanced vendor options with "Add New"
  const enhancedVendorOptions = [
    ...(vendorList || []),
    { id: null, name: 'Add New Vendor...' }
  ];

  // Stock data state for items
  const [stockLoading, setStockLoading] = useState<{[key: number]: boolean}>({});

  // GRN specific states
  const [selectedVoucherType, setSelectedVoucherType] = useState<'purchase-voucher' | 'purchase-order' | null>(null);
  const [selectedVoucherId, setSelectedVoucherId] = useState<number | null>(null);

  // Fetch purchase orders
  const { data: purchaseOrders } = useQuery({
    queryKey: ['purchase-orders'],
    queryFn: () => api.get('/purchase-orders').then(res => res.data),
    enabled: isOrgContextReady,
  });

  // Fetch purchase vouchers
  const { data: purchaseVouchers } = useQuery({
    queryKey: ['purchase-vouchers'],
    queryFn: () => api.get('/purchase-vouchers').then(res => res.data),
    enabled: isOrgContextReady,
  });

  // Voucher options based on type
  const voucherOptions = useMemo(() => {
    if (selectedVoucherType === 'purchase-order') {
      return purchaseOrders || [];
    } else if (selectedVoucherType === 'purchase-voucher') {
      return purchaseVouchers || [];
    }
    return [];
  }, [selectedVoucherType, purchaseOrders, purchaseVouchers]);

  // Fetch selected voucher details
  const { data: selectedVoucherData } = useQuery({
    queryKey: [selectedVoucherType, selectedVoucherId],
    queryFn: () => {
      if (!selectedVoucherType || !selectedVoucherId) return null;
      const endpoint = selectedVoucherType === 'purchase-order' ? '/purchase-orders' : '/purchase-vouchers';
      return api.get(`${endpoint}/${selectedVoucherId}`).then(res => res.data);
    },
    enabled: !!selectedVoucherType && !!selectedVoucherId,
  });

  // Populate form with selected voucher data
  useEffect(() => {
    if (selectedVoucherData) {
      setValue('vendor_id', selectedVoucherData.vendor_id);
      // Clear existing items
      remove();
      // Append items from selected voucher
      selectedVoucherData.items.forEach((item: any) => {
        append({
          product_id: item.product_id,
          product_name: item.product_name || '', // Assuming product has name
          order_qty: item.quantity,
          received_qty: 0,
          accepted_qty: 0,
          rejected_qty: 0,
          unit_price: item.unit_price, // Keep hidden
          unit: item.unit,
        });
      });
    }
  }, [selectedVoucherData, setValue, append, remove]);

  // Goods Receipt Note specific handlers
  const handleAddItem = () => {
    // No add item for GRN, as items come from voucher
  };

  // Custom submit handler to prompt for PDF after save
  const onSubmit = async (data: any) => {
    try {
      if (config.hasItems !== false) {
        // Calculate totals if needed, but since no price shown, perhaps adjust
        data.items = fields.map(field => ({
          ...field,
          total_cost: field.accepted_qty * field.unit_price, // Calculate hidden
        }));
        data.total_amount = data.items.reduce((sum: number, item: any) => sum + item.total_cost, 0);
      }

      let response;
      if (mode === 'create') {
        response = await api.post('/goods-receipt-notes', data);
        if (confirm('Voucher created successfully. Generate PDF?')) {
          handleGeneratePDF(response.data);
        }
        // Reset form and prepare for next entry
        reset();
        setMode('create');
        // Fetch next voucher number
        try {
          const nextNumber = await voucherService.getNextVoucherNumber(config.nextNumberEndpoint);
          setValue('voucher_number', nextNumber);
          setValue('date', new Date().toISOString().split('T')[0]);
        } catch (err) {
          console.error('Failed to fetch next voucher number:', err);
        }
      } else if (mode === 'edit') {
        response = await api.put('/goods-receipt-notes/' + data.id, data);
        if (confirm('Voucher updated successfully. Generate PDF?')) {
          handleGeneratePDF(response.data);
        }
      }
      
      // Refresh voucher list to show latest at top
      await refreshMasterData();
      
    } catch (error) {
      console.error('Error saving goods receipt note:', error);
      alert('Failed to save goods receipt note. Please try again.');
    }
  };

  // Validation for quantities
  const validateQuantities = () => {
    let valid = true;
    fields.forEach((field, index) => {
      const received = watch(`items.${index}.received_qty`) || 0;
      const accepted = watch(`items.${index}.accepted_qty`) || 0;
      const rejected = watch(`items.${index}.rejected_qty`) || 0;
      if (accepted + rejected > received) {
        alert(`For item ${index + 1}, accepted + rejected cannot exceed received quantity.`);
        valid = false;
      }
    });
    return valid;
  };

  // Wrap submit to include validation
  const handleFormSubmit = (data: any) => {
    if (validateQuantities()) {
      _handleSubmitForm(data);
    }
  };

  // Function to get stock color
  const getStockColor = (stock: number, reorder: number) => {
    if (stock === 0) return 'error.main';
    if (stock <= reorder) return 'warning.main';
    return 'success.main';
  };

  // Memoize all selected products
  const selectedProducts = useMemo(() => {
    return fields.map((_, index) => {
      const productId = watch(`items.${index}.product_id`);
      return productList?.find((p: any) => p.id === productId) || null;
    });
  }, [fields.length, productList, watch]);

  // Effect to fetch stock when product changes
  useEffect(() => {
    fields.forEach((_, index) => {
      const productId = watch(`items.${index}.product_id`);
      if (productId) {
        setStockLoading(prev => ({ ...prev, [index]: true }));
        getStock({ queryKey: ['', { product_id: productId }] }).then(res => {
          console.log('Stock Response for product ' + productId + ':', res);
          const stockData = res[0] || { quantity: 0 };
          setValue(`items.${index}.current_stock`, stockData.quantity);
          setStockLoading(prev => ({ ...prev, [index]: false }));
        }).catch(err => {
          console.error('Failed to fetch stock:', err);
          setStockLoading(prev => ({ ...prev, [index]: false }));
        });
      } else {
        setValue(`items.${index}.current_stock`, 0);
        setStockLoading(prev => ({ ...prev, [index]: false }));
      }
    });
  }, [fields, watch, setValue]);

  // Manual fetch for voucher number if not loaded
  useEffect(() => {
    if (mode === 'create' && !nextVoucherNumber && !isLoading) {
      voucherService.getNextVoucherNumber(config.nextNumberEndpoint)
        .then(number => setValue('voucher_number', number))
        .catch(err => console.error('Failed to fetch voucher number:', err));
    }
  }, [mode, nextVoucherNumber, isLoading, setValue, config.nextNumberEndpoint]);

  const handleVoucherClick = async (voucher: any) => {
    try {
      // Fetch complete voucher data including items
      const response = await api.get(`/goods-receipt-notes/${voucher.id}`);
      const fullVoucherData = response.data;
      
      // Load the complete voucher data into the form
      setMode('view');
      reset(fullVoucherData);
    } catch (error) {
      console.error('Error fetching voucher details:', error);
      // Fallback to available data
      setMode('view');
      reset(voucher);
    }
  };
  
  // Enhanced handleEdit to fetch complete data
  const handleEditWithData = async (voucher: any) => {
    try {
      const response = await api.get(`/goods-receipt-notes/${voucher.id}`);
      const fullVoucherData = response.data;
      setMode('edit');
      reset(fullVoucherData);
    } catch (error) {
      console.error('Error fetching voucher details:', error);
      handleEdit(voucher);
    }
  };
  
  // Enhanced handleView to fetch complete data
  const handleViewWithData = async (voucher: any) => {
    try {
      const response = await api.get(`/goods-receipt-notes/${voucher.id}`);
      const fullVoucherData = response.data;
      setMode('view');
      reset(fullVoucherData);
    } catch (error) {
      console.error('Error fetching voucher details:', error);
      handleView(voucher);
    }
  };

  const indexContent = (
    <>
      {/* Voucher list table */}
      <TableContainer sx={{ maxHeight: 400 }}>
        <Table stickyHeader size="small">
          <TableHead>
            <TableRow>
              <TableCell align="center" sx={{ fontSize: 15, fontWeight: 'bold', p: 1 }}>Voucher No.</TableCell>
              <TableCell align="center" sx={{ fontSize: 15, fontWeight: 'bold', p: 1 }}>Date</TableCell>
              <TableCell align="center" sx={{ fontSize: 15, fontWeight: 'bold', p: 1 }}>Vendor</TableCell>
              <TableCell align="center" sx={{ fontSize: 15, fontWeight: 'bold', p: 1 }}>Amount</TableCell>
              <TableCell align="right" sx={{ fontSize: 15, fontWeight: 'bold', p: 0, width: 40 }}></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {latestVouchers.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} align="center">No goods receipt notes available</TableCell>
              </TableRow>
            ) : (
              latestVouchers.slice(0, 7).map((voucher: any) => (
                <TableRow 
                  key={voucher.id} 
                  hover 
                  onContextMenu={(e) => { e.preventDefault(); handleContextMenu(e, voucher); }}
                  sx={{ cursor: 'pointer' }}
                >
                  <TableCell align="center" sx={{ fontSize: 12, p: 1 }} onClick={() => handleViewWithData(voucher)}>
                    {voucher.voucher_number}
                  </TableCell>
                  <TableCell align="center" sx={{ fontSize: 12, p: 1 }}>
                    {voucher.date ? new Date(voucher.date).toLocaleDateString() : 'N/A'}
                  </TableCell>
                  <TableCell align="center" sx={{ fontSize: 12, p: 1 }}>{vendorList?.find((v: any) => v.id === voucher.vendor_id)?.name || 'N/A'}</TableCell>
                  <TableCell align="center" sx={{ fontSize: 12, p: 1 }}>₹{voucher.total_amount?.toLocaleString() || '0'}</TableCell>
                  <TableCell align="right" sx={{ fontSize: 12, p: 0 }}>
                    <VoucherContextMenu
                      voucher={voucher}
                      voucherType="Goods Receipt Note"
                      onView={() => handleViewWithData(voucher)}
                      onEdit={() => handleEditWithData(voucher)}
                      onDelete={() => handleDelete(voucher)}
                      onPrint={() => handleGeneratePDF(voucher)}
                      showKebab={true}
                      onClose={() => {}}
                    />
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </>
  );

  const formContent = (
    <Box>
      {/* Header Actions */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h5" sx={{ fontSize: 20, fontWeight: 'bold', textAlign: 'center', flex: 1 }}>
          {config.voucherTitle} - {mode === 'create' ? 'Create' : mode === 'edit' ? 'Edit' : 'View'}
        </Typography>
        <VoucherHeaderActions
          mode={mode}
          voucherType={config.voucherTitle}
          voucherRoute="/vouchers/Purchase-Vouchers/grn"
          currentId={selectedVendorId}
        />
      </Box>

      <form onSubmit={handleSubmit(handleFormSubmit)} style={voucherStyles.formContainer}>
        <Grid container spacing={1}>
          {/* Voucher Number */}
          <Grid size={6}>
            <TextField
              fullWidth
              label="Voucher Number"
              {...control.register('voucher_number')}
              disabled
              InputLabelProps={{ shrink: true, style: { fontSize: 12 } }}
              inputProps={{ style: { fontSize: 14, textAlign: 'center', fontWeight: 'bold' } }}
              size="small"
              sx={{ '& .MuiInputBase-root': { height: 27 } }}
            />
          </Grid>

          {/* Date */}
          <Grid size={6}>
            <TextField
              fullWidth
              label="Date"
              type="date"
              {...control.register('date')}
              disabled={mode === 'view'}
              InputLabelProps={{ shrink: true, style: { fontSize: 12, display: 'block', visibility: 'visible' } }}
              inputProps={{ style: { fontSize: 14, textAlign: 'center' } }}
              size="small"
              sx={{ '& .MuiInputBase-root': { height: 27 } }}
            />
          </Grid>

          {/* Voucher Type */}
          <Grid size={4}>
            <Autocomplete
              size="small"
              options={[{value: 'purchase-order', label: 'Purchase Order'}, {value: 'purchase-voucher', label: 'Purchase Voucher'}]}
              getOptionLabel={(option: any) => option.label}
              value={selectedVoucherType ? {value: selectedVoucherType, label: selectedVoucherType === 'purchase-order' ? 'Purchase Order' : 'Purchase Voucher'} : null}
              onChange={(_, newValue) => {
                setSelectedVoucherType(newValue?.value || null);
                setSelectedVoucherId(null);
              }}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Voucher Type"
                  InputLabelProps={{ shrink: true, style: { fontSize: 12 } }}
                  inputProps={{ ...params.inputProps, style: { fontSize: 14 } }}
                  size="small"
                  sx={{ '& .MuiInputBase-root': { height: 27 } }}
                />
              )}
              disabled={mode === 'view'}
            />
          </Grid>

          {/* Voucher Number */}
          <Grid size={4}>
            <Autocomplete
              size="small"
              options={voucherOptions}
              getOptionLabel={(option: any) => option.voucher_number}
              value={voucherOptions.find((v: any) => v.id === selectedVoucherId) || null}
              onChange={(_, newValue) => {
                setSelectedVoucherId(newValue?.id || null);
              }}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Voucher Number"
                  InputLabelProps={{ shrink: true, style: { fontSize: 12 } }}
                  inputProps={{ ...params.inputProps, style: { fontSize: 14 } }}
                  size="small"
                  sx={{ '& .MuiInputBase-root': { height: 27 } }}
                />
              )}
              disabled={mode === 'view' || !selectedVoucherType}
            />
          </Grid>

          {/* Vendor */}
          <Grid size={4}>
            <Autocomplete
              size="small"
              options={enhancedVendorOptions}
              getOptionLabel={(option: any) => option?.name || ''}
              value={selectedVendor || null}
              onChange={(_, newValue) => {
                if (newValue?.id === null) {
                  setShowAddCustomerModal(true);
                } else {
                  setValue('vendor_id', newValue?.id || null);
                }
              }}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Vendor"
                  error={!!errors.vendor_id}
                  helperText={errors.vendor_id ? 'Required' : ''}
                  InputLabelProps={{ shrink: true, style: { fontSize: 12 } }}
                  inputProps={{ ...params.inputProps, style: { fontSize: 14 } }}
                  size="small"
                  sx={{ '& .MuiInputBase-root': { height: 27 } }}
                />
              )}
              disabled={mode === 'view' || !!selectedVoucherId} // Disable if voucher selected
            />
          </Grid>

          <Grid size={12}>
            <TextField
              fullWidth
              label="Notes"
              {...control.register('notes')}
              multiline
              rows={2}
              disabled={mode === 'view'}
              InputLabelProps={{ shrink: true, style: { fontSize: 12 } }}
              inputProps={{ style: { fontSize: 14 } }}
              size="small"
            />
          </Grid>

          {/* Items section */}
          <Grid size={12} sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 27 }}>
            <Typography variant="h6" sx={{ fontSize: 16, fontWeight: 'bold', textAlign: 'center' }}>Items</Typography>
          </Grid>

          {/* Items Table */}
          <Grid size={12}>
            <TableContainer component={Paper} sx={{ maxHeight: 300, ...voucherStyles.centeredTable, ...voucherStyles.optimizedTableContainer }}>
              <Table stickyHeader size="small">
                <TableHead>
                  <TableRow>
                    <TableCell sx={voucherStyles.grnTableColumns.productName}>Product</TableCell>
                    <TableCell sx={voucherStyles.grnTableColumns.orderQty}>Order Qty</TableCell>
                    <TableCell sx={voucherStyles.grnTableColumns.receivedQty}>Received Qty</TableCell>
                    <TableCell sx={voucherStyles.grnTableColumns.acceptedQty}>Accepted Qty</TableCell>
                    <TableCell sx={voucherStyles.grnTableColumns.rejectedQty}>Rejected Qty</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {fields.map((field: any, index: number) => (
                    <React.Fragment key={field.id}>
                      <TableRow>
                        <TableCell sx={{ p: 1, textAlign: 'center' }}>
                          <TextField
                            fullWidth
                            value={selectedProducts[index]?.name || ''}
                            disabled
                            size="small"
                            inputProps={{ style: { textAlign: 'center' } }}
                          />
                        </TableCell>
                        <TableCell sx={{ p: 1, textAlign: 'center' }}>
                          <TextField
                            type="number"
                            value={watch(`items.${index}.order_qty`)}
                            disabled
                            size="small"
                            sx={{ width: 80 }}
                            inputProps={{ style: { textAlign: 'center' } }}
                          />
                        </TableCell>
                        <TableCell sx={{ p: 1, textAlign: 'center' }}>
                          <TextField
                            type="number"
                            inputProps={{ style: { textAlign: 'center' } }}
                          />
                        </TableCell>
                        <TableCell sx={{ p: 1, textAlign: 'center' }}>
                          <TextField
                            type="number"
                            {...control.register(`items.${index}.accepted_qty`, { valueAsNumber: true })}
                            disabled={mode === 'view'}
                            size="small"
                            sx={{ width: 80 }}
                            inputProps={{ style: { textAlign: 'center' } }}
                          />
                        </TableCell>
                        <TableCell sx={{ p: 1, textAlign: 'center' }}>
                          <TextField
                            type="number"
                            {...control.register(`items.${index}.rejected_qty`, { valueAsNumber: true })}
                            disabled={mode === 'view'}
                            size="small"
                            sx={{ width: 80 }}
                            inputProps={{ style: { textAlign: 'center' } }}
                          />
                        </TableCell>
                      </TableRow>
                      {/* Hide stock display below the row for GRN */}
                    </React.Fragment>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Grid>

          {/* GRN does not have totals section - removed as per requirements */}

          {/* Action buttons */}
          <Grid size={12}>
            <Box sx={{ mt: 2, display: 'flex', gap: 1, justifyContent: 'center' }}>
              {mode !== 'view' && (
                <Button 
                  type="submit" 
                  variant="contained" 
                  color="success" 
                  disabled={createMutation.isPending || updateMutation.isPending}
                  sx={{ fontSize: 12 }}
                >
                  Save
                </Button>
              )}
            </Box>
          </Grid>
        </Grid>
      </form>
    </Box>
  );

  if (isLoading) {
    return (
      <Container>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <>
      <VoucherLayout
        voucherType={config.voucherTitle}
        voucherTitle={config.voucherTitle}
        indexContent={indexContent}
        formContent={formContent}
        onShowAll={() => setShowVoucherListModal(true)}
        pagination={paginationData ? {
          currentPage: currentPage,
          totalPages: paginationData.totalPages,
          onPageChange: handlePageChange,
          totalItems: paginationData.totalItems
        } : undefined}
        centerAligned={true}
        modalContent={
          <VoucherListModal
            open={showVoucherListModal}
            onClose={() => setShowVoucherListModal(false)}
            voucherType="Goods Receipt Notes"
            vouchers={sortedVouchers || []}
            onVoucherClick={handleVoucherClick}
            onEdit={handleEditWithData}
            onView={handleViewWithData}
            onDelete={handleDelete}
            onGeneratePDF={handleGeneratePDF}
            customerList={vendorList}
          />
        }
      />

      {/* Modals */}
      <AddVendorModal 
        open={showAddCustomerModal}
        onClose={() => setShowAddCustomerModal(false)}
        onVendorAdded={refreshMasterData}
        loading={addCustomerLoading}
        setLoading={setAddCustomerLoading}
      />

      <AddProductModal 
        open={showAddProductModal}
        onClose={() => setShowAddProductModal(false)}
        onProductAdded={refreshMasterData}
        loading={addProductLoading}
        setLoading={setAddProductLoading}
      />

      <AddShippingAddressModal 
        open={showShippingModal}
        onClose={() => setShowShippingModal(false)}
        loading={addShippingLoading}
        setLoading={setAddShippingLoading}
      />

      <VoucherContextMenu
        contextMenu={contextMenu}
        onClose={handleCloseContextMenu}
        onEdit={handleEditWithData}
        onView={handleViewWithData}
        onDelete={handleDelete}
        onPrint={handleGeneratePDF}
      />
    </>
  );
};

export default GoodsReceiptNotePage;