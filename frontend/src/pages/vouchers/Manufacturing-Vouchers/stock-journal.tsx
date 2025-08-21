import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { useForm, useFieldArray } from 'react-hook-form';
import { 
  Box, 
  Button, 
  TextField, 
  Typography, 
  Grid, 
  IconButton, 
  Alert, 
  CircularProgress, 
  Container, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow, 
  Paper, 
  Autocomplete, 
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Card,
  CardContent,
  Checkbox,
  FormControlLabel
} from '@mui/material';
import { 
  Add, 
  Remove,
  Visibility, 
  Edit, 
  Delete, 
  Save,
  Cancel
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../../../lib/api';
import { getProducts } from '../../../services/masterService';
import VoucherContextMenu from '../../../components/VoucherContextMenu';
import VoucherHeaderActions from '../../../components/VoucherHeaderActions';

interface StockJournalEntry {
  product_id: number;
  debit_quantity: number;
  credit_quantity: number;
  unit: string;
  unit_rate: number;
  debit_value: number;
  credit_value: number;
  from_location?: string;
  to_location?: string;
  from_warehouse?: string;
  to_warehouse?: string;
  from_bin?: string;
  to_bin?: string;
  batch_number?: string;
  lot_number?: string;
  expiry_date?: string;
  transformation_type?: string;
}

interface StockJournal {
  id?: number;
  voucher_number: string;
  date: string;
  journal_type: string;
  from_location?: string;
  to_location?: string;
  from_warehouse?: string;
  to_warehouse?: string;
  manufacturing_order_id?: number;
  bom_id?: number;
  transfer_reason?: string;
  assembly_product_id?: number;
  assembly_quantity?: number;
  physical_verification_done: boolean;
  verified_by?: string;
  verification_date?: string;
  notes?: string;
  status: string;
  total_amount: number;
  entries: StockJournalEntry[];
}

const defaultValues: Partial<StockJournal> = {
  voucher_number: '',
  date: new Date().toISOString().split('T')[0],
  journal_type: 'transfer',
  physical_verification_done: false,
  status: 'draft',
  total_amount: 0,
  entries: []
};

const journalTypeOptions = [
  { value: 'transfer', label: 'Stock Transfer' },
  { value: 'assembly', label: 'Assembly' },
  { value: 'disassembly', label: 'Disassembly' },
  { value: 'adjustment', label: 'Stock Adjustment' },
  { value: 'manufacturing', label: 'Manufacturing' }
];

const transformationTypeOptions = [
  { value: 'consume', label: 'Consume' },
  { value: 'produce', label: 'Produce' },
  { value: 'byproduct', label: 'Byproduct' },
  { value: 'scrap', label: 'Scrap' }
];

export default function StockJournal() {
  const router = useRouter();
  const [mode, setMode] = useState<'create' | 'edit' | 'view'>('create');
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const queryClient = useQueryClient();

  const { control, handleSubmit, watch, setValue, reset, formState: { errors } } = useForm<StockJournal>({
    defaultValues
  });

  const {
    fields: entryFields,
    append: appendEntry,
    remove: removeEntry
  } = useFieldArray({
    control,
    name: 'entries'
  });

  // Fetch stock journals list
  const { data: journalList, isLoading } = useQuery({
    queryKey: ['stock-journals'],
    queryFn: () => api.get('/stock-journals').then(res => res.data),
  });

  // Fetch manufacturing orders
  const { data: manufacturingOrders } = useQuery({
    queryKey: ['manufacturing-orders'],
    queryFn: () => api.get('/manufacturing-orders').then(res => res.data),
  });

  // Fetch BOMs
  const { data: bomList } = useQuery({
    queryKey: ['boms'],
    queryFn: () => api.get('/boms').then(res => res.data),
  });

  // Fetch products
  const { data: productList } = useQuery({
    queryKey: ['products'],
    queryFn: getProducts
  });

  // Fetch specific journal
  const { data: journalData, isFetching } = useQuery({
    queryKey: ['stock-journal', selectedId],
    queryFn: () => api.get(`/stock-journals/${selectedId}`).then(res => res.data),
    enabled: !!selectedId
  });

  // Fetch next voucher number
  const { data: nextVoucherNumber, refetch: refetchNextNumber } = useQuery({
    queryKey: ['nextStockJournalNumber'],
    queryFn: () => api.get('/stock-journals/next-number').then(res => res.data),
    enabled: mode === 'create',
  });

  const sortedJournals = journalList ? [...journalList].sort((a, b) => 
    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  ) : [];

  const latestJournals = sortedJournals.slice(0, 10);
  const productOptions = productList || [];
  const manufacturingOrderOptions = manufacturingOrders || [];
  const bomOptions = bomList || [];

  useEffect(() => {
    if (mode === 'create' && nextVoucherNumber) {
      setValue('voucher_number', nextVoucherNumber);
    } else if (journalData) {
      reset(journalData);
    } else if (mode === 'create') {
      reset(defaultValues);
    }
  }, [journalData, mode, reset, nextVoucherNumber, setValue]);

  // Calculate totals
  useEffect(() => {
    const entries = watch('entries') || [];
    const total = entries.reduce((sum, entry) => 
      sum + (entry.debit_value || 0) - (entry.credit_value || 0), 0);
    setValue('total_amount', total);
  }, [watch('entries'), setValue]);

  // Mutations
  const createMutation = useMutation({
    mutationFn: (data: StockJournal) => api.post('/stock-journals', data),
    onSuccess: async () => {
      queryClient.invalidateQueries({ queryKey: ['stock-journals'] });
      setMode('create');
      setSelectedId(null);
      reset(defaultValues);
      const { data: newNextNumber } = await refetchNextNumber();
      setValue('voucher_number', newNextNumber);
    },
    onError: (error: any) => {
      console.error('Error creating stock journal:', error);
    }
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: StockJournal }) => 
      api.put(`/stock-journals/${id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['stock-journals'] });
      setMode('create');
      setSelectedId(null);
      reset(defaultValues);
    },
    onError: (error: any) => {
      console.error('Error updating stock journal:', error);
    }
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.delete(`/stock-journals/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['stock-journals'] });
      if (selectedId) {
        setSelectedId(null);
        setMode('create');
        reset(defaultValues);
      }
    }
  });

  const onSubmit = (data: StockJournal) => {
    if (mode === 'edit' && selectedId) {
      updateMutation.mutate({ id: selectedId, data });
    } else {
      createMutation.mutate(data);
    }
  };

  const handleEdit = (journal: StockJournal) => {
    setSelectedId(journal.id!);
    setMode('edit');
  };

  const handleView = (journal: StockJournal) => {
    setSelectedId(journal.id!);
    setMode('view');
  };

  const handleDelete = (journalId: number) => {
    if (window.confirm('Are you sure you want to delete this journal?')) {
      deleteMutation.mutate(journalId);
    }
  };

  const handleCancel = () => {
    setMode('create');
    setSelectedId(null);
    reset(defaultValues);
  };

  const addEntry = () => {
    appendEntry({
      product_id: 0,
      debit_quantity: 0,
      credit_quantity: 0,
      unit: '',
      unit_rate: 0,
      debit_value: 0,
      credit_value: 0
    });
  };

  const updateEntryValues = (index: number) => {
    const entries = watch('entries');
    const entry = entries[index];
    if (entry) {
      const debitValue = entry.debit_quantity * entry.unit_rate;
      const creditValue = entry.credit_quantity * entry.unit_rate;
      setValue(`entries.${index}.debit_value`, debitValue);
      setValue(`entries.${index}.credit_value`, creditValue);
    }
  };

  const getJournalTypeIcon = (type: string) => {
    const colors = {
      transfer: 'primary',
      assembly: 'success',
      disassembly: 'warning',
      adjustment: 'info',
      manufacturing: 'secondary'
    };
    return colors[type] || 'default';
  };

  if (isLoading) {
    return (
      <Container>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl">
      <Typography variant="h4" component="h1" gutterBottom>
        Stock Journals
      </Typography>

      <Grid container spacing={3}>
        {/* Journal List - Left Side */}
        <Grid size={12} md={5}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="between" alignItems="center" mb={2}>
                <Typography variant="h6">Recent Journals</Typography>
                <VoucherHeaderActions 
                  onRefresh={() => queryClient.invalidateQueries({ queryKey: ['stock-journals'] })}
                />
              </Box>
              
              <TableContainer component={Paper}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Voucher No.</TableCell>
                      <TableCell>Date</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Amount</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell align="center">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {latestJournals.map((journal, index) => (
                      <TableRow key={journal.id}>
                        <TableCell>{journal.voucher_number}</TableCell>
                        <TableCell>{new Date(journal.date).toLocaleDateString()}</TableCell>
                        <TableCell>
                          <Chip 
                            label={journal.journal_type} 
                            size="small"
                            color={getJournalTypeIcon(journal.journal_type)}
                          />
                        </TableCell>
                        <TableCell>₹{journal.total_amount?.toFixed(2)}</TableCell>
                        <TableCell>
                          <Chip 
                            label={journal.status} 
                            color={journal.status === 'approved' ? 'success' : 'default'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell align="center">
                          <VoucherContextMenu
                            voucher={journal}
                            voucherType="Stock Journal"
                            onView={() => handleView(journal)}
                            onEdit={() => handleEdit(journal)}
                            onDelete={() => handleDelete(journal.id!)}
                            canEdit={journal.status !== 'approved'}
                            canDelete={journal.status !== 'approved'}
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Journal Form - Right Side */}
        <Grid size={12} md={7}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="between" alignItems="center" mb={2}>
                <Typography variant="h6">
                  {mode === 'create' && 'Create Stock Journal'}
                  {mode === 'edit' && 'Edit Stock Journal'}
                  {mode === 'view' && 'View Stock Journal'}
                </Typography>
                {mode !== 'create' && (
                  <Button 
                    variant="outlined" 
                    onClick={handleCancel}
                    startIcon={<Cancel />}
                  >
                    Cancel
                  </Button>
                )}
              </Box>

              <form onSubmit={handleSubmit(onSubmit)}>
                {/* Basic Details */}
                <Grid container spacing={2} mb={3}>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <TextField
                      label="Voucher Number"
                      {...control.register('voucher_number')}
                      fullWidth
                      disabled
                      value={watch('voucher_number')}
                    />
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <TextField
                      label="Date"
                      type="date"
                      {...control.register('date')}
                      fullWidth
                      InputLabelProps={{ shrink: true }}
                      disabled={mode === 'view'}
                    />
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <FormControl fullWidth>
                      <InputLabel>Journal Type</InputLabel>
                      <Select
                        value={watch('journal_type')}
                        onChange={(e) => setValue('journal_type', e.target.value)}
                        disabled={mode === 'view'}
                      >
                        {journalTypeOptions.map((option) => (
                          <MenuItem key={option.value} value={option.value}>
                            {option.label}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <TextField
                      label="Transfer Reason"
                      {...control.register('transfer_reason')}
                      fullWidth
                      disabled={mode === 'view'}
                    />
                  </Grid>
                </Grid>

                {/* Location Details */}
                <Typography variant="h6" gutterBottom>Location Details</Typography>
                <Grid container spacing={2} mb={3}>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <TextField
                      label="From Location"
                      {...control.register('from_location')}
                      fullWidth
                      disabled={mode === 'view'}
                    />
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <TextField
                      label="To Location"
                      {...control.register('to_location')}
                      fullWidth
                      disabled={mode === 'view'}
                    />
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <TextField
                      label="From Warehouse"
                      {...control.register('from_warehouse')}
                      fullWidth
                      disabled={mode === 'view'}
                    />
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <TextField
                      label="To Warehouse"
                      {...control.register('to_warehouse')}
                      fullWidth
                      disabled={mode === 'view'}
                    />
                  </Grid>
                </Grid>

                {/* Manufacturing Details - Show for manufacturing type */}
                {watch('journal_type') === 'manufacturing' && (
                  <>
                    <Typography variant="h6" gutterBottom>Manufacturing Details</Typography>
                    <Grid container spacing={2} mb={3}>
                      <Grid size={{ xs: 12, sm: 6 }}>
                        <Autocomplete
                          options={manufacturingOrderOptions}
                          getOptionLabel={(option) => option.voucher_number || ''}
                          value={manufacturingOrderOptions.find(mo => mo.id === watch('manufacturing_order_id')) || null}
                          onChange={(_, newValue) => setValue('manufacturing_order_id', newValue?.id || undefined)}
                          renderInput={(params) => (
                            <TextField {...params} label="Manufacturing Order" />
                          )}
                          disabled={mode === 'view'}
                        />
                      </Grid>
                      <Grid size={{ xs: 12, sm: 6 }}>
                        <Autocomplete
                          options={bomOptions}
                          getOptionLabel={(option) => option.bom_name || ''}
                          value={bomOptions.find(bom => bom.id === watch('bom_id')) || null}
                          onChange={(_, newValue) => setValue('bom_id', newValue?.id || undefined)}
                          renderInput={(params) => (
                            <TextField {...params} label="BOM" />
                          )}
                          disabled={mode === 'view'}
                        />
                      </Grid>
                    </Grid>
                  </>
                )}

                {/* Assembly Details - Show for assembly/disassembly */}
                {(watch('journal_type') === 'assembly' || watch('journal_type') === 'disassembly') && (
                  <>
                    <Typography variant="h6" gutterBottom>Assembly Details</Typography>
                    <Grid container spacing={2} mb={3}>
                      <Grid size={{ xs: 12, sm: 6 }}>
                        <Autocomplete
                          options={productOptions}
                          getOptionLabel={(option) => option.name || ''}
                          value={productOptions.find(p => p.id === watch('assembly_product_id')) || null}
                          onChange={(_, newValue) => setValue('assembly_product_id', newValue?.id || undefined)}
                          renderInput={(params) => (
                            <TextField {...params} label="Assembly Product" />
                          )}
                          disabled={mode === 'view'}
                        />
                      </Grid>
                      <Grid size={{ xs: 12, sm: 6 }}>
                        <TextField
                          label="Assembly Quantity"
                          type="number"
                          {...control.register('assembly_quantity', { valueAsNumber: true })}
                          fullWidth
                          disabled={mode === 'view'}
                        />
                      </Grid>
                    </Grid>
                  </>
                )}

                {/* Verification Details */}
                <Typography variant="h6" gutterBottom>Physical Verification</Typography>
                <Grid container spacing={2} mb={3}>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={watch('physical_verification_done')}
                          onChange={(e) => setValue('physical_verification_done', e.target.checked)}
                          disabled={mode === 'view'}
                        />
                      }
                      label="Physical Verification Done"
                    />
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <TextField
                      label="Verified By"
                      {...control.register('verified_by')}
                      fullWidth
                      disabled={mode === 'view'}
                    />
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <TextField
                      label="Verification Date"
                      type="datetime-local"
                      {...control.register('verification_date')}
                      fullWidth
                      InputLabelProps={{ shrink: true }}
                      disabled={mode === 'view'}
                    />
                  </Grid>
                </Grid>

                {/* Journal Entries */}
                <Typography variant="h6" gutterBottom>Journal Entries</Typography>
                {mode !== 'view' && (
                  <Box mb={2}>
                    <Button
                      variant="outlined"
                      onClick={addEntry}
                      startIcon={<Add />}
                    >
                      Add Entry
                    </Button>
                  </Box>
                )}

                <TableContainer component={Paper} sx={{ mb: 3 }}>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Product</TableCell>
                        <TableCell>Debit Qty</TableCell>
                        <TableCell>Credit Qty</TableCell>
                        <TableCell>Unit</TableCell>
                        <TableCell>Rate</TableCell>
                        <TableCell>Debit Value</TableCell>
                        <TableCell>Credit Value</TableCell>
                        <TableCell>From Loc</TableCell>
                        <TableCell>To Loc</TableCell>
                        <TableCell>Batch</TableCell>
                        {watch('journal_type') === 'manufacturing' && <TableCell>Type</TableCell>}
                        {mode !== 'view' && <TableCell>Actions</TableCell>}
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {entryFields.map((field, index) => (
                        <TableRow key={field.id}>
                          <TableCell>
                            <Autocomplete
                              options={productOptions}
                              getOptionLabel={(option) => option.name || ''}
                              value={productOptions.find(p => p.id === watch(`entries.${index}.product_id`)) || null}
                              onChange={(_, newValue) => {
                                setValue(`entries.${index}.product_id`, newValue?.id || 0);
                                setValue(`entries.${index}.unit`, newValue?.unit || '');
                                setValue(`entries.${index}.unit_rate`, newValue?.price || 0);
                                updateEntryValues(index);
                              }}
                              renderInput={(params) => (
                                <TextField {...params} size="small" />
                              )}
                              disabled={mode === 'view'}
                              sx={{ minWidth: 150 }}
                            />
                          </TableCell>
                          <TableCell>
                            <TextField
                              type="number"
                              size="small"
                              value={watch(`entries.${index}.debit_quantity`)}
                              onChange={(e) => {
                                setValue(`entries.${index}.debit_quantity`, parseFloat(e.target.value) || 0);
                                updateEntryValues(index);
                              }}
                              disabled={mode === 'view'}
                              sx={{ width: 80 }}
                            />
                          </TableCell>
                          <TableCell>
                            <TextField
                              type="number"
                              size="small"
                              value={watch(`entries.${index}.credit_quantity`)}
                              onChange={(e) => {
                                setValue(`entries.${index}.credit_quantity`, parseFloat(e.target.value) || 0);
                                updateEntryValues(index);
                              }}
                              disabled={mode === 'view'}
                              sx={{ width: 80 }}
                            />
                          </TableCell>
                          <TableCell>
                            <TextField
                              size="small"
                              value={watch(`entries.${index}.unit`)}
                              onChange={(e) => setValue(`entries.${index}.unit`, e.target.value)}
                              disabled={mode === 'view'}
                              sx={{ width: 70 }}
                            />
                          </TableCell>
                          <TableCell>
                            <TextField
                              type="number"
                              size="small"
                              value={watch(`entries.${index}.unit_rate`)}
                              onChange={(e) => {
                                setValue(`entries.${index}.unit_rate`, parseFloat(e.target.value) || 0);
                                updateEntryValues(index);
                              }}
                              disabled={mode === 'view'}
                              sx={{ width: 80 }}
                            />
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              ₹{(watch(`entries.${index}.debit_value`) || 0).toFixed(2)}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              ₹{(watch(`entries.${index}.credit_value`) || 0).toFixed(2)}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <TextField
                              size="small"
                              value={watch(`entries.${index}.from_location`)}
                              onChange={(e) => setValue(`entries.${index}.from_location`, e.target.value)}
                              disabled={mode === 'view'}
                              sx={{ width: 100 }}
                            />
                          </TableCell>
                          <TableCell>
                            <TextField
                              size="small"
                              value={watch(`entries.${index}.to_location`)}
                              onChange={(e) => setValue(`entries.${index}.to_location`, e.target.value)}
                              disabled={mode === 'view'}
                              sx={{ width: 100 }}
                            />
                          </TableCell>
                          <TableCell>
                            <TextField
                              size="small"
                              value={watch(`entries.${index}.batch_number`)}
                              onChange={(e) => setValue(`entries.${index}.batch_number`, e.target.value)}
                              disabled={mode === 'view'}
                              sx={{ width: 100 }}
                            />
                          </TableCell>
                          {watch('journal_type') === 'manufacturing' && (
                            <TableCell>
                              <Select
                                size="small"
                                value={watch(`entries.${index}.transformation_type`) || ''}
                                onChange={(e) => setValue(`entries.${index}.transformation_type`, e.target.value)}
                                disabled={mode === 'view'}
                                sx={{ width: 100 }}
                              >
                                {transformationTypeOptions.map((option) => (
                                  <MenuItem key={option.value} value={option.value}>
                                    {option.label}
                                  </MenuItem>
                                ))}
                              </Select>
                            </TableCell>
                          )}
                          {mode !== 'view' && (
                            <TableCell>
                              <IconButton
                                onClick={() => removeEntry(index)}
                                size="small"
                                color="error"
                              >
                                <Remove />
                              </IconButton>
                            </TableCell>
                          )}
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>

                {/* Notes */}
                <Grid container spacing={2} mb={3}>
                  <Grid size={12}>
                    <TextField
                      label="Notes"
                      {...control.register('notes')}
                      fullWidth
                      multiline
                      rows={3}
                      disabled={mode === 'view'}
                    />
                  </Grid>
                </Grid>

                {/* Total Amount */}
                <Box display="flex" justifyContent="flex-end" mb={3}>
                  <Typography variant="h6">
                    Net Value: ₹{(watch('total_amount') || 0).toFixed(2)}
                  </Typography>
                </Box>

                {/* Action Buttons */}
                {mode !== 'view' && (
                  <Box mt={3} display="flex" gap={2}>
                    <Button
                      type="submit"
                      variant="contained"
                      color="primary"
                      disabled={createMutation.isPending || updateMutation.isPending}
                      startIcon={<Save />}
                    >
                      {mode === 'edit' ? 'Update' : 'Create'} Journal
                    </Button>
                    <Button
                      variant="outlined"
                      onClick={handleCancel}
                      startIcon={<Cancel />}
                    >
                      Cancel
                    </Button>
                  </Box>
                )}
              </form>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
}