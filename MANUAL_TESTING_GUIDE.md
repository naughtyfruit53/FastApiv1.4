# Manual Testing Guide for Session Continuity Fixes

## Pre-Testing Setup

1. **Open Browser Developer Tools**
   - Press F12 or right-click → Inspect Element
   - Go to Console tab
   - Clear existing logs

2. **Enable Verbose Logging**
   - All debug logs are enabled by default
   - Look for logs starting with [AuthContext], [API], [Dashboard], etc.

## Test Scenario 1: App Super Admin License Creation

### Objective: Verify super admin session is preserved during license creation

### Steps:
1. **Login as App Super Admin**
   - Use credentials for app super admin account
   - Watch console for login flow logs:
     ```
     [AuthService] Starting login process for: admin@example.com
     [AuthService] Login API response received: {hasToken: true, ...}
     [AuthContext] Login complete - user context established
     ```

2. **Navigate to License Management**
   - Go to dashboard
   - Look for dashboard logs:
     ```
     [Dashboard] Component mounted, checking auth state
     [Dashboard] Auth context ready - determining dashboard type
     [Dashboard] Rendering App Super Admin Dashboard
     ```

3. **Create Organization License**
   - Click "Create Organization License" or similar
   - Fill out the form with test data
   - Watch console for license creation logs:
     ```
     [LicenseModal] Starting license creation process
     [LicenseModal] Current auth state before license creation: {...}
     ```

4. **Submit License Creation**
   - Click "Create License"
   - Watch for session preservation logs:
     ```
     [LicenseModal] License creation successful: {...}
     [LicenseModal] Verifying session after license creation: {...}
     [LicenseModal] License creation complete - current user session preserved
     ```

5. **Verify Session Preservation**
   - ✅ User should remain logged in
   - ✅ Success message should appear
   - ✅ No redirect to login page
   - ✅ Console shows session preservation logs

### Expected Results:
- App super admin remains logged in
- License creation succeeds without logout
- Console shows detailed session preservation logging

## Test Scenario 2: Org Super Admin First Login

### Objective: Verify org admin doesn't get logout loop after first login

### Prerequisites:
- Create an org admin account with must_change_password=true
- Or use existing org admin credentials

### Steps:
1. **Login with Org Admin Credentials**
   - Use org admin email/password
   - Watch console for enhanced login flow:
     ```
     [AuthService] Starting email login process for: orgadmin@company.com
     [AuthService] Email login API response received: {...}
     [AuthService] Stored organization_id: 123
     [AuthService] Email login complete - all context established
     ```

2. **Password Change (if required)**
   - If must_change_password=true, user will be redirected to password reset
   - Complete password change
   - Watch for password change completion logs

3. **Dashboard Access**
   - After login/password change, user should reach dashboard
   - Watch for dashboard protection logs:
     ```
     [Dashboard] Component mounted, checking auth state: {hasUser: true, loading: false}
     [Dashboard] Auth context ready - determining dashboard type
     [Dashboard] Rendering Organization Dashboard
     ```

4. **Verify No Logout Loops**
   - ✅ Dashboard should load successfully
   - ✅ No automatic redirects to login
   - ✅ User context should be complete
   - ✅ Organization-specific data should load

### Expected Results:
- Org admin successfully reaches dashboard
- No logout loops or session issues
- Console shows complete auth context establishment

## Test Scenario 3: API Error Handling

### Objective: Verify enhanced error handling and debugging

### Steps:
1. **Trigger 401 Error**
   - Manually clear localStorage token: `localStorage.removeItem('token')`
   - Try to access protected resource
   - Watch console for enhanced error handling:
     ```
     [API] Error GET /users/me - status: 401
     [API] 401 Unauthorized - clearing auth data and redirecting
     [API] 401 Error reason: Token expired or invalid
     ```

2. **Trigger Organization Context Error**
   - Login as org admin
   - Try to access endpoint requiring org context
   - Watch for organization validation logs:
     ```
     [ensure_organization_context] Checking context for user 123
     [ensure_organization_context] Organization context established: org_id=42
     ```

3. **Network Error Simulation**
   - Disable network in dev tools (Network tab → Offline)
   - Try to make API call
   - Re-enable network
   - Verify error handling and recovery

### Expected Results:
- Clear error messages with specific context
- Proper cleanup on auth failures
- Detailed logging for troubleshooting

## Test Scenario 4: Session State Verification

### Objective: Verify localStorage and auth context consistency

### Steps:
1. **Check Initial Auth State**
   - Login successfully
   - Open browser console
   - Run: `console.log('Token:', !!localStorage.getItem('token'))`
   - Run: `console.log('Org ID:', localStorage.getItem('organization_id'))`
   - Run: `console.log('User Role:', localStorage.getItem('user_role'))`

2. **Verify Context Consistency**
   - Navigate between different pages
   - Refresh the page
   - Watch for auth context restoration:
     ```
     [AuthContext] Initial auth check on mount
     [AuthContext] Token found, fetching user data
     [AuthContext] User state updated successfully
     ```

3. **Test Logout Process**
   - Click logout button
   - Watch for cleanup logs:
     ```
     [AuthContext] Logout called - clearing all auth data
     ```
   - Verify all localStorage items are cleared

### Expected Results:
- Consistent auth state across page reloads
- Proper localStorage management
- Clean logout process

## Debugging Checklist

When investigating session issues, check console for:

### ✅ **Login Flow Logs**
- `[AuthService] Starting login process`
- `[AuthService] Login API response received`
- `[AuthService] All context established`

### ✅ **Auth Context Logs**
- `[AuthContext] Starting fetchUser`
- `[AuthContext] User data received from API`
- `[AuthContext] User state updated successfully`

### ✅ **API Request Logs**
- `[API] GET /users/me - hasToken: true, hasOrgId: true`
- `[API] Success GET /users/me - status: 200`

### ✅ **Dashboard Protection Logs**
- `[Dashboard] Component mounted, checking auth state`
- `[Dashboard] Auth context ready`

### ✅ **Error Handling Logs**
- `[API] Error ... - status: 401`
- `[API] 401 Error reason: ...`

## Common Issues and Solutions

### Issue: Dashboard flashes then redirects to login
**Check for:**
- Missing auth context during initial load
- Race condition between auth check and component mounting
- Incomplete localStorage state

**Look for logs:**
- `[Dashboard] No user found and not loading - redirecting to login`
- `[AuthContext] Failed to fetch user:`

### Issue: Session lost after license creation
**Check for:**
- Auto-login functionality accidentally enabled
- Token modification during license creation
- Context switching to new user

**Look for logs:**
- `[LicenseModal] Current auth state before license creation`
- `[LicenseModal] License creation complete - current user session preserved`

### Issue: 401 errors without clear reason
**Check for:**
- Missing organization context
- Expired tokens
- Invalid user state

**Look for logs:**
- `[ensure_organization_context] Organization access denied`
- `[API] 401 Error reason:`

---

This testing guide should help verify that all session continuity fixes are working correctly and provide clear debugging information when issues occur.