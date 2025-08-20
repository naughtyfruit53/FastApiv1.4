# Manual Testing Guide: Org Superadmin Session Continuity Fix - UPDATED

## Overview
This updated guide provides step-by-step testing procedures to validate that the org superadmin logout issue has been resolved with the latest race condition prevention and context hardening improvements.

## Prerequisites
- ERP system running with both frontend and backend
- Access to browser developer tools
- Valid org superadmin credentials
- Access to backend logs

## New Improvements to Test

### 1. API Request Queuing
- API requests now wait for auth context to be ready
- Protected endpoints are queued until authentication is established
- Public endpoints (login, OTP) proceed immediately

### 2. Retry Logic with Exponential Backoff
- Failed user context fetches are retried up to 2 times
- Delays: 1s, 2s, 4s between retries
- Only retries on non-401 errors

### 3. Enhanced Error Handling
- Toast notifications for better user feedback
- Specific error messages for different failure scenarios
- Comprehensive localStorage cleanup on auth failures

### 4. Context Synchronization
- AuthContext properly manages auth ready state
- API client and contexts are synchronized
- Race condition prevention between multiple components

## Test Cases

### Test Case 1: Basic Org Superadmin Login with Race Condition Prevention

**Objective:** Verify that org superadmin can login and access dashboard without race conditions.

**Steps:**
1. Open browser and navigate to login page
2. Open Developer Tools (F12) → Console tab
3. Clear console logs
4. Enter valid org superadmin credentials
5. Click Login button
6. Watch for the new improved logging sequence

**Expected Console Logs:**
```
[Login] Login successful, processing response...
[Login] All auth context stored, establishing session...
[AuthContext] Login called with new token
[AuthContext] Starting fetchUser - getting current user data {attempt: 1, maxRetries: 3}
[AuthContext] User data received from API...
[API] Auth context marked as ready
[Dashboard] Component mounted, checking auth state
[CompanyContext] Auth context ready, checking company details
[API] GET /companies/current - hasToken: true, hasOrgId: true, authReady: true
[Dashboard] Auth context ready - determining dashboard type
```

**Expected Results:**
- No 401 errors
- Dashboard loads successfully
- All API requests show `authReady: true` when they execute
- No premature API calls before auth is ready

### Test Case 2: Network Error Retry Testing

**Objective:** Test the new retry logic with exponential backoff.

**Steps:**
1. Login as org superadmin
2. Open Developer Tools → Network tab
3. Set network throttling to "Slow 3G" or "Offline"
4. Refresh the page
5. Quickly restore network connectivity
6. Observe retry behavior in console

**Expected Console Logs:**
```
[AuthContext] Failed to fetch user: {message: "Network Error", attempt: 1}
[AuthContext] Retrying fetchUser in 1000ms (attempt 2/3)
[AuthContext] Starting fetchUser - getting current user data {attempt: 2, maxRetries: 3}
[AuthContext] User data received from API...
[API] Auth context marked as ready
```

**Expected Results:**
- System automatically retries failed requests
- Exponential backoff delays are visible
- User is not logged out due to transient network issues
- Success on retry shows proper recovery

### Test Case 3: Toast Notification Testing

**Objective:** Verify enhanced error feedback with toast notifications.

**Steps:**
1. Login with invalid credentials
2. Or simulate a 401 error by manually calling a protected endpoint with an expired token
3. Observe toast notifications

**Expected Results:**
- Toast notifications appear for authentication errors
- Specific error messages are shown
- Example: "Session expired: Token has expired"
- Or: "Authentication failed: Invalid credentials"

### Test Case 4: API Request Queuing

**Objective:** Test that API requests wait for auth context.

**Steps:**
1. Open browser with slow network conditions
2. Login as org superadmin
3. Watch console logs carefully during login process
4. Look for queuing behavior

**Expected Console Logs:**
```
[API] Waiting for auth context to be ready for: /companies/current
[API] Waiting for auth context to be ready for: /users/me
[API] Auth context ready, proceeding with request: /companies/current
[API] Auth context ready, proceeding with request: /users/me
```

**Expected Results:**
- Protected API calls show "Waiting for auth context" messages
- Requests proceed only after auth is marked ready
- No 401 errors due to premature API calls

### Test Case 5: Multiple Component Race Condition

**Objective:** Test that multiple components calling APIs simultaneously don't cause issues.

**Steps:**
1. Login as org superadmin
2. Open multiple browser tabs to the dashboard
3. Refresh all tabs simultaneously (Ctrl+F5 on each)
4. Watch console logs in each tab

**Expected Results:**
- All tabs load successfully
- Each tab shows proper auth context establishment
- No race conditions between Dashboard, CompanyContext, and other components
- All API calls wait for auth context before proceeding

### Test Case 6: Context Synchronization

**Objective:** Verify localStorage and React context stay synchronized.

**Steps:**
1. Login as org superadmin
2. Open Developer Tools → Application → Local Storage
3. Verify all auth data is stored correctly
4. Check that React context matches localStorage
5. Navigate between pages and verify consistency

**Expected localStorage Data:**
- `token`: JWT token string
- `organization_id`: Organization ID number
- `user_role`: User role string
- `is_super_admin`: "true" or "false"

**Expected Results:**
- All required data present in localStorage
- React context reflects the same data
- Data persists across navigation
- No mismatches between storage and context

## Backend Verification

### Check Backend Logs
Access backend logs and verify detailed logging for debugging:

**Expected Backend Logs:**
```
[/companies/current] Request from user: 123 (admin@example.com)
[/companies/current] User context: role=admin, is_super_admin=False, org_id=42
[ensure_organization_context] Organization context established: org_id=42
[/users/me] Request from user: 123 (admin@example.com)
```

## Debugging New Features

### If API Requests Still Fail
1. Check that `markAuthReady()` is called after user context is established
2. Verify that protected endpoints are not in the public endpoints list
3. Look for auth ready state in API request logs

### If Retry Logic Doesn't Work
1. Verify error status is not 401 (401 errors don't retry)
2. Check that retry count is within limits (max 2 retries)
3. Look for exponential backoff timing in logs

### If Toast Notifications Don't Appear
1. Verify react-toastify is properly imported
2. Check that ToastContainer is rendered in the app
3. Look for toast function calls in console logs

## Success Criteria for New Improvements

The session continuity fix is successful when:

1. ✅ **API Request Queuing**: Protected API requests wait for auth context
2. ✅ **Retry Logic**: Failed requests are retried with exponential backoff  
3. ✅ **Toast Notifications**: Clear error messages are shown to users
4. ✅ **Race Condition Prevention**: Multiple components don't interfere with each other
5. ✅ **Context Synchronization**: localStorage and React context stay in sync
6. ✅ **No Premature Logouts**: Org superadmins stay logged in during normal operations

## Performance Verification

The improvements should not significantly impact performance:
- Auth ready waiting adds < 100ms delay typically
- Retry logic only activates on actual failures  
- Toast notifications are lightweight
- Additional logging has minimal overhead

## Rollback Plan

If issues are discovered:
1. The auth ready state can be disabled by always returning `true`
2. Retry logic can be disabled by setting max retries to 0
3. Toast notifications can be replaced with console.log
4. Original AuthContext behavior can be restored

---

**Note:** These improvements specifically target the race condition and context propagation issues causing org superadmin logouts. The comprehensive logging and error handling will make any remaining issues much easier to diagnose and fix.