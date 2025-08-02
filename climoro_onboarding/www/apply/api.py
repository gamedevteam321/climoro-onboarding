"""
Climoro Onboarding API - Main Entry Point
This file serves as the main API entry point and imports functions from modular files.
"""

# Import functions from modular files
from .form_api import (
    submit_onboarding_form,
    get_existing_application,
    save_step_data,
    get_saved_data
)

from .email_api import (
    send_verification_email,
    verify_email,
    send_resume_email,
    get_session_data,
    test_email_verification_flow
)

from .resume_api import (
    verify_resume_token,
    debug_resume_token,
    check_current_step_debug,
    update_current_step_debug
)

from .file_api import (
    upload_file,
    validate_file_upload,
    delete_uploaded_file,
    get_file_info
)

# Re-export all functions for backward compatibility
__all__ = [
    # Form functions
    'submit_onboarding_form',
    'get_existing_application', 
    'save_step_data',
    'get_saved_data',
    
    # Email functions
    'send_verification_email',
    'verify_email',
    'send_resume_email',
    'get_session_data',
    'test_email_verification_flow',
    
    # Resume functions
    'verify_resume_token',
    'debug_resume_token',
    'check_current_step_debug',
    'update_current_step_debug',
    
    # File functions
    'upload_file',
    'validate_file_upload',
    'delete_uploaded_file',
    'get_file_info'
] 