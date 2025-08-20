// Purchase Voucher Page - Refactored using shared DRY logic
import React, { useState, useRef, useMemo, useEffect } from 'react';
import { Box, Button, TextField, Typography, Grid, IconButton, CircularProgress, Container, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Autocomplete, InputAdornment, Tooltip, Modal, LinearProgress, Alert, Chip } from '@mui/material';
import { Add, Remove, Visibility, Edit, CloudUpload, CheckCircle, Description } from '@mui/icons-material';
import { useQueryClient, useQuery } from '@tanstack/react-query';
import { createFilterOptions } from '@mui/material/Autocomplete';
import AddVendorModal from '../../../components/AddVendorModal';
import AddProductModal from '../../../components/AddProductModal';
import AddShippingAddressModal from '../../../components/AddShippingAddressModal';
import VoucherContextMenu from '../../../components/VoucherContextMenu';
import VoucherHeaderActions from '../../../components/VoucherHeaderActions';
import VoucherListModal from '../../../components/VoucherListModal';
import BalanceDisplay from '../../../components/BalanceDisplay';
import StockDisplay from '../../../components/StockDisplay';
import { useVoucherPage } from '../../../hooks/useVoucherPage';
import { getVoucherConfig, GST_SLABS } from '../../../utils/voucherUtils';
import { voucherService } from '../../../services/authService';
import api from '../../../lib/api';

