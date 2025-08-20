// Purchase Return Page - Refactored using shared DRY logic  
import React, { useCallback } from 'react';
import { Box, Button, TextField, Typography, Grid, IconButton, Alert, CircularProgress, Container, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Autocomplete, createFilterOptions, InputAdornment, Tooltip, Switch, FormControlLabel, Modal } from '@mui/material';
import { Add, Remove, Visibility, Edit } from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { voucherService } from '../../../services/authService';
import AddVendorModal from '../../../components/AddVendorModal';
import AddProductModal from '../../../components/AddProductModal';
import AddShippingAddressModal from '../../../components/AddShippingAddressModal';
import VoucherContextMenu from '../../../components/VoucherContextMenu';
import VoucherHeaderActions from '../../../components/VoucherHeaderActions';
import ProductAutocomplete from '../../../components/ProductAutocomplete';
import { useVoucherPage } from '../../../hooks/useVoucherPage';
import { getVoucherConfig, numberToWords, GST_SLABS } from '../../../utils/voucherUtils';

const PurchaseReturnPage: React.FC = () => {
  const config = getVoucherConfig('purchase-return');
  const {
    // State
    mode,
    isLoading,
    showAddVendorModal,
    setShowAddVendorModal,
    showAddProductModal,
    setShowAddProductModal,
    showShippingModal,
    setShowShippingModal,
    addVendorLoading,
    setAddVendorLoading,
    addProductLoading,
    setAddProductLoading,
    addShippingLoading,
    setAddShippingLoading,
    addingItemIndex,
    setAddingItemIndex,
    showFullModal,
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
    watch,
    setValue,
    errors,
    fields,
    append,
    remove,

    // Data
    voucherList,
    vendorList,
    productList,
    sortedVouchers,
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
    handleCloseContextMenu: handleContextMenuClose,
    handleSearch,
    handleModalOpen,
    handleModalClose,
    handleGeneratePDF,
    handleDelete,
    handleAddVendor,
    handleAddProduct,
    handleAddShipping,
  } = useVoucherPage(config);

  // Reference voucher queries for returns
  const { data: referenceVouchers } = useQuery({
    queryKey: ['reference-vouchers', selectedReferenceType],
    queryFn: () => voucherService.getVouchers(selectedReferenceType!, { returnable: true }),
    enabled: !!selectedReferenceType
  });

  const { data: selectedReferenceData } = useQuery({
    queryKey: ['selected-reference', selectedReferenceType, selectedReferenceId],
    queryFn: () => voucherService.getVoucherById(selectedReferenceType!, selectedReferenceId!),
    enabled: !!selectedReferenceType && !!selectedReferenceId
  });

  const handleReferenceSelect = useCallback((referenceVoucher: any) => {
    if (referenceVoucher && referenceVoucher.items) {
      // Auto-populate return items from reference voucher
      const returnItems = referenceVoucher.items.map((item: any) => ({
        ...item,
        returned_quantity: 0,
        return_reason: '',
        original_voucher_item_id: item.id
      }));
      
      setValue('items', returnItems);
      setValue('vendor_id', referenceVoucher.vendor_id);
    }
  }, [setValue]);

  const nameFilter = createFilterOptions();

  return (
    <Container maxWidth="xl" sx={{ py: 2 }}>
      <Grid container spacing={3}>
        {/* Left side - Voucher List */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: 'calc(100vh - 120px)', display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">Purchase Returns</Typography>
              <VoucherHeaderActions
                onCreate={handleCreate}
                onSearch={handleModalOpen}
                voucherType="Purchase Return"
              />
            </Box>

            {isLoading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                <CircularProgress />
              </Box>
            ) : (
              <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Sr.</TableCell>
                      <TableCell>Return #</TableCell>
                      <TableCell>Date</TableCell>
                      <TableCell>Vendor</TableCell>
                      <TableCell>Reference</TableCell>
                      <TableCell>Total</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {sortedVouchers?.map((voucher: any, index: number) => (
                      <TableRow 
                        key={voucher.id} 
                        hover
                        onContextMenu={(e) => handleContextMenu(e, voucher)}
                        sx={{ cursor: 'context-menu' }}
                      >
                        <TableCell>{index + 1}</TableCell>
                        <TableCell>{voucher.voucher_number}</TableCell>
                        <TableCell>{new Date(voucher.date).toLocaleDateString()}</TableCell>
                        <TableCell>{voucher.vendor?.name || 'N/A'}</TableCell>
                        <TableCell>{voucher.reference || 'N/A'}</TableCell>
                        <TableCell>₹{voucher.total_amount?.toFixed(2) || '0.00'}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Right side - Voucher Form */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: 'calc(100vh - 120px)', overflow: 'auto' }}>
            <Typography variant="h6" gutterBottom>
              {mode === 'create' ? 'Create' : mode === 'edit' ? 'Edit' : 'View'} Purchase Return
            </Typography>

            <form onSubmit={handleSubmit(handleSubmitForm)} className="space-y-4">
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <TextField
                    {...control.register('voucher_number')}
                    label="Return Number"
                    fullWidth
                    disabled={mode === 'view'}
                    error={!!errors.voucher_number}
                    helperText={errors.voucher_number?.message}
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    {...control.register('date')}
                    label="Date"
                    type="date"
                    fullWidth
                    disabled={mode === 'view'}
                    InputLabelProps={{ shrink: true }}
                    error={!!errors.date}
                    helperText={errors.date?.message}
                  />
                </Grid>

                {/* Reference Selection */}
                <Grid item xs={6}>
                  <Autocomplete
                    options={['purchase-vouchers', 'goods-receipt-notes']}
                    getOptionLabel={(option) => 
                      option === 'purchase-vouchers' ? 'Purchase Voucher' : 'Goods Receipt Note'
                    }
                    value={selectedReferenceType}
                    onChange={(_, value) => setSelectedReferenceType(value)}
                    disabled={mode === 'view'}
                    renderInput={(params) => (
                      <TextField {...params} label="Return Against" />
                    )}
                  />
                </Grid>

                <Grid item xs={6}>
                  <Autocomplete
                    options={referenceVouchers || []}
                    getOptionLabel={(option: any) => option?.voucher_number || ''}
                    value={referenceVouchers?.find((v: any) => v.id === selectedReferenceId) || null}
                    onChange={(_, value: any) => {
                      setSelectedReferenceId(value?.id || null);
                      if (value) handleReferenceSelect(value);
                    }}
                    disabled={!selectedReferenceType || mode === 'view'}
                    renderInput={(params) => (
                      <TextField {...params} label="Reference Voucher" />
                    )}
                  />
                </Grid>

                <Grid item xs={12}>
                  <Autocomplete
                    options={vendorList || []}
                    getOptionLabel={(option: any) => option?.name || ''}
                    value={vendorList?.find((vendor: any) => vendor.id === watch('vendor_id')) || null}
                    onChange={(_, value: any) => setValue('vendor_id', value?.id || null)}
                    filterOptions={nameFilter}
                    disabled={mode === 'view'}
                    renderInput={(params) => (
                      <TextField 
                        {...params} 
                        label="Vendor" 
                        error={!!errors.vendor_id}
                        helperText={errors.vendor_id?.message}
                        InputProps={{
                          ...params.InputProps,
                          endAdornment: (
                            <>
                              {params.InputProps.endAdornment}
                              <InputAdornment position="end">
                                <Tooltip title="Add Vendor">
                                  <Button
                                    size="small"
                                    onClick={handleAddVendor}
                                    sx={{ minWidth: 'auto', p: 0.5 }}
                                  >
                                    <Add fontSize="small" />
                                  </Button>
                                </Tooltip>
                              </InputAdornment>
                            </>
                          ),
                        }}
                      />
                    )}
                  />
                </Grid>

                <Grid item xs={6}>
                  <TextField
                    {...control.register('reference')}
                    label="Reference"
                    fullWidth
                    disabled={mode === 'view'}
                    error={!!errors.reference}
                    helperText={errors.reference?.message}
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    {...control.register('return_reason')}
                    label="Return Reason"
                    fullWidth
                    disabled={mode === 'view'}
                  />
                </Grid>

                {/* Items Section */}
                <Grid item xs={12}>
                  <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="subtitle1">Return Items</Typography>
                    {mode !== 'view' && (
                      <Button
                        variant="outlined"
                        size="small"
                        onClick={() => append({ 
                          product_id: null, 
                          hsn_code: '', 
                          quantity: 0, 
                          returned_quantity: 0,
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
                          total_amount: 0,
                          return_reason: '',
                          original_voucher_item_id: null
                        })}
                        startIcon={<Add />}
                      >
                        Add Item
                      </Button>
                    )}
                  </Box>

                  <TableContainer component={Paper} variant="outlined">
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Product</TableCell>
                          <TableCell>HSN</TableCell>
                          <TableCell>Original Qty</TableCell>
                          <TableCell>Return Qty</TableCell>
                          <TableCell>Unit</TableCell>
                          <TableCell>Rate</TableCell>
                          <TableCell>GST%</TableCell>
                          <TableCell>Amount</TableCell>
                          <TableCell>Reason</TableCell>
                          <TableCell>Actions</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {fields.map((field, index) => (
                          <TableRow key={field.id}>
                            <TableCell>
                              <ProductAutocomplete
                                value={productList?.find((p: any) => p.id === watch(`items.${index}.product_id`)) || null}
                                onChange={(product: any) => {
                                  setValue(`items.${index}.product_id`, product?.id || null);
                                  if (product) {
                                    setValue(`items.${index}.hsn_code`, product.hsn_code || '');
                                    setValue(`items.${index}.unit`, product.unit || '');
                                    setValue(`items.${index}.unit_price`, product.selling_price || 0);
                                    setValue(`items.${index}.original_unit_price`, product.selling_price || 0);
                                    setValue(`items.${index}.gst_rate`, product.gst_rate || 0);
                                  }
                                }}
                                disabled={mode === 'view'}
                                onAddNew={() => {
                                  setAddingItemIndex(index);
                                  handleAddProduct();
                                }}
                                error={!!errors.items?.[index]?.product_id}
                              />
                            </TableCell>
                            <TableCell>
                              <TextField
                                {...control.register(`items.${index}.hsn_code`)}
                                size="small"
                                disabled={mode === 'view'}
                                sx={{ width: 80 }}
                              />
                            </TableCell>
                            <TableCell>
                              <TextField
                                {...control.register(`items.${index}.quantity`, { valueAsNumber: true })}
                                size="small"
                                type="number"
                                disabled={mode === 'view'}
                                sx={{ width: 70 }}
                              />
                            </TableCell>
                            <TableCell>
                              <TextField
                                {...control.register(`items.${index}.returned_quantity`, { valueAsNumber: true })}
                                size="small"
                                type="number"
                                disabled={mode === 'view'}
                                sx={{ width: 70 }}
                              />
                            </TableCell>
                            <TableCell>
                              <TextField
                                {...control.register(`items.${index}.unit`)}
                                size="small"
                                disabled={mode === 'view'}
                                sx={{ width: 60 }}
                              />
                            </TableCell>
                            <TableCell>
                              <TextField
                                {...control.register(`items.${index}.unit_price`, { valueAsNumber: true })}
                                size="small"
                                type="number"
                                disabled={mode === 'view'}
                                sx={{ width: 80 }}
                              />
                            </TableCell>
                            <TableCell>
                              <Autocomplete
                                options={GST_SLABS}
                                value={watch(`items.${index}.gst_rate`) || 0}
                                onChange={(_, value) => setValue(`items.${index}.gst_rate`, value || 0)}
                                disabled={mode === 'view'}
                                renderInput={(params) => (
                                  <TextField
                                    {...params}
                                    size="small"
                                    sx={{ width: 70 }}
                                  />
                                )}
                              />
                            </TableCell>
                            <TableCell>
                              ₹{(computedItems[index]?.total_amount || 0).toFixed(2)}
                            </TableCell>
                            <TableCell>
                              <TextField
                                {...control.register(`items.${index}.return_reason`)}
                                size="small"
                                disabled={mode === 'view'}
                                sx={{ width: 100 }}
                                placeholder="Reason"
                              />
                            </TableCell>
                            <TableCell>
                              {mode !== 'view' && (
                                <IconButton
                                  size="small"
                                  onClick={() => remove(index)}
                                  disabled={fields.length === 1}
                                >
                                  <Remove fontSize="small" />
                                </IconButton>
                              )}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    {...control.register('notes')}
                    label="Notes"
                    fullWidth
                    multiline
                    rows={2}
                    disabled={mode === 'view'}
                  />
                </Grid>

                <Grid item xs={12}>
                  <Box sx={{ mt: 2, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
                    <Grid container spacing={2}>
                      <Grid item xs={6}>
                        <Typography variant="body2">Subtotal: ₹{totalSubtotal.toFixed(2)}</Typography>
                        <Typography variant="body2">GST: ₹{totalGst.toFixed(2)}</Typography>
                        <Typography variant="h6">Return Total: ₹{totalAmount.toFixed(2)}</Typography>
                      </Grid>
                      <Grid item xs={6}>
                        {totalAmount > 0 && (
                          <Typography variant="body2" color="textSecondary">
                            Amount in words: {numberToWords(totalAmount)}
                          </Typography>
                        )}
                      </Grid>
                    </Grid>
                  </Box>
                </Grid>

                {mode !== 'view' && (
                  <Grid item xs={12}>
                    <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                      <Button 
                        variant="outlined" 
                        onClick={handleCreate}
                        disabled={createMutation.isPending || updateMutation.isPending}
                      >
                        Clear
                      </Button>
                      <Button 
                        type="submit" 
                        variant="contained"
                        disabled={createMutation.isPending || updateMutation.isPending}
                      >
                        {createMutation.isPending || updateMutation.isPending ? 
                          <CircularProgress size={20} /> : 
                          (mode === 'create' ? 'Create' : 'Update')
                        }
                      </Button>
                      <Button 
                        variant="outlined" 
                        onClick={() => handleGeneratePDF()}
                        disabled={!watch('voucher_number')}
                      >
                        Save as PDF
                      </Button>
                    </Box>
                  </Grid>
                )}
              </Grid>
            </form>
          </Paper>
        </Grid>
      </Grid>

      {/* Add Vendor Modal */}
      <AddVendorModal
        open={showAddVendorModal}
        onClose={() => setShowAddVendorModal(false)}
        onAdd={handleAddVendor}
        loading={addVendorLoading}
      />

      {/* Add Product Modal */}
      <AddProductModal
        open={showAddProductModal}
        onClose={() => setShowAddProductModal(false)}
        onAdd={handleAddProduct}
        loading={addProductLoading}
      />

      {/* Add Shipping Address Modal */}
      <AddShippingAddressModal
        open={showShippingModal}
        onClose={() => setShowShippingModal(false)}
        onAdd={handleAddShipping}
        loading={addShippingLoading}
      />

      {/* Context Menu */}
      {contextMenu !== null && (
        <VoucherContextMenu
          voucher={contextMenu.voucher}
          voucherType="Purchase Return"
          onEdit={handleEdit}
          onView={handleView}
          onDelete={handleDelete}
          onPrint={() => handleGeneratePDF(contextMenu.voucher)}
          onDuplicate={(voucher) => {
            handleCreate();
            setValue('reference', voucher.voucher_number);
          }}
          showKebab={false}
          open={true}
          onClose={handleContextMenuClose}
          anchorReference="anchorPosition"
          anchorPosition={{ top: contextMenu.mouseY, left: contextMenu.mouseX }}
        />
      )}

      {/* Search/Filter Modal */}
      <Modal open={showFullModal} onClose={handleModalClose}>
        <Box
          sx={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            width: '90%',
            maxWidth: 1000,
            bgcolor: 'background.paper',
            boxShadow: 24,
            p: 4,
            borderRadius: 2,
          }}
        >
          <Typography variant="h6" gutterBottom>
            Search Purchase Returns
          </Typography>
          
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} md={4}>
              <TextField
                label="Search"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                fullWidth
                placeholder="Return number, vendor, notes..."
              />
            </Grid>
            <Grid item xs={6} md={3}>
              <TextField
                label="From Date"
                type="date"
                value={fromDate}
                onChange={(e) => setFromDate(e.target.value)}
                InputLabelProps={{ shrink: true }}
                fullWidth
              />
            </Grid>
            <Grid item xs={6} md={3}>
              <TextField
                label="To Date"
                type="date"
                value={toDate}
                onChange={(e) => setToDate(e.target.value)}
                InputLabelProps={{ shrink: true }}
                fullWidth
              />
            </Grid>
            <Grid item xs={12} md={2}>
              <Button
                variant="contained"
                onClick={handleSearch}
                fullWidth
                sx={{ height: '56px' }}
              >
                Search
              </Button>
            </Grid>
          </Grid>

          <TableContainer component={Paper} sx={{ maxHeight: 400 }}>
            <Table stickyHeader>
              <TableHead>
                <TableRow>
                  <TableCell>Return #</TableCell>
                  <TableCell>Date</TableCell>
                  <TableCell>Vendor</TableCell>
                  <TableCell>Reference</TableCell>
                  <TableCell>Total</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredVouchers.map((voucher: any) => (
                  <TableRow key={voucher.id}>
                    <TableCell>{voucher.voucher_number}</TableCell>
                    <TableCell>{new Date(voucher.date).toLocaleDateString()}</TableCell>
                    <TableCell>{voucher.vendor?.name || 'N/A'}</TableCell>
                    <TableCell>{voucher.reference || 'N/A'}</TableCell>
                    <TableCell>₹{voucher.total_amount?.toFixed(2) || '0.00'}</TableCell>
                    <TableCell>
                      <Button
                        size="small"
                        onClick={() => {
                          handleEdit(voucher);
                          handleModalClose();
                        }}
                        startIcon={<Edit />}
                      >
                        Edit
                      </Button>
                      <Button
                        size="small"
                        onClick={() => {
                          handleView(voucher);
                          handleModalClose();
                        }}
                        startIcon={<Visibility />}
                      >
                        View
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      </Modal>
    </Container>
  );
};

export default PurchaseReturnPage;