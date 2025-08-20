# Authentication and Company Onboarding Testing Guide

## Overview
This guide validates the refactored authentication and company onboarding flow. The implementation ensures:

1. **Backend**: Canonical auth imports, proper logging, JWT for password reset
2. **Frontend**: 404 vs auth error distinction, company onboarding flow, proper error toasts

## Test Scenarios

### ✅ Scenario 1: New User Login → Password Reset → Onboarding
**Flow**: First-time user login requiring password change, then company setup

**Steps:**
1. Login with new user credentials
2. System detects `must_change_password: true`
3. User redirected to `/password-reset`
4. After password change, new JWT token issued
5. User redirected to `/dashboard` 
6. CompanySetupGuard detects missing company (404 from `/companies/current`)
7. Welcome modal appears: "Welcome! Please complete your company setup to get started."
8. User completes company setup
9. Success toast: "Company details saved successfully!"
10. Normal dashboard access granted

**Expected Behavior:**
- ✅ No logout during company 404 error
- ✅ Fresh JWT token after password reset
- ✅ Automatic onboarding prompt on dashboard
- ✅ Friendly welcome message vs error message

---

### ✅ Scenario 2: Login with Company Missing → Onboarding (Not Logout)
**Flow**: Existing user whose company was deleted/missing

**Steps:**
1. Login with valid credentials
2. User redirected to `/dashboard`
3. API call to `/companies/current` returns 404
4. Frontend intercepts 404 - does NOT trigger logout
5. CompanySetupGuard shows setup modal immediately
6. Toast: "Company setup required to continue"
7. User completes company setup
8. Normal access restored

**Expected Behavior:**
- ✅ 404 on `/companies/current` does NOT clear auth tokens
- ✅ 404 on `/companies/current` does NOT redirect to login
- ✅ Setup modal appears immediately 
- ✅ Informational toast (not error toast)

---

### ✅ Scenario 3: Login with Expired Session → Logout as Normal
**Flow**: User with expired/invalid JWT token

**Steps:**
1. User tries to access protected route with expired token
2. API returns 401 Unauthorized
3. Frontend intercepts 401 and triggers logout
4. Toast: "Session expired. Please login again."
5. Auth data cleared from localStorage
6. User redirected to login page

**Expected Behavior:**
- ✅ 401/403 errors trigger logout flow
- ✅ Clear all auth data (token, user_role, is_super_admin)
- ✅ Redirect to login
- ✅ Appropriate error message

---

### ✅ Scenario 4: Normal Login with Company → Dashboard
**Flow**: Standard login for user with existing company

**Steps:**
1. Login with valid credentials
2. User redirected to `/dashboard`
3. API call to `/companies/current` returns company data
4. CompanySetupGuard allows normal access
5. Dashboard loads normally

**Expected Behavior:**
- ✅ No setup modal appears
- ✅ No error toasts
- ✅ Direct dashboard access
- ✅ Normal application functionality

---

## Technical Validation

### Backend Changes
- ✅ **Canonical Imports**: All endpoints use `from app.core.security import get_current_user`
- ✅ **Logging**: All route files have `logger = logging.getLogger(__name__)`
- ✅ **JWT on Reset**: Password reset endpoint issues fresh token
- ✅ **404 vs Auth**: `/companies/current` returns 404 only for missing company

### Frontend Changes  
- ✅ **Error Distinction**: API interceptor distinguishes 404 vs 401/403
- ✅ **No Logout on 404**: Company missing does not trigger logout
- ✅ **JWT Handling**: Password service stores new tokens
- ✅ **Onboarding Flow**: CompanySetupGuard handles all scenarios
- ✅ **Debug Logging**: Enhanced logging throughout

## Key Files Modified

### Backend
- `app/api/v1/organizations.py` - Fixed imports
- `app/api/v1/bom.py` - Fixed imports, added logging  
- `app/api/v1/manufacturing.py` - Fixed imports, added logging
- `app/api/v1/password.py` - Added JWT token generation on reset

### Frontend
- `frontend/src/lib/api.ts` - Enhanced error handling
- `frontend/src/services/authService.ts` - JWT token handling
- `frontend/src/context/CompanyContext.tsx` - Better error toasts
- `frontend/src/components/CompanySetupGuard.tsx` - Dashboard route, welcome message

## Validation Results
```
📈 OVERALL RESULT: 6/6 checks passed
🎉 ALL CHECKS PASSED! Implementation is ready for testing.
```

All automated validation checks passed successfully!