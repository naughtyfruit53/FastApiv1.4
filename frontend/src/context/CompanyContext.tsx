// frontend/src/context/CompanyContext.tsx

import React, { createContext, useState, useContext, useEffect } from 'react';
import { companyService } from '../services/authService';
import { useAuth } from './AuthContext';

interface CompanyContextType {
  isCompanySetupNeeded: boolean;
  setIsCompanySetupNeeded: React.Dispatch<React.SetStateAction<boolean>>;
  checkCompanyDetails: () => Promise<void>;
}

const CompanyContext = createContext<CompanyContextType | undefined>(undefined);

export const CompanyProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isCompanySetupNeeded, setIsCompanySetupNeeded] = useState(false);
  const { user, loading } = useAuth();

  const checkCompanyDetails = async () => {
    try {
      console.log('[CompanyContext] Checking company details');
      const company = await companyService.getCurrentCompany();
      if (company) {
        setIsCompanySetupNeeded(false);
        console.log('[CompanyContext] Company details found:', company.name);
      } else {
        setIsCompanySetupNeeded(true);
        console.log('[CompanyContext] No company found - setup required');
      }
    } catch (error: any) {
      console.error('[CompanyContext] Company details check error:', error);
      
      // Check if this is a company setup scenario vs other errors
      if (error.status === 404 || error.isCompanySetupRequired) {
        setIsCompanySetupNeeded(true);
        console.log('[CompanyContext] Company setup needed due to 404/missing company');
        
        // Show informational toast for company setup requirement
        import('react-toastify').then(({ toast }) => {
          toast.info('Company setup required to continue', {
            position: "top-right",
            autoClose: 4000,
          });
        });
      } else {
        // For other errors, log but don't assume company setup is needed
        console.error('[CompanyContext] Unexpected error checking company details:', error);
        
        // Show error toast for other issues
        import('react-toastify').then(({ toast }) => {
          toast.error(`Error checking company details: ${error.userMessage || error.message}`, {
            position: "top-right",
            autoClose: 5000,
          });
        });
      }
    }
  };

  useEffect(() => {
    // Only check company details after auth context is fully loaded and user is authenticated
    if (!loading && user && localStorage.getItem('token')) {
      console.log('[CompanyContext] Auth context ready, checking company details');
      checkCompanyDetails();
    }
  }, [loading, user]);

  return (
    <CompanyContext.Provider value={{ isCompanySetupNeeded, setIsCompanySetupNeeded, checkCompanyDetails }}>
      {children}
    </CompanyContext.Provider>
  );
};

export const useCompany = () => {
  const context = useContext(CompanyContext);
  if (undefined === context) {
    throw new Error('useCompany must be used within a CompanyProvider');
  }
  return context;
};