# Climoro Onboarding Resume Functionality

## Overview

The Climoro Onboarding form now includes a comprehensive resume functionality that allows users to save their progress and resume from where they left off. This feature is similar to the franchise portal implementation but customized for the Climoro onboarding process.

## Features

### 1. Welcome Modal (New)
- **Display**: Shows immediately when user visits `/apply`
- **Function**: Forces user to choose between new or resume application
- **Styling**: Beautiful modal with large buttons and descriptions
- **Form Blur**: Blurs the form behind the modal until choice is made

### 2. Resume Button (Removed)
- **Status**: Removed from header - functionality now handled by welcome modal
- **Reason**: Cleaner UI with welcome modal providing all navigation options

### 2. Resume Modal System
- **Welcome Modal**: Initial choice between new or resume application
- **Primary Modal**: Email input for resume link with back button
- **Success Modal**: Confirmation when resume link is sent
- **Application Modal**: Options to resume existing or start fresh

### 3. Email-Based Resume System
- **Token Generation**: Unique UUID-based tokens
- **24-Hour Expiry**: Security-focused token expiration
- **Custom Email Template**: Branded Climoro email design

### 4. Step Tracking
- **Current Step Field**: Tracks user progress in database
- **Resume from Last Step**: Users return to their last saved step
- **Progress Indicator**: Visual progress bar updates

## Technical Implementation

### Backend API Functions

#### 1. `send_resume_email(email)`
```python
@frappe.whitelist(allow_guest=True)
def send_resume_email(email):
    """Send resume email to user with unique token"""
```

**Features:**
- Validates email and checks for existing draft applications
- Generates unique resume token
- Stores session data in cache for 24 hours
- Sends branded email with resume link

#### 2. `verify_resume_token(token)`
```python
@frappe.whitelist(allow_guest=True)
def verify_resume_token(token):
    """Verify resume token and return application data"""
```

**Features:**
- Validates token and checks expiration
- Retrieves latest application data
- Returns current step and form data
- Refreshes cache with updated data

#### 3. Enhanced `save_step_data(step_data)`
```python
@frappe.whitelist(allow_guest=True)
def save_step_data(step_data):
    """Save step data to existing draft application"""
```

**Features:**
- Saves data for all 6 steps
- Updates current_step field
- Handles complex form fields (checkboxes, child tables)
- Returns success status and current step

### Frontend Implementation

#### 1. Resume Button (Removed)
```html
<!-- Resume button removed - functionality now handled by welcome modal -->
```

#### 2. Modal System
- **Resume Modal**: Email input form
- **Success Modal**: Confirmation message
- **Application Modal**: Resume/Start fresh options

#### 3. JavaScript Functions
```javascript
// Initialize welcome modal (checks for tokens)
function initializeWelcomeModal()

// Initialize resume functionality
function initializeResumeFunctionality()

// Check for resume/verification tokens in URL
function checkForResumeToken()

// Verify resume token
function verifyResumeToken(token)

// Restore form data
function restoreFormData(sessionData)

// Reset form
function resetForm()
```

## User Flow

### 1. Initial Page Load
1. User visits `/apply` URL
2. Welcome modal appears immediately (unless verification/resume token present)
3. Form is blurred behind the modal
4. User must choose: "Start New Application" or "Resume Application"

### 2. Starting a New Application
1. User clicks "Start New Application" in welcome modal
2. Modal closes, form unblurs
3. User fills out Step 1 (Contact Details)
4. Data is automatically saved as draft
5. User can continue or leave the form

### 3. Resuming an Application
1. User clicks "Resume Application" in welcome modal
2. Resume modal opens asking for email address (form stays blurred)
3. User enters email and clicks "Send Resume Link"
4. User can click "← Back" to return to welcome modal
5. Email is sent with secure resume link
6. User clicks link in email
7. Form loads with previous data and correct step

### 4. Resume Options
When user clicks resume link:
- **Resume Existing**: Loads previous data and continues
- **Start Fresh**: Clears form and starts over

## Email Template

The resume email includes:
- Climoro branding and logo
- Personalized greeting with company name
- Clear call-to-action button
- Security notice about 24-hour expiry
- Support information

## Security Features

1. **Token Expiration**: 24-hour automatic expiry
2. **Unique Tokens**: UUID-based token generation
3. **Cache Storage**: Secure session data storage
4. **Email Validation**: Only sends to verified email addresses
5. **URL Cleaning**: Removes tokens from URL after use

## User Experience Improvements

1. **Clear Navigation**: Welcome modal forces user choice upfront
2. **Form Blur**: Prevents interaction until choice is made
3. **Back Button**: Easy navigation between modals
4. **Consistent State**: Form stays blurred during resume flow
5. **Smooth Transitions**: Professional animations and effects

## Database Schema

### Onboarding Form Fields
- `current_step`: Integer field tracking user progress (1-6)
- `status`: Draft/Submitted status
- All existing form fields for data persistence

### Cache Storage
- **Key Format**: `climoro_resume_{token}`
- **Data Structure**: JSON with email, current_step, application_data
- **Expiry**: 24 hours (86400 seconds)

## Testing

### Manual Testing
1. **Normal flow**: Visit `/apply` - welcome modal should appear
2. **With verification token**: Visit `/apply?verify=token` - no welcome modal
3. **With resume token**: Visit `/apply?resume=token` - no welcome modal
4. Start filling out the form
2. Leave at any step
3. Click resume button
4. Enter email and send resume link
5. Check email and click link
6. Verify form loads with correct data and step

### Automated Testing
Run the test script:
```bash
cd frappe-bench
bench --site your-site.com console
exec(open('apps/climoro_onboarding/climoro_onboarding/www/apply/test_resume_functionality.py').read())
```

## Configuration

### Email Settings
- Ensure email is configured in Frappe
- Test email delivery in development
- Monitor email logs for issues

### Cache Settings
- Default expiry: 24 hours
- Cache backend: Frappe cache system
- Storage: Redis/Memory based on Frappe configuration

## Troubleshooting

### Common Issues

1. **Resume link not working**
   - Check token expiration
   - Verify email configuration
   - Check cache storage

2. **Form data not loading**
   - Verify current_step field
   - Check application status (should be "Draft")
   - Review browser console for errors

3. **Email not received**
   - Check spam folder
   - Verify email configuration
   - Check Frappe email logs

### Debug Functions
```javascript
// Check resume token in console
console.log('Resume token:', new URLSearchParams(window.location.search).get('resume'));

// Debug form data
console.log('Application data:', window.applicationData);

// Check current step
console.log('Current step:', currentStep);
```

## Future Enhancements

1. **SMS Resume**: Add SMS-based resume functionality
2. **Auto-save**: Periodic auto-save during form filling
3. **Progress Tracking**: Analytics on form completion rates
4. **Multi-language**: Support for multiple languages
5. **Mobile Optimization**: Enhanced mobile experience

## Support

For technical support or questions about the resume functionality:
1. Check the Frappe logs for errors
2. Review the browser console for JavaScript errors
3. Verify email and cache configuration
4. Test with the provided test script

## Changelog

### Version 1.0.0 (Current)
- Initial implementation of resume functionality
- Email-based resume system
- 24-hour token expiry
- Custom Climoro email template
- Complete step tracking
- Modal-based user interface 