const PurchaseVoucherPage: React.FC = () => {
  const config = getVoucherConfig('purchase-voucher');
  const {
    // State
    mode,
    setMode,
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
    reset,
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
    refreshMasterData,
    getAmountInWords,

    // Utilities
    isViewMode,
  } = useVoucherPage(config);
  
  // Handle voucher click to load details
  const handleVoucherClick = (voucher: any) => {
    // Load the selected voucher into the form
    setMode('view');
    reset(voucher);
    // Set the form with the voucher data
    Object.keys(voucher).forEach(key => {
      setValue(key, voucher[key]);
    });
  };

  const [selectedReferenceType, setSelectedReferenceType] = useState<string | null>(null);
  const [selectedReferenceId, setSelectedReferenceId] = useState<number | null>(null);
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [pdfUploadLoading, setPdfUploadLoading] = useState(false);
  const [pdfExtractedData, setPdfExtractedData] = useState<any>(null);
  const [pdfUploadError, setPdfUploadError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();
  const vendorInputRef = useRef<HTMLInputElement>(null);
  const productInputRefs = useRef<HTMLInputElement[]>([]);





  // Reference voucher queries for purchase vouchers
  const { data: referenceVouchers, isLoading: isLoadingReference } = useQuery({
    queryKey: ['reference-vouchers', selectedReferenceType],
    queryFn: () => voucherService.getVouchers(selectedReferenceType!),
    enabled: !!selectedReferenceType
  });

  const { data: selectedReferenceData, isLoading: isLoadingSelectedReference } = useQuery({
    queryKey: ['selected-reference', selectedReferenceType, selectedReferenceId],
    queryFn: () => voucherService.getVoucherById(selectedReferenceType!, selectedReferenceId!),
    enabled: !!selectedReferenceType && !!selectedReferenceId
  });

  // Use reference data when selected
  useEffect(() => {
    if (selectedReferenceData) {
      setValue('vendor_id', selectedReferenceData.vendor_id);
      setValue('payment_terms', selectedReferenceData.payment_terms);
      setValue('notes', selectedReferenceData.notes);
      remove();
      selectedReferenceData.items.forEach((item: any) => append(item));
    }
  }, [selectedReferenceData, setValue, append, remove]);



  // Handle PDF upload for data extraction
  const handlePdfFileUpload = async (file: File) => {
    setPdfUploadLoading(true);
    setPdfUploadError(null);
    
    try {
      // Create FormData for file upload
      const formData = new FormData();
      formData.append('file', file);
      
      // Call real PDF extraction API
      const response = await api.post('/api/v1/pdf-extraction/extract/purchase_voucher', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      if (response.data.success) {
        const extractedData = response.data.extracted_data;
        
        // Auto-populate form fields with extracted data
        if (extractedData.invoice_number) {
          setValue('invoice_number', extractedData.invoice_number);
        }
        if (extractedData.invoice_date) {
          setValue('invoice_date', extractedData.invoice_date);
        }
        if (extractedData.payment_terms) {
          setValue('payment_terms', extractedData.payment_terms);
        }
        if (extractedData.notes) {
          setValue('notes', extractedData.notes);
        }
        if (extractedData.total_amount) {
          setValue('total_amount', extractedData.total_amount);
        }
        
        // Clear existing items and add extracted items
        if (extractedData.items && extractedData.items.length > 0) {
          remove();
          extractedData.items.forEach((item: any) => {
            append({
              product_id: item.product_id,
              hsn_code: item.hsn_code || '',
              quantity: item.quantity || 0,
              unit: item.unit || 'PCS',
              unit_price: item.unit_price || 0,
              original_unit_price: item.unit_price || 0,
              discount_percentage: 0,
              discount_amount: 0,
              taxable_amount: (item.quantity || 0) * (item.unit_price || 0),
              gst_rate: item.gst_rate || 0,
              cgst_amount: ((item.quantity || 0) * (item.unit_price || 0) * (item.gst_rate || 0)) / 200,
              sgst_amount: ((item.quantity || 0) * (item.unit_price || 0) * (item.gst_rate || 0)) / 200,
              igst_amount: 0,
              total_amount: item.total_amount || 0
            });
          });
        }
        
        setPdfExtractedData(extractedData);
        setPdfFile(file);
      } else {
        setPdfUploadError('Failed to extract data from PDF');
      }
      
    } catch (error: any) {
      console.error('Error processing PDF:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to process PDF. Please try again.';
      setPdfUploadError(errorMessage);
    } finally {
      setPdfUploadLoading(false);
    }
  };

  const handleFileInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (file.type !== 'application/pdf') {
        setPdfUploadError('Please upload a PDF file');
        return;
      }
      if (file.size > 10 * 1024 * 1024) { // 10MB limit
        setPdfUploadError('File size should be less than 10MB');
        return;
      }
      handlePdfFileUpload(file);
    }
  };

  const triggerFileUpload = () => {
    fileInputRef.current?.click();
  };

  const removePdfFile = () => {
    setPdfFile(null);
    setPdfExtractedData(null);
    setPdfUploadError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleVendorAdd = async (vendorData: any) => {
    setAddVendorLoading(true);
    try {
      const response = await api.post('/vendors', vendorData);
      const newVendor = response.data;
      
      // Update query data immediately
      queryClient.setQueryData(['vendors'], (old: any) => old ? [...old, newVendor] : [newVendor]);
      queryClient.invalidateQueries({ queryKey: ['vendors'] });
      
      // Auto-select the new vendor
      setValue('vendor_id', newVendor.id);
      
      setShowAddVendorModal(false);
      alert('Vendor added successfully!');
    } catch (error: any) {
      console.error('Error adding vendor:', error);
      let errorMsg = 'Error adding vendor';
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        if (Array.isArray(detail)) {
          errorMsg += ': ' + detail.map((err: any) => `${err.loc ? err.loc.join('.') : 'Field'}: ${err.msg}`).join(', ');
        } else {
          errorMsg += ': ' + detail;
        }
      } else if (error.message) {
        errorMsg += ': ' + error.message;
      }
      alert(errorMsg);
    } finally {
      setAddVendorLoading(false);
    }
  };

  const handleProductAdd = async (productData: any) => {
    setAddProductLoading(true);
    try {
      const response = await api.post('/products', productData);
      const newProduct = response.data;
      
      // Update query data immediately
      queryClient.setQueryData(['products'], (old: any) => old ? [...old, newProduct] : [newProduct]);
      queryClient.invalidateQueries({ queryKey: ['products'] });
      
      // Auto-select in the specific row if applicable
      if (addingItemIndex !== -1) {
        setValue(`items.${addingItemIndex}.product_id`, newProduct.id);
        setValue(`items.${addingItemIndex}.hsn_code`, newProduct.hsn_code || '');
        setValue(`items.${addingItemIndex}.unit_price`, newProduct.unit_price || 0);
        setValue(`items.${addingItemIndex}.original_unit_price`, newProduct.unit_price || 0);
        setValue(`items.${addingItemIndex}.gst_rate`, newProduct.gst_rate || 0);
        setValue(`items.${addingItemIndex}.unit`, newProduct.unit || '');
        setAddingItemIndex(-1);
      }
      
      setShowAddProductModal(false);
      alert('Product added successfully!');
    } catch (error: any) {
      console.error('Error adding product:', error);
      let errorMsg = 'Error adding product';
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        if (Array.isArray(detail)) {
          errorMsg += ': ' + detail.map((err: any) => `${err.loc ? err.loc.join('.') : 'Field'}: ${err.msg}`).join(', ');
        } else {
          errorMsg += ': ' + detail;
        }
      } else if (error.message) {
        errorMsg += ': ' + error.message;
      }
      alert(errorMsg);
    } finally {
      setAddProductLoading(false);
    }
  };



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

  if (isLoading || isLoadingSelectedReference) {
    return <CircularProgress />;
  }



  const filter = createFilterOptions<any>();

  const vendorOptions = vendorList || [];
  const productOptions = productList || [];

  return (
    <Container maxWidth="xl">
      <Grid container spacing={2}>
        <Grid size={{ xs: 12, md: 4, lg: 4 }}>
          <Paper sx={{ p: 2 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
              <Typography variant="h6" sx={{ fontSize: 18, fontWeight: 'bold' }}>Purchase Vouchers</Typography>
              <Button variant="outlined" size="small" onClick={handleModalOpen}>Show All</Button>
            </Box>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Voucher #</TableCell>
                    <TableCell>Date</TableCell>
                    <TableCell>Vendor</TableCell>
                    <TableCell></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {latestVouchers.map((voucher: any) => (
                    <TableRow 
                      key={voucher.id}
                      onContextMenu={(e) => handleContextMenu(e, voucher)}
                      style={{ cursor: 'context-menu' }}
                    >
                      <TableCell>{voucher.voucher_number}</TableCell>
                      <TableCell>{new Date(voucher.date).toLocaleDateString()}</TableCell>
                      <TableCell>{vendorList?.find((c: any) => c.id === voucher.vendor_id)?.name || ''}</TableCell>
                      <TableCell align="right" sx={{ pr: 0 }}>
                        <VoucherContextMenu
                          voucher={voucher}
                          voucherType="Purchase Voucher"
                          onView={handleView}
                          onEdit={handleEdit}
                          onDelete={handleDeleteVoucher}
                          onPrint={() => handlePrintVoucher(voucher.id, voucher.voucher_number)}
                          onEmail={handleEmailVoucher}
                          showKebab={true}
                          open={false}
                          onClose={() => {}}
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>
        <Grid size={{ xs: 12, md: 8, lg: 8 }}>
          <Paper sx={{ p: 1 }}>
            <Box sx={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              mb: 1 
            }}>
              <Typography variant="h6" sx={{ fontSize: 18, fontWeight: 'bold', flexGrow: 1, textAlign: 'center' }}>
                {mode === 'create' ? 'Create Purchase Voucher' : mode === 'edit' ? 'Edit Purchase Voucher' : 'View Purchase Voucher'}
              </Typography>
              <VoucherHeaderActions
                mode={mode}
                voucherType="Purchase Voucher"
                voucherRoute="/vouchers/Purchase-Vouchers/purchase-voucher"
                currentId={selectedId || undefined}
              />
            </Box>
            <form onSubmit={handleSubmit(onSubmit)}>
              <Grid container spacing={0.5}>
                <Grid size={4}>
                  <Tooltip title={mode === 'create' ? 'Auto-generated on save' : ''} arrow>
                    <TextField
                      fullWidth
                      label="Voucher Number"
                      {...control.register('voucher_number')}
                      error={!!errors.voucher_number}
                      helperText={errors.voucher_number ? 'Required' : ''}
                      disabled={mode === 'create' || isViewMode}
                      InputLabelProps={{ shrink: true, style: { fontSize: 10, textAlign: 'center' } }}
                      inputProps={{ style: { fontSize: 12, textAlign: 'center' } }}
                      size="small"
                      sx={{ 
                        '& .MuiInputBase-root': { height: 27 },
                        width: '100%' 
                      }}
                    />
                  </Tooltip>
                </Grid>
                <Grid size={4}>
                  <TextField
                    fullWidth
                    label="Date"
                    type="date"
                    {...control.register('date', { required: true })}
                    error={!!errors.date}
                    helperText={errors.date ? 'Required' : ''}
                    disabled={isViewMode}
                    InputLabelProps={{ shrink: true, style: { fontSize: 10, textAlign: 'center' } }}
                    inputProps={{ style: { fontSize: 12, textAlign: 'center' } }}
                    size="small"
                    sx={{ 
                      '& .MuiInputBase-root': { height: 27 },
                      width: '100%' 
                    }}
                  />
                </Grid>
                <Grid size={4}>
                  <Box sx={{ display: 'flex', height: 27, alignItems: 'center' }}>
                    <Autocomplete
                      options={voucherTypes}
                      getOptionLabel={(option) => option.label}
                      onChange={(_, newValue) => {
                        setSelectedReferenceType(newValue ? newValue.slug : null);
                        setSelectedReferenceId(null);
                        setValue('reference', '');
                      }}
                      renderInput={(params) => (
                        <TextField
                          {...params}
                          label="Ref Type"
                          InputLabelProps={{ style: { fontSize: 10, textAlign: 'center' } }}
                          inputProps={{
                            ...params.inputProps,
                            style: { fontSize: 12, textAlign: 'center' }
                          }}
                          size="small"
                          sx={{ 
                            '& .MuiInputBase-root': { height: 27 },
                            borderTopRightRadius: 0,
                            borderBottomRightRadius: 0,
                            borderRight: 'none',
                          }}
                        />
                      )}
                      disabled={isViewMode}
                      sx={{ flex: 1 }}
                    />
                    <Autocomplete
                      options={referenceVouchers || []}
                      getOptionLabel={(option) => option.voucher_number}
                      onChange={(_, newValue) => {
                        setSelectedReferenceId(newValue ? newValue.id : null);
                        setValue('reference', newValue ? newValue.voucher_number : '');
                      }}
                      renderInput={(params) => (
                        <TextField
                          {...params}
                          label="Ref Number"
                          InputLabelProps={{ style: { fontSize: 10, textAlign: 'center' } }}
                          inputProps={{
                            ...params.inputProps,
                            style: { fontSize: 12, textAlign: 'center' }
                          }}
                          size="small"
                          sx={{ 
                            '& .MuiInputBase-root': { height: 27 },
                            borderTopLeftRadius: 0,
                            borderBottomLeftRadius: 0,
                          }}
                        />
                      )}
                      disabled={isViewMode || !selectedReferenceType}
                      sx={{ flex: 1 }}
                    />
                  </Box>
                </Grid>
                <Grid size={4}>
                  <Autocomplete
                    options={vendorOptions}
                    getOptionLabel={(option) => option.name || ''}
                    value={vendorOptions.find((opt: any) => opt.id === watch('vendor_id')) || null}
                    onChange={(_, newValue) => {
                      if (newValue && newValue.id === -1) {
                        if (vendorInputRef.current) {
                          vendorInputRef.current.blur();
                        }
                        handleAddVendor();
                      } else {
                        setValue('vendor_id', newValue ? newValue.id : null);
                      }
                    }}
                    openOnFocus
                    filterOptions={(options, params) => {
                      const filtered = filter(options, params);
                      if (params.inputValue !== '') {
                        filtered.unshift({ id: -1, name: `Add "${params.inputValue}"` });
                      } else {
                        filtered.unshift({ id: -1, name: 'Add Vendor' });
                      }
                      return filtered;
                    }}
                    renderOption={(props, option) => (
                      <li {...props} style={{ fontSize: 12 }}>
                        {option.id === -1 ? (
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Add sx={{ mr: 1 } } />
                            {option.name}
                          </Box>
                        ) : (
                          option.name
                        )}
                      </li>
                    )}
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        inputRef={vendorInputRef}
                        label="Vendor"
                        error={!!errors.vendor_id}
                        helperText={errors.vendor_id ? 'Required' : ''}
                        InputLabelProps={{ shrink: true, style: { fontSize: 10, textAlign: 'center' } }}
                        inputProps={{
                          ...params.inputProps,
                          style: { fontSize: 12, textAlign: 'center' }
                        }}
                        size="small"
                        sx={{ 
                          '& .MuiInputBase-root': { height: 27 },
                        }}
                      />
                    )}
                    disabled={isViewMode}
                    sx={{ width: '100%' }}
                  />
                  <BalanceDisplay 
                    accountType="vendor"
                    accountId={watch('vendor_id')}
                    disabled={isViewMode}
                  />
                </Grid>
                <Grid size={4}>
                  <TextField
                    fullWidth
                    label="Payment Terms"
                    {...control.register('payment_terms')}
                    disabled={isViewMode}
                    InputLabelProps={{ shrink: true, style: { fontSize: 10, textAlign: 'center' } }}
                    inputProps={{ style: { fontSize: 12, textAlign: 'center' } }}
                    size="small"
                    sx={{ 
                      '& .MuiInputBase-root': { height: 27 },
                      width: '100%' 
                    }}
                  />
                </Grid>

                {/* PDF Upload Section */}
                <Grid size={12} sx={{ mt: 2, mb: 2 }}>
                  <Paper sx={{ p: 2, bgcolor: 'grey.50', border: '1px dashed', borderColor: 'grey.300' }}>
                    <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
                      <Typography variant="subtitle2" color="textSecondary">
                        PDF Invoice Upload (Optional)
                      </Typography>
                      <Tooltip title="Upload PDF invoice to auto-extract item details and populate the form">
                        <Typography variant="caption" color="textSecondary">
                          Auto-Extract Data
                        </Typography>
                      </Tooltip>
                    </Box>
                    
                    {!pdfFile && !pdfUploadLoading && (
                      <Box
                        sx={{
                          border: '2px dashed',
                          borderColor: 'grey.300',
                          borderRadius: 1,
                          p: 3,
                          textAlign: 'center',
                          cursor: 'pointer',
                          '&:hover': {
                            borderColor: 'primary.main',
                            bgcolor: 'action.hover'
                          }
                        }}
                        onClick={triggerFileUpload}
                      >
                        <CloudUpload sx={{ fontSize: 48, color: 'grey.400', mb: 1 }} />
                        <Typography variant="body2" color="textSecondary" gutterBottom>
                          Click to upload PDF invoice (PDF only)
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          Maximum file size: 10MB
                        </Typography>
                      </Box>
                    )}
                    
                    {pdfUploadLoading && (
                      <Box sx={{ p: 3, textAlign: 'center' }}>
                        <CircularProgress size={40} sx={{ mb: 2 }} />
                        <Typography variant="body2" color="textSecondary" gutterBottom>
                          Processing PDF invoice...
                        </Typography>
                        <LinearProgress sx={{ mt: 1 }} />
                      </Box>
                    )}
                    
                    {pdfFile && !pdfUploadLoading && (
                      <Box sx={{ p: 2, bgcolor: 'success.light', borderRadius: 1 }}>
                        <Box display="flex" alignItems="center" justifyContent="space-between">
                          <Box display="flex" alignItems="center" gap={1}>
                            <Description color="primary" />
                            <Typography variant="body2" fontWeight="medium">
                              {pdfFile.name}
                            </Typography>
                            <Chip
                              icon={<CheckCircle />}
                              label="Processed"
                              size="small"
                              color="success"
                              variant="outlined"
                            />
                          </Box>
                          <Button
                            size="small"
                            onClick={removePdfFile}
                            color="error"
                            variant="outlined"
                          >
                            Remove
                          </Button>
                        </Box>
                        {pdfExtractedData && (
                          <Alert severity="success" sx={{ mt: 1 }}>
                            <Typography variant="caption">
                              Extracted {pdfExtractedData.items?.length || 0} items and vendor information
                            </Typography>
                          </Alert>
                        )}
                      </Box>
                    )}
                    
                    {pdfUploadError && (
                      <Alert severity="error" sx={{ mt: 1 }} onClose={() => setPdfUploadError(null)}>
                        {pdfUploadError}
                      </Alert>
                    )}
                    
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept=".pdf"
                      style={{ display: 'none' }}
                      onChange={handleFileInputChange}
                    />
                  </Paper>
                </Grid>

                <Grid size={12} sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-start', height: 27 }}>
                  <Typography variant="h6" sx={{ fontSize: 16, fontWeight: 'bold' }}>Items</Typography>
                </Grid>
                {fields.map((field, index) => (
                  <Grid container spacing={2} key={field.id} sx={{ mb: 2 }}>
                    <Grid size={3}>
                      <Autocomplete
                        options={productOptions}
                        getOptionLabel={(option) => option.product_name || ''}
                        value={productOptions.find((opt: any) => opt.id === watch(`items.${index}.product_id`)) || null}
                        onChange={(_, newValue) => {
                          if (newValue && newValue.id === -1) {
                            if (productInputRefs.current[index]) {
                              productInputRefs.current[index].blur();
                            }
                            setAddingItemIndex(index);
                            handleAddProduct();
                          } else {
                            setValue(`items.${index}.product_id`, newValue ? newValue.id : null);
                            if (newValue) {
                              setValue(`items.${index}.hsn_code`, newValue.hsn_code || '');
                              const price = newValue.unit_price || 0;
                              setValue(`items.${index}.unit_price`, price);
                              setValue(`items.${index}.original_unit_price`, price);
                              setValue(`items.${index}.gst_rate`, newValue.gst_rate || 0);
                              setValue(`items.${index}.unit`, newValue.unit || '');
                            }
                          }
                        }}
                        openOnFocus
                        filterOptions={(options, params) => {
                          const filtered = filter(options, params);
                          if (params.inputValue !== '') {
                            filtered.unshift({ id: -1, product_name: `Add "${params.inputValue}"` });
                          } else {
                            filtered.unshift({ id: -1, product_name: 'Add Product' });
                          }
                          return filtered;
                        }}
                        renderOption={(props, option) => (
                          <li {...props} style={{ fontSize: 12 }}>
                            {option.id === -1 ? (
                              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                <Add sx={{ mr: 1 } } />
                                {option.product_name}
                              </Box>
                            ) : (
                              option.product_name
                            )}
                          </li>
                        )}
                        renderInput={(params) => (
                          <TextField
                            {...params}
                            inputRef={(el) => { productInputRefs.current[index] = el; }}
                            label="Product"
                            error={!!errors.items?.[index]?.product_id}
                            helperText={errors.items?.[index]?.product_id ? 'Product is required' : ''}
                            InputLabelProps={{ shrink: true, style: { fontSize: 10, textAlign: 'center' } }}
                            inputProps={{
                              ...params.inputProps,
                              style: { fontSize: 12, textAlign: 'center' }
                            }}
                            size="small"
                            sx={{ 
                              '& .MuiInputBase-root': { height: 27 },
                            }}
                          />
                        )}
                        disabled={isViewMode}
                        sx={{ width: '100%' }}
                      />
                      <StockDisplay 
                        productId={watch(`items.${index}.product_id`)}
                        disabled={isViewMode}
                      />
                    </Grid>
                    <Grid size={1.5}>
                      <TextField
                        fullWidth
                        label="HSN Code"
                        {...control.register(`items.${index}.hsn_code`)}
                        disabled={isViewMode}
                        InputLabelProps={{ shrink: true, style: { fontSize: 10, textAlign: 'center' } }}
                        inputProps={{ style: { fontSize: 12, textAlign: 'center' } }}
                        size="small"
                        sx={{ 
                          '& .MuiInputBase-root': { height: 27 },
                          width: '100%' 
                        }}
                      />
                    </Grid>
                    <Grid size={1.5}>
                      <TextField
                        fullWidth
                        label="Qty"
                        type="number"
                        {...control.register(`items.${index}.quantity`, { required: true, valueAsNumber: true })}
                        error={!!errors.items?.[index]?.quantity}
                        helperText={errors.items?.[index]?.quantity ? 'Required' : ''}
                        disabled={isViewMode}
                        InputLabelProps={{ shrink: true, style: { fontSize: 10, textAlign: 'center' } }}
                        inputProps={{ style: { fontSize: 12, textAlign: 'center' } }}
                        InputProps={{
                          endAdornment: <InputAdornment position="end" sx={{ fontSize: 10 }}>{watch(`items.${index}.unit`) || ''}</InputAdornment>,
                        }}
                        size="small"
                        sx={{ 
                          '& .MuiInputBase-root': { height: 27 },
                          width: '100%',
                          '& input[type=number]': {
                            MozAppearance: 'textfield',
                          },
                          '& input::-webkit-outer-spin-button, & input::-webkit-inner-spin-button': {
                            display: 'none',
                          },
                        }}
                      />
                    </Grid>
                    <Grid size={1.5}>
                      <TextField
                        fullWidth
                        label="Unit Price"
                        type="number"
                        {...control.register(`items.${index}.unit_price`, { required: true, valueAsNumber: true })}
                        error={!!errors.items?.[index]?.unit_price}
                        helperText={errors.items?.[index]?.unit_price ? 'Required' : ''}
                        disabled={isViewMode}
                        InputLabelProps={{ shrink: true, style: { fontSize: 10, textAlign: 'center' } }}
                        inputProps={{ style: { fontSize: 12, textAlign: 'center' } }}
                        size="small"
                        sx={{ 
                          '& .MuiInputBase-root': { height: 27 },
                          width: '100%',
                          '& input[type=number]': {
                            MozAppearance: 'textfield',
                          },
                          '& input::-webkit-outer-spin-button, & input::-webkit-inner-spin-button': {
                            display: 'none',
                          },
                        }}
                      />
                    </Grid>
                    <Grid size={1.5}>
                      <Autocomplete<number>
                        options={GST_SLABS}
                        value={watch(`items.${index}.gst_rate`)}
                        onChange={(_, newValue) => {
                          setValue(`items.${index}.gst_rate`, newValue ?? 0);
                        }}
                        renderInput={(params) => (
                          <TextField
                            {...params}
                            label="GST %"
                            InputLabelProps={{ shrink: true, style: { fontSize: 10, textAlign: 'center' } }}
                            inputProps={{
                              ...params.inputProps,
                              style: { fontSize: 12, textAlign: 'center' }
                            }}
                            size="small"
                            sx={{ 
                              '& .MuiInputBase-root': { height: 27 },
                            }}
                          />
                        )}
                        disabled={isViewMode}
                        sx={{ width: '100%' }}
                      />
                    </Grid>
                    <Grid size={2}>
                      <TextField
                        fullWidth
                        label="Amount"
                        type="number"
                        value={computedItems[index]?.total_amount || 0}
                        disabled
                        InputLabelProps={{ shrink: true, style: { fontSize: 10, textAlign: 'center' } }}
                        inputProps={{ style: { fontSize: 12, textAlign: 'center' } }}
                        size="small"
                        sx={{ 
                          '& .MuiInputBase-root': { height: 27 },
                          width: '100%' 
                        }}
                      />
                    </Grid>
                    {!isViewMode && (
                      <Grid size={0.5}>
                        <IconButton sx={{ backgroundColor: 'error.main', color: 'white', fontSize: 10 }} onClick={() => remove(index)} disabled={fields.length === 1}>
                          <Remove fontSize="inherit" />
                        </IconButton>
                      </Grid>
                    )}
                  </Grid>
                ))}
                {!isViewMode && (
                  <Box sx={{ mb: 1.0625, mt: 0.5 }}>
                    <IconButton 
                      sx={{ 
                        backgroundColor: 'green', 
                        color: 'white', 
                        borderRadius: '50%',
                        width: 20,
                        height: 20,
                      }} 
                      onClick={() => append({ product_id: null, hsn_code: '', quantity: 0, unit: '', unit_price: 0, original_unit_price: 0, discount_percentage: 0, discount_amount: 0, taxable_amount: 0, gst_rate: 0, cgst_amount: 0, sgst_amount: 0, igst_amount: 0, total_amount: 0 })}
                    >
                      <Add sx={{ fontSize: 12 }} />
                    </IconButton>
                  </Box>
                )}
              </Grid>
              <Grid size={12}>
                <Grid container spacing={0.5}>
                  <Grid size={6}>
                    <Grid container direction="column" spacing={0.625}>
                      <Grid size={12}>
                        <TextField
                          fullWidth
                          label="Total Amt"
                          type="number"
                          value={totalSubtotal}
                          disabled
                          InputLabelProps={{ shrink: true, style: { fontSize: 10, textAlign: 'center' } }}
                          inputProps={{ style: { fontSize: 13.5, fontWeight: 'bold', textAlign: 'center' } }}
                          size="small"
                          sx={{ 
                            '& .MuiInputBase-root': { height: 26.4 },
                            width: '100%' 
                          }}
                        />
                      </Grid>
                      <Grid size={12}>
                        <TextField
                          fullWidth
                          label="GST Amt"
                          type="number"
                          value={totalGst}
                          disabled
                          InputLabelProps={{ shrink: true, style: { fontSize: 10, textAlign: 'center' } }}
                          inputProps={{ style: { fontSize: 13.5, fontWeight: 'bold', textAlign: 'center' } }}
                          size="small"
                          sx={{ 
                            '& .MuiInputBase-root': { height: 26.4 },
                            width: '100%' 
                          }}
                        />
                      </Grid>
                      <Grid size={12}>
                        <TextField
                          fullWidth
                          label="Grand Total"
                          type="number"
                          value={calculatedTotalAmount}
                          disabled
                          InputLabelProps={{ shrink: true, style: { fontSize: 10, textAlign: 'center' } }}
                          inputProps={{ style: { fontSize: 13.5, fontWeight: 'bold', textAlign: 'center' } }}
                          size="small"
                          sx={{ 
                            '& .MuiInputBase-root': { height: 26.4 },
                            width: '100%' 
                          }}
                        />
                      </Grid>
                    </Grid>
                  </Grid>
                  <Grid size={6}>
                    <Grid container direction="column" spacing={1}>
                      <Grid size={12}>
                        <TextField
                          fullWidth
                          label="Amount in Words"
                          value={numberToWords(calculatedTotalAmount || 0)}
                          disabled
                          InputLabelProps={{ shrink: true, style: { fontSize: 10, textAlign: 'center' } }}
                          inputProps={{ style: { fontSize: 13.5, fontWeight: 'bold', textAlign: 'center' } }}
                          size="small"
                          sx={{ 
                            '& .MuiInputBase-root': { height: 52.8 },
                            width: '100%' 
                          }}
                        />
                      </Grid>
                      <Grid size={12}>
                        <TextField
                          fullWidth
                          label="Description"
                          multiline
                          rows={1}
                          {...control.register('notes')}
                          disabled={isViewMode}
                          InputLabelProps={{ shrink: true, style: { fontSize: 10, textAlign: 'center' } }}
                          inputProps={{ style: { fontSize: 13.5, fontWeight: 'bold', textAlign: 'center' } }}
                          size="small"
                          sx={{ 
                            '& .MuiInputBase-root': { height: 26.4 },
                            width: '100%' 
                          }}
                        />
                      </Grid>
                    </Grid>
                  </Grid>
                </Grid>
              </Grid>
              <Box sx={{ mt: 1, display: 'flex', justifyContent: 'center' }}>
                {!isViewMode && (
                  <Button type="submit" variant="contained" color="success" disabled={createMutation.isPending || updateMutation.isPending} sx={{ mr: 1, fontSize: 10 }}>
                    Save
                  </Button>
                )}
                <Button variant="contained" color="error" onClick={() => router.push('/dashboard')} sx={{ mr: 1, fontSize: 10 }}>
                  Cancel
                </Button>
                <Button variant="contained" color="primary" sx={{ fontSize: 10 }}>
                  Manage Column
                </Button>
              </Box>
            </form>
          </Paper>
        </Grid>
      </Grid>
      {/* Add Vendor Modal */}
      <AddVendorModal
        open={showAddVendorModal}
        onClose={() => setShowAddVendorModal(false)}
        onAdd={handleVendorAdd}
        loading={addVendorLoading}
      />
      {/* Add Product Modal */}
      <AddProductModal
        open={showAddProductModal}
        onClose={() => setShowAddProductModal(false)}
        onAdd={handleProductAdd}
        loading={addProductLoading}
      />
      {/* Add Shipping Address Modal */}
      <AddShippingAddressModal
        open={showShippingModal}
        onClose={() => setShowShippingModal(false)}
        onAdd={handleAddShipping}
        loading={addShippingLoading}
      />
      {/* Voucher List Modal */}
      <VoucherListModal
        open={showFullModal}
        onClose={handleModalClose}
        voucherType="Purchase Vouchers"
        vouchers={sortedVouchers || []}
        onVoucherClick={handleVoucherClick}
        onEdit={handleView}
        onView={handleView}
        onDelete={handleDelete}
        onGeneratePDF={handleGeneratePDF}
        vendorList={vendorList}
      />
      
      {contextMenu !== null && (
        <VoucherContextMenu
          voucher={contextMenu.voucher}
          voucherType="Purchase Voucher"
          onView={handleView}
          onEdit={handleEdit}
          onDelete={handleDelete}
          onPrint={() => handleGeneratePDF(contextMenu.voucher)}
          showKebab={false}
          open={true}
          onClose={handleContextMenuClose}
          anchorReference="anchorPosition"
          anchorPosition={{ top: contextMenu.mouseY, left: contextMenu.mouseX }}
        />
      )}
    </Container>
  );
};

export default PurchaseVoucherPage;
