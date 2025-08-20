// GRN (Goods Receipt Note) Page - Refactored using shared DRY logic with QC extensions
import React, { useState, useCallback, useMemo } from 'react';
import { Box, Button, TextField, Typography, Grid, IconButton, Alert, CircularProgress, Container, Checkbox, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Autocomplete, createFilterOptions, InputAdornment, Tooltip, Switch, FormControlLabel, Modal } from '@mui/material';
import { Add, Remove, Visibility, Edit, Check } from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { voucherService } from '../../../services/authService';
import AddVendorModal from '../../../components/AddVendorModal';
import AddProductModal from '../../../components/AddProductModal';
import VoucherContextMenu from '../../../components/VoucherContextMenu';
import VoucherHeaderActions from '../../../components/VoucherHeaderActions';
import ProductAutocomplete from '../../../components/ProductAutocomplete';
import { useVoucherPage } from '../../../hooks/useVoucherPage';
import { getVoucherConfig, numberToWords } from '../../../utils/voucherUtils';

const GoodsReceiptNote: React.FC = () => {
  const config = getVoucherConfig('grn');
  const {
    // State
    mode,
    isLoading,
    showAddVendorModal,
    setShowAddVendorModal,
    showAddProductModal,
    setShowAddProductModal,
    addVendorLoading,
    setAddVendorLoading,
    addProductLoading,
    setAddProductLoading,
    addingItemIndex,
    setAddingItemIndex,
    showFullModal,
    contextMenu,
    selectedReferenceType,
    setSelectedReferenceType,
    selectedReferenceId,
    setSelectedReferenceId,
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
  } = useVoucherPage(config);

  // GRN-specific state for QC features
  const [qcIndex, setQcIndex] = useState(-1);
  const [qcDone, setQcDone] = useState<boolean[]>([]);

  // QC-specific calculations
  const qcCalculations = useMemo(() => {
    if (qcIndex >= 0 && qcIndex < fields.length) {
      const received = watch(`items.${qcIndex}.received_quantity`) || 0;
      const accepted = watch(`items.${qcIndex}.accepted_quantity`) || 0;
      const rejected = watch(`items.${qcIndex}.rejected_quantity`) || 0;
      const isValid = received === (accepted + rejected);
      return { received, accepted, rejected, isValid };
    }
    return { received: 0, accepted: 0, rejected: 0, isValid: true };
  }, [qcIndex, watch, fields.length]);

  // Reference voucher queries for GRN
  const { data: referenceVouchers } = useQuery({
    queryKey: ['reference-vouchers', selectedReferenceType],
    queryFn: () => voucherService.getVouchers(selectedReferenceType!, { pending: true }),
    enabled: !!selectedReferenceType
  });

  const { data: selectedReferenceData } = useQuery({
    queryKey: ['selected-reference', selectedReferenceType, selectedReferenceId],
    queryFn: () => voucherService.getVoucherById(selectedReferenceType!, selectedReferenceId!),
    enabled: !!selectedReferenceType && !!selectedReferenceId
  });

  // GRN-specific handlers
  const handleQCToggle = useCallback((index: number) => {
    setQcDone(prev => {
      const newQcDone = [...prev];
      newQcDone[index] = !newQcDone[index];
      setValue(`items.${index}.quality_status`, newQcDone[index] ? 'passed' : 'pending');
      return newQcDone;
    });
  }, [setValue]);

  const handleQCStart = useCallback((index: number) => {
    setQcIndex(index);
  }, []);

  const handleQCFinish = useCallback(() => {
    if (qcCalculations.isValid) {
      handleQCToggle(qcIndex);
      setQcIndex(-1);
    }
  }, [qcCalculations.isValid, handleQCToggle, qcIndex]);

  const handleReferenceSelect = useCallback((referenceVoucher: any) => {
    if (referenceVoucher && referenceVoucher.items) {
      // Auto-populate GRN items from reference voucher
      const grnItems = referenceVoucher.items.map((item: any) => ({
        product_id: item.product_id,
        po_item_id: item.id,
        ordered_quantity: item.quantity,
        received_quantity: 0,
        accepted_quantity: 0,
        rejected_quantity: 0,
        unit: item.unit,
        unit_price: item.unit_price,
        total_cost: 0,
        remarks: '',
        quality_status: 'pending'
      }));
      
      setValue('items', grnItems);
      setQcDone(new Array(grnItems.length).fill(false));
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
              <Typography variant="h6">Goods Receipt Notes</Typography>
              <VoucherHeaderActions
                onCreate={handleCreate}
                onSearch={handleModalOpen}
                voucherType="GRN"
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
                      <TableCell>GRN #</TableCell>
                      <TableCell>Date</TableCell>
                      <TableCell>Vendor</TableCell>
                      <TableCell>Status</TableCell>
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
                        <TableCell>{voucher.inspection_status || 'pending'}</TableCell>
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
              {mode === 'create' ? 'Create' : mode === 'edit' ? 'Edit' : 'View'} Goods Receipt Note
            </Typography>

            <form onSubmit={handleSubmit(handleSubmitForm)} className="space-y-4">
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <TextField
                    {...control.register('voucher_number')}
                    label="GRN Number"
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
                    options={['purchase-orders', 'purchase-vouchers']}
                    getOptionLabel={(option) => option === 'purchase-orders' ? 'Purchase Order' : 'Purchase Voucher'}
                    value={selectedReferenceType}
                    onChange={(_, value) => setSelectedReferenceType(value)}
                    disabled={mode === 'view'}
                    renderInput={(params) => (
                      <TextField {...params} label="Reference Type" />
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

                {/* Items Section */}
                <Grid item xs={12}>
                  <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="subtitle1">Items</Typography>
                    {mode !== 'view' && (
                      <Button
                        variant="outlined"
                        size="small"
                        onClick={() => append({ 
                          product_id: null, 
                          po_item_id: null,
                          ordered_quantity: 0, 
                          received_quantity: 0,
                          accepted_quantity: 0,
                          rejected_quantity: 0,
                          unit: '', 
                          unit_price: 0, 
                          total_cost: 0,
                          remarks: '',
                          quality_status: 'pending'
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
                          <TableCell>Ordered</TableCell>
                          <TableCell>Received</TableCell>
                          <TableCell>Accepted</TableCell>
                          <TableCell>Rejected</TableCell>
                          <TableCell>Unit Price</TableCell>
                          <TableCell>Total</TableCell>
                          <TableCell>QC</TableCell>
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
                                    setValue(`items.${index}.unit`, product.unit || '');
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
                                {...control.register(`items.${index}.ordered_quantity`, { valueAsNumber: true })}
                                size="small"
                                type="number"
                                disabled={mode === 'view'}
                                sx={{ width: 80 }}
                              />
                            </TableCell>
                            <TableCell>
                              <TextField
                                {...control.register(`items.${index}.received_quantity`, { valueAsNumber: true })}
                                size="small"
                                type="number"
                                disabled={mode === 'view'}
                                sx={{ width: 80 }}
                              />
                            </TableCell>
                            <TableCell>
                              <TextField
                                {...control.register(`items.${index}.accepted_quantity`, { valueAsNumber: true })}
                                size="small"
                                type="number"
                                disabled={mode === 'view' || qcIndex !== index}
                                sx={{ width: 80 }}
                              />
                            </TableCell>
                            <TableCell>
                              <TextField
                                {...control.register(`items.${index}.rejected_quantity`, { valueAsNumber: true })}
                                size="small"
                                type="number"
                                disabled={mode === 'view' || qcIndex !== index}
                                sx={{ width: 80 }}
                              />
                            </TableCell>
                            <TableCell>
                              <TextField
                                {...control.register(`items.${index}.unit_price`, { valueAsNumber: true })}
                                size="small"
                                type="number"
                                disabled={mode === 'view'}
                                sx={{ width: 100 }}
                              />
                            </TableCell>
                            <TableCell>
                              ₹{(computedItems[index]?.total_amount || 0).toFixed(2)}
                            </TableCell>
                            <TableCell>
                              {mode !== 'view' && (
                                qcIndex === index ? (
                                  <Box sx={{ display: 'flex', gap: 0.5 }}>
                                    <Button
                                      size="small"
                                      variant="contained"
                                      color={qcCalculations.isValid ? "success" : "error"}
                                      onClick={handleQCFinish}
                                      disabled={!qcCalculations.isValid}
                                    >
                                      <Check fontSize="small" />
                                    </Button>
                                    <Button
                                      size="small"
                                      variant="outlined"
                                      onClick={() => setQcIndex(-1)}
                                    >
                                      Cancel
                                    </Button>
                                  </Box>
                                ) : (
                                  <FormControlLabel
                                    control={
                                      <Checkbox
                                        checked={qcDone[index] || false}
                                        onChange={() => handleQCToggle(index)}
                                        disabled={qcIndex >= 0 && qcIndex !== index}
                                      />
                                    }
                                    label={qcDone[index] ? "Passed" : "Pending"}
                                    onClick={() => !qcDone[index] && handleQCStart(index)}
                                  />
                                )
                              )}
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

                {/* QC Status Display */}
                {qcIndex >= 0 && (
                  <Grid item xs={12}>
                    <Alert 
                      severity={qcCalculations.isValid ? "success" : "warning"}
                      sx={{ mb: 2 }}
                    >
                      <Typography variant="body2">
                        QC for item {qcIndex + 1}: 
                        Received: {qcCalculations.received}, 
                        Accepted: {qcCalculations.accepted}, 
                        Rejected: {qcCalculations.rejected}
                        {!qcCalculations.isValid && " - Totals don't match!"}
                      </Typography>
                    </Alert>
                  </Grid>
                )}

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
                  <Typography variant="h6" align="right">
                    Total Amount: ₹{totalAmount.toFixed(2)}
                  </Typography>
                  {totalAmount > 0 && (
                    <Typography variant="body2" align="right" color="textSecondary">
                      {numberToWords(totalAmount)}
                    </Typography>
                  )}
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
                        disabled={createMutation.isPending || updateMutation.isPending || qcIndex >= 0}
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

      {/* Context Menu */}
      {contextMenu !== null && (
        <VoucherContextMenu
          voucher={contextMenu.voucher}
          voucherType="GRN"
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
            Search Goods Receipt Notes
          </Typography>
          
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} md={4}>
              <TextField
                label="Search"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                fullWidth
                placeholder="GRN number, vendor, notes..."
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
                  <TableCell>GRN #</TableCell>
                  <TableCell>Date</TableCell>
                  <TableCell>Vendor</TableCell>
                  <TableCell>Status</TableCell>
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
                    <TableCell>{voucher.inspection_status || 'pending'}</TableCell>
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

export default GoodsReceiptNote;