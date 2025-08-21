// frontend/src/components/MegaMenu.tsx

'use client';

import React, { useState, useEffect } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Menu,
  MenuItem,
  Box,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  IconButton,
  Avatar,
  ListItemButton,
  Grid as Grid,
} from '@mui/material';
import {
  Dashboard,
  Receipt,
  Inventory,
  People,
  Business,
  Assessment,
  Settings,
  AccountCircle,
  ExpandMore,
  ShoppingCart,
  LocalShipping,
  AccountBalance,
  SwapHoriz,
  TrendingUp,
  BarChart,
  Security,
  Storage,
  Build,
  ReceiptLong,
  NoteAdd,
  AddBusiness,
  DeveloperMode
} from '@mui/icons-material';
import { useRouter } from 'next/navigation';
import CreateOrganizationLicenseModal from './CreateOrganizationLicenseModal';
import { isAppSuperAdmin, isOrgSuperAdmin, canManageUsers, canShowUserManagementInMegaMenu } from '../types/user.types';
import { useQuery } from '@tanstack/react-query';
import { companyService } from '../services/authService';

interface MegaMenuProps {
  user?: any;
  onLogout: () => void;
  isVisible?: boolean;
}

const MegaMenu: React.FC<MegaMenuProps> = ({ user, onLogout, isVisible = true }) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [userMenuAnchor, setUserMenuAnchor] = useState<null | HTMLElement>(null);
  const [activeMenu, setActiveMenu] = useState<string | null>(null);
  const [createLicenseModalOpen, setCreateLicenseModalOpen] = useState(false);
  const router = useRouter();

  // Query for company data to show logo
  const { data: companyData } = useQuery({
    queryKey: ['company'],
    queryFn: companyService.getCurrentCompany,
    enabled: !isAppSuperAdmin(user), // Only fetch for organization users
    retry: false,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Add keyboard event listener for Escape key
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        if (anchorEl) {
          handleMenuClose();
        }
        if (userMenuAnchor) {
          handleUserMenuClose();
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [anchorEl, userMenuAnchor]);

  // Don't render if not visible
  if (!isVisible) {
    return null;
  }

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>, menuName: string) => {
    setAnchorEl(event.currentTarget);
    setActiveMenu(menuName);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setActiveMenu(null);
  };

  const handleUserMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setUserMenuAnchor(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setUserMenuAnchor(null);
  };

  const navigateTo = (path: string) => {
    router.push(path);
    handleMenuClose();
  };

  const _handleCreateOrgLicense = () => {
    // For now, we'll use a state to control the modal
    // In a full implementation, this would be managed by parent component
    setCreateLicenseModalOpen(true);
    handleMenuClose();
  };

  const handleDemoMode = () => {
    // Navigate to demo page
    router.push('/demo');
    handleMenuClose();
  };

  // Check user roles using proper utility functions
  const isSuperAdmin = isAppSuperAdmin(user);
  const _isOrgAdmin = isOrgSuperAdmin(user);
  const _canManage = canManageUsers(user);
  const _canShowUserMgmtInMenu = canShowUserManagementInMegaMenu(user);

  // Enhanced logo navigation function
  const navigateToHome = () => {
    router.push('/dashboard');
    handleMenuClose();
  };

  const menuItems = {
    vouchers: {
      title: 'Vouchers',
      icon: <Receipt />,
      sections: [
        {
          title: 'Purchase Vouchers',
          items: [
            { name: 'Purchase Order', path: '/vouchers/Purchase-Vouchers/purchase-order', icon: <LocalShipping /> },
            { name: 'GRN (Goods Received Note)', path: '/vouchers/Purchase-Vouchers/grn', icon: <Inventory /> },
            { name: 'Purchase Voucher', path: '/vouchers/Purchase-Vouchers/purchase-voucher', icon: <ShoppingCart /> },
            { name: 'Purchase Return', path: '/vouchers/Purchase-Vouchers/purchase-return', icon: <SwapHoriz /> }
          ]
        },
        {
          title: 'Pre Sales Vouchers',
          items: [
            { name: 'Quotation', path: '/vouchers/Pre-Sales-Voucher/quotation', icon: <NoteAdd /> },
            { name: 'Proforma Invoice', path: '/vouchers/Pre-Sales-Voucher/proforma-invoice', icon: <ReceiptLong /> },
            { name: 'Sales Order', path: '/vouchers/Pre-Sales-Voucher/sales-order', icon: <Assessment /> }
          ]
        },
        {
          title: 'Sales Vouchers',
          items: [
            { name: 'Sales Voucher', path: '/vouchers/Sales-Vouchers/sales-voucher', icon: <TrendingUp /> },
            { name: 'Delivery Challan', path: '/vouchers/Sales-Vouchers/delivery-challan', icon: <LocalShipping /> },
            { name: 'Sales Return', path: '/vouchers/Sales-Vouchers/sales-return', icon: <SwapHoriz /> }
          ]
        },
        {
          title: 'Manufacturing Vouchers',
          items: [
            { name: 'Production Order', path: '/vouchers/Manufacturing-Vouchers/production-order', icon: <Build /> },
            { name: 'Material Requisition', path: '/vouchers/Manufacturing-Vouchers/material-requisition', icon: <Storage /> },
            { name: 'Work Order', path: '/vouchers/Manufacturing-Vouchers/work-order', icon: <Assessment /> },
            { name: 'Finished Goods Receipt', path: '/vouchers/Manufacturing-Vouchers/finished-goods-receipt', icon: <Inventory /> }
          ]
        },
        {
          title: 'Financial Vouchers',
          items: [
            { name: 'Payment Voucher', path: '/vouchers/Financial-Vouchers/payment-voucher', icon: <AccountBalance /> },
            { name: 'Receipt Voucher', path: '/vouchers/Financial-Vouchers/receipt-voucher', icon: <AccountBalance /> },
            { name: 'Journal Voucher', path: '/vouchers/Financial-Vouchers/journal-voucher', icon: <AccountBalance /> },
            { name: 'Contra Voucher', path: '/vouchers/Financial-Vouchers/contra-voucher', icon: <AccountBalance /> },
            { name: 'Credit Note', path: '/vouchers/Financial-Vouchers/credit-note', icon: <AccountBalance /> },
            { name: 'Debit Note', path: '/vouchers/Financial-Vouchers/debit-note', icon: <AccountBalance /> },
            { name: 'Non-Sales Credit Note', path: '/vouchers/Financial-Vouchers/non-sales-credit-note', icon: <AccountBalance /> }
          ]
        },
        {
          title: 'Intern Department Vouchers',
          items: [
            { name: 'Inter Department Voucher', path: '/vouchers/inter-department-voucher', icon: <SwapHoriz /> }
          ]
        }
      ]
    },
    masters: {
      title: 'Master Data',
      icon: <People />,
      sections: [
        {
          title: 'Business Partners',
          items: [
            { name: 'Vendors', path: '/masters/vendors', icon: <People /> },
            { name: 'Customers', path: '/masters/customers', icon: <Business /> },
            { name: 'Employees', path: '/masters?tab=employees', icon: <People /> },
            { name: 'Company Details', path: '/masters?tab=company', icon: <Business /> },
          ]
        },
        {
          title: 'Inventory',
          items: [
            { name: 'Products', path: '/masters/products', icon: <Inventory /> },
            { name: 'Categories', path: '/masters?tab=categories', icon: <Storage /> },
            { name: 'Units', path: '/masters?tab=units', icon: <Storage /> },
            { name: 'Bill of Materials (BOM)', path: '/masters?tab=bom', icon: <Build /> }
          ]
        },
        {
          title: 'Financial',
          items: [
            { name: 'Chart of Accounts', path: '/masters?tab=accounts', icon: <AccountBalance /> },
            { name: 'Tax Codes', path: '/masters?tab=tax-codes', icon: <Assessment /> },
            { name: 'Payment Terms', path: '/masters?tab=payment-terms', icon: <Business /> }
          ]
        }
      ]
    },
    inventory: {
      title: 'Inventory',
      icon: <Inventory />,
      sections: [
        {
          title: 'Stock Management',
          items: [
            { name: 'Current Stock', path: '/inventory/stock', icon: <Inventory /> },
            { name: 'Stock Movements', path: '/inventory/movements', icon: <SwapHoriz /> },
            { name: 'Low Stock Report', path: '/inventory/low-stock', icon: <TrendingUp /> }
          ]
        },
        {
          title: 'Warehouse',
          items: [
            { name: 'Locations', path: '/inventory/locations', icon: <Storage /> },
            { name: 'Bin Management', path: '/inventory/bins', icon: <Storage /> },
            { name: 'Cycle Count', path: '/inventory/cycle-count', icon: <Assessment /> }
          ]
        }
      ]
    },
    reports: {
      title: 'Reports',
      icon: <Assessment />,
      sections: [
        {
          title: 'Financial Reports',
          items: [
            { name: 'Ledgers', path: '/reports/ledgers', icon: <AccountBalance /> },
            { name: 'Trial Balance', path: '/reports/trial-balance', icon: <BarChart /> },
            { name: 'Profit & Loss', path: '/reports/profit-loss', icon: <TrendingUp /> },
            { name: 'Balance Sheet', path: '/reports/balance-sheet', icon: <Assessment /> }
          ]
        },
        {
          title: 'Inventory Reports',
          items: [
            { name: 'Stock Report', path: '/reports/stock', icon: <Inventory /> },
            { name: 'Valuation Report', path: '/reports/valuation', icon: <BarChart /> },
            { name: 'Movement Report', path: '/reports/movements', icon: <SwapHoriz /> }
          ]
        },
        {
          title: 'Business Reports',
          items: [
            { name: 'Sales Analysis', path: '/reports/sales-analysis', icon: <TrendingUp /> },
            { name: 'Purchase Analysis', path: '/reports/purchase-analysis', icon: <ShoppingCart /> },
            { name: 'Vendor Analysis', path: '/reports/vendor-analysis', icon: <People /> }
          ]
        }
      ]
    }
  };

  const renderMegaMenu = () => {
    if (!activeMenu || !menuItems[activeMenu as keyof typeof menuItems]) return null;

    const menu = menuItems[activeMenu as keyof typeof menuItems];

    return (
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
        PaperProps={{
          sx: {
            width: 800,
            maxHeight: 500,
            mt: 1
          }
        }}
        MenuListProps={{
          sx: { p: 2 }
        }}
      >
        <Typography variant="h6" sx={{ mb: 2, color: 'primary.main' }}>
          {menu.title}
        </Typography>
        <Grid container spacing={2}>
          {menu.sections.map((section, index) => (
            <Grid
              key={index}
              size={{
                xs: 12,
                sm: 6,
                md: 3
              }}>
              <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 'bold', color: 'text.secondary' }}>
                {section.title}
              </Typography>
              <List dense>
                {section.items.map((item, itemIndex) => (
                  <ListItemButton
                    key={itemIndex}
                    onClick={() => navigateTo(item.path)}
                    sx={{
                      borderRadius: 1,
                      mb: 0.5,
                      '&:hover': {
                        backgroundColor: 'primary.light',
                        color: 'primary.contrastText'
                      }
                    }}
                  >
                    <ListItemIcon sx={{ minWidth: 36 }}>
                      {item.icon}
                    </ListItemIcon>
                    <ListItemText primary={item.name} />
                  </ListItemButton>
                ))}
              </List>
              {index < menu.sections.length - 1 && <Divider sx={{ mt: 1 }} />}
            </Grid>
          ))}
        </Grid>
      </Menu>
    );
  };

  return (
    <>
      <AppBar position="static">
        <Toolbar>
          {/* Enhanced Logo Section */}
          <Box 
            sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              cursor: 'pointer',
              mr: 3,
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                borderRadius: 1
              },
              p: 1,
              borderRadius: 1,
              transition: 'background-color 0.2s'
            }}
            onClick={navigateToHome}
          >
            <Avatar 
              src={companyData?.logo_path ? companyService.getLogoUrl(companyData.id) : undefined}
              sx={{ 
                bgcolor: 'white', 
                color: 'primary.main', 
                mr: 1,
                width: 40,
                height: 40
              }}
            >
              {!companyData?.logo_path && <Dashboard />}
            </Avatar>
            <Typography variant="h6" component="div" sx={{ fontWeight: 'bold' }}>
              {companyData?.name || 'TRITIQ ERP'}
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
            {/* Different menu structures based on user type */}
            {isSuperAdmin ? (
              <>
                {/* App Super Admins: Only Demo, License Management, Settings */}
                <Button
                  color="inherit"
                  startIcon={<DeveloperMode />}
                  onClick={handleDemoMode}
                  sx={{ mx: 1 }}
                >
                  Demo
                </Button>
                <Button
                  color="inherit"
                  startIcon={<Security />}
                  onClick={() => router.push('/admin/license-management')}
                  sx={{ mx: 1 }}
                >
                  License Management
                </Button>
                <Button
                  color="inherit"
                  startIcon={<Settings />}
                  onClick={() => router.push('/settings')}
                  sx={{ mx: 1 }}
                >
                  Settings
                </Button>
              </>
            ) : (
              <>
                {/* Organization users: Full menu access for business operations */}
                {['masters', 'inventory', 'vouchers', 'reports'].map((key) => {
                  const menu = menuItems[key as keyof typeof menuItems];
                  return (
                    <Button
                      key={key}
                      color="inherit"
                      startIcon={menu.icon}
                      endIcon={<ExpandMore />}
                      onClick={(e) => handleMenuClick(e, key)}
                      sx={{ mx: 1 }}
                    >
                      {menu.title}
                    </Button>
                  );
                })}

                <Button
                  color="inherit"
                  startIcon={<Settings />}
                  onClick={() => router.push('/settings')}
                  sx={{ mx: 1 }}
                >
                  Settings
                </Button>
              </>
            )}
          </Box>

          <IconButton
            color="inherit"
            onClick={handleUserMenuClick}
            sx={{ ml: 2 }}
          >
            <AccountCircle />
          </IconButton>
        </Toolbar>
      </AppBar>

      {renderMegaMenu()}

      <Menu
        anchorEl={userMenuAnchor}
        open={Boolean(userMenuAnchor)}
        onClose={handleUserMenuClose}
      >
        <MenuItem onClick={handleUserMenuClose}>
          <Typography variant="body2">
            {user?.full_name || user?.email || 'User'}
          </Typography>
        </MenuItem>
        <MenuItem onClick={handleUserMenuClose}>
          <Typography variant="body2" color="textSecondary">
            Role: {user?.role || 'Standard User'}
          </Typography>
        </MenuItem>
        <Divider />
        <MenuItem onClick={() => router.push('/profile')}>
          Profile Settings
        </MenuItem>
        <MenuItem onClick={onLogout}>
          Logout
        </MenuItem>
      </Menu>

      {/* Organization License Creation Modal */}
      <CreateOrganizationLicenseModal
        open={createLicenseModalOpen}
        onClose={() => setCreateLicenseModalOpen(false)}
        onSuccess={(result) => {
          console.log('License created:', result);
          // You might want to show a success notification here
        }}
      />
    </>
  );
};

export default MegaMenu;