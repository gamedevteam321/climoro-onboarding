import frappe
from frappe import _
from frappe.utils import now, now_datetime, get_url
import uuid
import json
from datetime import timedelta


@frappe.whitelist(allow_guest=True)
def send_verification_email(email, data):
    """Send email verification after Step 1 completion"""
    try:
        # Validate input
        if not email or not email.strip():
            return {"success": False, "message": "Email is required"}
        
        # Validate email format
        if not frappe.utils.validate_email_address(email):
            return {"success": False, "message": "Invalid email format"}
        
        # Handle JSON string data from frontend
        if isinstance(data, str):
            data = json.loads(data)
        
        # Generate verification token
        verification_token = str(uuid.uuid4())
        
        # Store session data temporarily (expires in 24 hours)
        session_key = f"climoro_onboarding_{verification_token}"
        session_data = {
            "email": email,
            "data": data,
            "current_step": 1,
            "verified": False,
            "created_at": now()
        }
        
        # Store in cache for 24 hours (86400 seconds)
        frappe.cache().set_value(session_key, json.dumps(session_data), expires_in_sec=86400)
        
        # Create verification URL
        site_url = frappe.utils.get_url()
        verification_url = f"{site_url}/apply?verify={verification_token}"
        
        # Send verification email
        send_verification_email_to_user(email, data.get("company_name", ""), verification_url)
        
        return {
            "success": True,
            "message": "Verification email sent successfully",
            "requires_verification": True,
            "verification_token": verification_token
        }
        
    except Exception as e:
        frappe.log_error(f"Error sending verification email: {str(e)}", "Climoro Onboarding Verification Error")
        return {
            "success": False,
            "message": f"Error sending verification email: {str(e)}"
        }


@frappe.whitelist(allow_guest=True)
def verify_email(token):
    """Verify email and create draft onboarding form entry"""
    try:
        if not token:
            return {"success": False, "message": "Verification token is required"}
            
        session_key = f"climoro_onboarding_{token}"
        session_data_str = frappe.cache().get_value(session_key)
        
        if not session_data_str:
            return {"success": False, "message": "Invalid or expired verification token"}
            
        session_data = json.loads(session_data_str)
        email = session_data.get("email")
        
        if not email:
            return {"success": False, "message": "Email not found in session data"}
        
        # Mark as verified in session
        session_data["verified"] = True
        session_data["verified_at"] = now()
        
        # Update cache with verified status
        frappe.cache().set_value(session_key, json.dumps(session_data), expires_in_sec=86400)
        
        # Save/update the doctype with verified email data
        application_id = save_verified_email_to_doctype(email, session_data)
        
        # Update session data with the application ID if we got one
        if application_id:
            session_data["application_id"] = application_id
            # Update cache with application ID
            frappe.cache().set_value(session_key, json.dumps(session_data), expires_in_sec=86400)
        
        return {
            "success": True,
            "message": "Email verified successfully",
            "session_data": session_data,
            "email": email,
            "application_id": application_id
        }
        
    except Exception as e:
        frappe.log_error(f"Error in verify_email: {str(e)}", "Climoro Onboarding Verification Error")
        return {
            "success": False,
            "message": f"Error verifying email: {str(e)}"
        }


