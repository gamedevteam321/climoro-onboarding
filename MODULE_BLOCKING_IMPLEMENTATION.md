# Module Blocking Implementation for Onboarding Forms

## Overview

This implementation adds functionality to block all modules for users created during the onboarding approval process. When an onboarding form is approved, all newly created users (both main user and unit users) will have all available modules blocked by default.

## What Was Implemented

### 1. Modified User Creation Methods

#### `_create_main_user()` Method
- **Location**: `onboarding_form.py` (lines ~174-226)
- **Changes**: Added module blocking for the main user (Super Admin)
- **Functionality**: 
  - Blocks all modules for both new and existing users
  - Applies to users with Super Admin role
  - Logs the blocking action
  - **Note**: Only creates user account, no employee record

#### `_create_single_unit_user()` Method  
- **Location**: `onboarding_form.py` (lines ~246-298)
- **Changes**: Added module blocking for unit users
- **Functionality**:
  - Blocks all modules for both new and existing unit users
  - Applies to users with Unit Manager, Data Analyst, or other roles
  - Logs the blocking action
  - **Note**: Only creates user account, no employee record

### 2. New Helper Method

#### `_block_all_modules_for_user()` Method
- **Location**: `onboarding_form.py` (lines ~300-320)
- **Purpose**: Centralized method to block all modules for any user
- **Functionality**:
  - Gets all available modules from the system using `frappe.config.get_modules_from_all_apps()`
  - Clears existing blocked modules
  - Adds all modules to the user's `block_modules` table
  - Handles errors gracefully and logs issues

### 3. Removed Employee Record Creation
- **Removed**: `_create_employee_record()` method
- **Reason**: Simplified user creation process
- **Result**: Only user accounts are created, no employee records

## How It Works

### Module Blocking Process

1. **When Onboarding is Approved**:
   - Company is created
   - Main user (Super Admin) is created/updated with all modules blocked
   - Unit users are created/updated with all modules blocked
   - **Note**: Employee records are not created - only user accounts are created

2. **Module Blocking Details**:
   - Uses Frappe's built-in `block_modules` table in the User doctype
   - Gets all available modules from all installed apps
   - Blocks every module by adding it to the `block_modules` child table
   - Users will not see any modules in their workspace

3. **User Experience**:
   - Users will have a clean workspace with no modules visible
   - They can only access what's explicitly granted through roles
   - Module access can be selectively enabled later by removing specific modules from `block_modules`

## Technical Implementation

### Code Structure

```python
def _block_all_modules_for_user(self, user_doc):
    """Block all available modules for a user"""
    try:
        # Get all available modules from the system
        from frappe.config import get_modules_from_all_apps
        all_modules = get_modules_from_all_apps()
        
        # Clear existing blocked modules
        user_doc.set("block_modules", [])
        
        # Add all modules to blocked modules
        for module_data in all_modules:
            module_name = module_data.get("module_name")
            if module_name:
                user_doc.append("block_modules", {"module": module_name})
        
        frappe.logger().info(f"Blocked {len(all_modules)} modules for user {user_doc.email}")
        
    except Exception as e:
        frappe.log_error(f"Error blocking modules for user {user_doc.email}: {str(e)}")
        # Continue with user creation even if module blocking fails
```

### Integration Points

- **Called from**: `_create_main_user()` and `_create_single_unit_user()`
- **Database**: Uses User doctype's `block_modules` child table
- **Logging**: Comprehensive logging for debugging and monitoring

## Testing

### Test Scripts Created

1. **`test_module_blocking.py`**:
   - Tests the complete workflow
   - Creates test onboarding form
   - Approves it and verifies module blocking
   - Checks both main user and unit users

2. **Verification Functions**:
   - `test_module_blocking_workflow()`: Full workflow test
   - `verify_existing_users_module_blocking()`: Check existing users
   - `test_module_access()`: Verify module access restrictions

### How to Test

```bash
# Run the test from Frappe bench
bench --site localhost console

# In the console:
from climoro_onboarding.climoro_onboarding.climoro_onboarding.test_module_blocking import test_module_blocking_workflow
test_module_blocking_workflow()
```

## Benefits

### Security
- **Principle of Least Privilege**: Users start with no module access
- **Controlled Access**: Modules must be explicitly enabled
- **Audit Trail**: All blocking actions are logged

### User Management
- **Clean Workspace**: Users see only what they need
- **Flexible Control**: Easy to enable specific modules later
- **Consistent Experience**: All onboarding users start with same restrictions

### Administrative Control
- **Centralized Management**: All blocking happens during approval
- **Error Handling**: Graceful failure if blocking fails
- **Monitoring**: Comprehensive logging for troubleshooting

## Future Enhancements

### Potential Improvements

1. **Selective Module Blocking**:
   - Allow configuration of which modules to block
   - Module blocking profiles
   - Role-based module access

2. **Module Unblocking**:
   - Admin interface to unblock specific modules
   - Bulk operations for multiple users
   - Scheduled module access

3. **Enhanced Logging**:
   - Track module access changes
   - User activity monitoring
   - Compliance reporting

## Configuration

### Current Settings
- **Default Behavior**: All modules blocked for all new users
- **Error Handling**: Continue user creation even if blocking fails
- **Logging Level**: Info for successful blocking, Error for failures

### Customization Options
- Modify `_block_all_modules_for_user()` to exclude specific modules
- Add configuration options to onboarding form
- Create module blocking profiles

## Troubleshooting

### Common Issues

1. **No Modules Blocked**:
   - Check if `get_modules_from_all_apps()` returns data
   - Verify user creation completed successfully
   - Check error logs for exceptions

2. **Partial Module Blocking**:
   - Verify all modules are being processed
   - Check for module name validation issues
   - Review error logs for specific failures

3. **User Creation Fails**:
   - Module blocking errors won't prevent user creation
   - Check other validation issues
   - Review user creation logs

### Debug Commands

```python
# Check available modules
from frappe.config import get_modules_from_all_apps
modules = get_modules_from_all_apps()
print(f"Total modules: {len(modules)}")

# Check user's blocked modules
user = frappe.get_doc("User", "user@example.com")
blocked = [bm.module for bm in user.block_modules]
print(f"Blocked modules: {len(blocked)}")
```

## Conclusion

This implementation provides a secure, controlled approach to user access management during the onboarding process. All users start with no module access and can be granted specific permissions as needed, following security best practices and providing a clean user experience. 