def save_verified_email_to_doctype(email, session_data):
    """Save or update doctype with verified email data"""
    try:
        # Check if application already exists for this email
        existing_applications = frappe.get_all(
            "Onboarding Form",
            filters={"email": email},
            fields=["name", "status"],
            limit=1
        )
        
        if existing_applications:
            # Update existing application
            existing_app = existing_applications[0]
            doc_name = existing_app["name"]
            
            # Update with verification status and basic fields
            updates = {
                "email_verified": 1,
                "email_verified_at": now(),
                "status": "Draft",
                "current_step": 1
            }
            
            # Add Step 1 data from session
            application_data = session_data.get("data", {})
            
            basic_fields = [
                "first_name", "middle_name", "last_name", "phone_number", "position"
            ]
            for field in basic_fields:
                if field in application_data and application_data[field]:
                    updates[field] = application_data[field]
            
            frappe.db.set_value("Onboarding Form", doc_name, updates)
            frappe.db.commit()
            
            return doc_name
        else:
            # No existing application found - create new one
            try:
                doc = frappe.new_doc("Onboarding Form")
                doc.email = email
                doc.email_verified = 1
                doc.email_verified_at = now()
                doc.status = "Draft"
                doc.current_step = 1
                
                # Set naming series explicitly
                if not doc.naming_series:
                    doc.naming_series = "OF-.YYYY.-"
                
                # Add Step 1 data from session
                application_data = session_data.get("data", {})
                
                basic_fields = [
                    "first_name", "middle_name", "last_name", "phone_number", "position"
                ]
                for field in basic_fields:
                    if field in application_data and application_data[field]:
                        setattr(doc, field, application_data[field])
                
                # Use flag to prevent automatic email modification
                frappe.flags.ignore_email_uniqueness = True
                doc.insert(ignore_permissions=True)
                frappe.flags.ignore_email_uniqueness = False
                
                frappe.db.commit()
                
                return doc.name
            except Exception as e:
                frappe.log_error(f"Exception during doc.insert: {str(e)}", "Climoro Onboarding Doc Creation Error")
                return None
                
    except Exception as e:
        frappe.log_error(f"Error in save_verified_email_to_doctype: {str(e)}", "Climoro Onboarding Doc Creation Error")
        return None


@frappe.whitelist(allow_guest=True)
def send_resume_email(email):
    """Send resume email to user with unique token"""
    try:
        # Validate input
        if not email or not email.strip():
            return {
                "success": False,
                "message": "Email address is required"
            }
        
        # Validate email format
        if not frappe.utils.validate_email_address(email):
            return {
                "success": False,
                "message": "Invalid email format"
            }
        
        # Check if there's an existing draft application
        existing_applications = frappe.get_all(
            "Onboarding Form",
            filters={"email": email, "status": "Draft"},
            fields=["name", "current_step", "company_name"],
            order_by="modified desc",
            limit=1
        )
        
        if not existing_applications:
            return {
                "success": False,
                "message": "No incomplete application found for this email address. Please start a new application."
            }
        
        application = existing_applications[0]
        
        # Generate unique resume token
        resume_token = str(uuid.uuid4())
        
        # Create resume URL
        site_url = get_url()
        resume_url = f"{site_url}/apply?resume={resume_token}"
        
        # Store session data in cache for 24 hours
        session_data = {
            "email": email,
            "application_id": application.name,
            "current_step": application.current_step or 1,
            "company_name": application.company_name,
            "created_at": now_datetime().isoformat(),
            "expires_at": (now_datetime() + timedelta(hours=24)).isoformat()
        }
        
        session_key = f"climoro_resume_{resume_token}"
        frappe.cache().set_value(session_key, json.dumps(session_data), expires_in_sec=86400)  # 24 hours
        
        # Send resume email
        send_resume_email_to_user(email, application.company_name, resume_url)
        
        return {
            "success": True,
            "message": "Resume link sent to your email address. Please check your inbox."
        }
        
    except Exception as e:
        frappe.log_error(f"Error sending resume email: {str(e)}")
        return {
            "success": False,
            "message": f"Error sending resume email: {str(e)}"
        }


@frappe.whitelist(allow_guest=True)
def get_session_data(token):
    """Get session data for verified token"""
    try:
        if not token:
            return {"success": False, "message": "Verification token is required"}
            
        session_key = f"climoro_onboarding_{token}"
        session_data_str = frappe.cache().get_value(session_key)
        
        if not session_data_str:
            return {"success": False, "message": "Invalid or expired verification token"}
            
        session_data = json.loads(session_data_str)
        
        if not session_data.get("verified"):
            return {"success": False, "message": "Email not verified", "requires_verification": True}
        
        return {
            "success": True,
            "session_data": session_data
        }
        
    except Exception as e:
        frappe.log_error(f"Error getting session data: {str(e)}", "Climoro Onboarding Verification Error")
        return {
            "success": False,
            "message": f"Error retrieving session data: {str(e)}"
        }


@frappe.whitelist(allow_guest=True)
def test_email_verification_flow():
    """Test the email verification flow"""
    try:
        # Test data
        test_email = "test@example.com"
        test_data = {
            "first_name": "Test User",
            "phone_number": "1234567890",
            "position": "Manager"
        }
        
        # Step 1: Send verification email
        result1 = send_verification_email(test_email, test_data)
        if not result1.get("success"):
            return {"success": False, "message": f"Failed to send verification email: {result1.get('message')}"}
        
        verification_token = result1.get("verification_token")
        
        # Step 2: Verify email
        result2 = verify_email(verification_token)
        if not result2.get("success"):
            return {"success": False, "message": f"Failed to verify email: {result2.get('message')}"}
        
        # Step 3: Check if doctype was created/updated
        applications = frappe.get_all(
            "Onboarding Form",
            filters={"email": test_email},
            fields=["name", "email_verified", "email_verified_at", "first_name", "status", "current_step"]
        )
        
        if not applications:
            return {"success": False, "message": "No application found after verification"}
        
        app = applications[0]
        
        return {
            "success": True,
            "message": "Email verification flow test completed successfully",
            "application_id": app.name,
            "email_verified": app.email_verified,
            "email_verified_at": app.email_verified_at,
            "first_name": app.first_name,
            "status": app.status,
            "current_step": app.current_step
        }
        
    except Exception as e:
        return {"success": False, "message": f"Test failed: {str(e)}"}


def send_verification_email_to_user(email, company_name, verification_url):
    """Send verification email to the applicant"""
    subject = f"Verify Your Email - Climoro Onboarding Form"
    
    message = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #5e64ff;">Email Verification Required</h2>
        
        <p>Dear Applicant,</p>
        
        <p>Thank you for starting your Climoro onboarding process for <strong>{company_name or 'your company'}</strong>.</p>
        
        <p>To continue with your onboarding, please verify your email address by clicking the button below:</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{verification_url}" 
               style="background-color: #5e64ff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                Verify Email & Continue Onboarding
            </a>
        </div>
        
        <p style="color: #6c757d; font-size: 14px;">If the button doesn't work, copy and paste this link in your browser:</p>
        <p style="color: #5e64ff; word-break: break-all; font-size: 14px;">{verification_url}</p>
        
        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h4 style="margin-top: 0; color: #495057;">What happens next?</h4>
            <ul style="color: #6c757d; margin-bottom: 0;">
                <li>Click the verification link</li>
                <li>You'll be taken to Step 2: Company Details</li>
                <li>Complete the remaining sections</li>
                <li>Submit your complete onboarding form</li>
            </ul>
        </div>
        
        <p style="color: #dc3545; font-size: 14px;"><strong>Note:</strong> This verification link will expire in 24 hours.</p>
        
        <p>Best regards,<br>
        <strong>Climoro Team</strong></p>
    </div>
    """
    
    frappe.sendmail(
        recipients=[email],
        subject=subject,
        message=message,
        now=True
    )


def send_resume_email_to_user(email, company_name, resume_url):
    """Send resume email with custom climoro template"""
    subject = "Resume Your Climoro Onboarding Application"
    message = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; margin-bottom: 30px;">
                <img src="/assets/climoro_onboarding/images/climoro.png" alt="Climoro Logo" style="max-width: 200px; height: auto;">
            </div>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                <h2 style="color: #2c3e50; margin-top: 0;">Resume Your Onboarding Application</h2>
                <p style="color: #555; line-height: 1.6;">
                    Dear {company_name or 'Valued Customer'},
                </p>
                <p style="color: #555; line-height: 1.6;">
                    We noticed you started your Climoro onboarding application but didn't complete it. 
                    You can resume your application from where you left off by clicking the button below.
                </p>
                <p style="color: #555; line-height: 1.6;">
                    <strong>Important:</strong> This link will expire in 24 hours for security reasons.
                </p>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href='{resume_url}' style="background: #28a745; color: white; padding: 15px 30px; border-radius: 5px; text-decoration: none; font-weight: bold; display: inline-block;">
                    🔄 Resume Application
                </a>
            </div>
            
            <div style="background: #e9ecef; padding: 15px; border-radius: 5px; margin-top: 20px;">
                <p style="color: #6c757d; margin: 0; font-size: 14px;">
                    <strong>Need help?</strong> If you have any questions about your onboarding process, 
                    please don't hesitate to contact our support team.
                </p>
            </div>
            
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; text-align: center;">
                <p style="color: #6c757d; font-size: 12px; margin: 0;">
                    Best regards,<br>
                    The Climoro Team
                </p>
            </div>
        </div>
    """
    
    frappe.sendmail(
        recipients=[email], 
        subject=subject, 
        message=message, 
        now=True
    ) 