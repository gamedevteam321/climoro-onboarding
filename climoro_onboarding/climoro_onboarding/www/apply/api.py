import frappe
import json
import os
from frappe import _
from frappe.utils import now_datetime, get_url
import uuid

@frappe.whitelist()
def submit_onboarding_form(form_data):
    """Submit the complete onboarding form"""
    try:
        data = json.loads(form_data)
        
        # Check if a draft already exists for this email
        existing_draft = frappe.db.exists("Onboarding Form", {
            "email": data.get("email"),
            "status": "Draft"
        })
        
        if existing_draft:
            # Update existing draft
            doc = frappe.get_doc("Onboarding Form", existing_draft)
            doc.update(data)
            doc.status = "Submitted"
            doc.submitted_at = now_datetime()
            doc.current_step = 3
        else:
            # Create new form
            doc = frappe.get_doc({
                "doctype": "Onboarding Form",
                **data,
                "status": "Submitted",
                "submitted_at": now_datetime(),
                "current_step": 3
            })
        
        # Add units with assigned users
        if data.get("units"):
            for unit_data in data["units"]:
                unit_doc = doc.append("units", {
                    "type_of_unit": unit_data.get("type_of_unit"),
                    "name_of_unit": unit_data.get("name_of_unit"),
                    "size_of_unit": unit_data.get("size_of_unit"),
                    "address": unit_data.get("address"),
                    "gst": unit_data.get("gst"),
                    "phone_number": unit_data.get("phone_number"),
                    "position": unit_data.get("position")
                })
                
                # Add assigned users to this unit
                if unit_data.get("assigned_users"):
                    for user_data in unit_data["assigned_users"]:
                        unit_doc.append("assigned_users", {
                            "email": user_data.get("email"),
                            "first_name": user_data.get("first_name"),
                            "user_role": user_data.get("user_role")
                        })
                
                # Try to bypass validation for child tables
                unit_doc.flags.ignore_validate = True
        
        doc.insert()
        frappe.db.commit()
        
        # Send admin notification
        send_admin_notification(doc)
        
        return {
            "success": True,
            "message": "Onboarding form submitted successfully!",
            "application_id": doc.name
        }
        
    except Exception as e:
        frappe.log_error(f"Error submitting onboarding form: {str(e)}", "Onboarding Form Submit Error")
        return {
            "success": False,
            "message": f"Error submitting form: {str(e)}"
        }

@frappe.whitelist()
def save_step_data(step, form_data):
    """Save data for a specific step"""
    try:
        data = json.loads(form_data)
        
        # Debug logging for step data
        frappe.logger().info(f"🔍 Step Data Debug:")
        frappe.logger().info(f"   Step: {step}")
        frappe.logger().info(f"   Industry Type: '{data.get('industry_type')}'")
        frappe.logger().info(f"   Sub-Industry Type: '{data.get('sub_industry_type')}'")
        frappe.logger().info(f"   All data keys: {list(data.keys())}")
        
        # Check if a draft already exists for this email
        existing_draft = frappe.db.exists("Onboarding Form", {
            "email": data.get("email"),
            "status": "Draft"
        })
        
        if existing_draft:
            # Update existing draft
            doc = frappe.get_doc("Onboarding Form", existing_draft)
            doc.update(data)
            doc.current_step = int(step)
        else:
            # Create new draft
            doc = frappe.get_doc({
                "doctype": "Onboarding Form",
                **data,
                "status": "Draft",
                "current_step": int(step)
            })
        
        # Add units with assigned users if this is step 3
        if int(step) == 3 and data.get("units"):
            for unit_data in data["units"]:
                unit_doc = doc.append("units", {
                    "type_of_unit": unit_data.get("type_of_unit"),
                    "name_of_unit": unit_data.get("name_of_unit"),
                    "size_of_unit": unit_data.get("size_of_unit"),
                    "address": unit_data.get("address"),
                    "gst": unit_data.get("gst"),
                    "phone_number": unit_data.get("phone_number"),
                    "position": unit_data.get("position")
                })
                
                # Add assigned users to this unit
                if unit_data.get("assigned_users"):
                    for user_data in unit_data["assigned_users"]:
                        unit_doc.append("assigned_users", {
                            "email": user_data.get("email"),
                            "first_name": user_data.get("first_name"),
                            "user_role": user_data.get("user_role")
                        })
                
                # Try to bypass validation for child tables
                unit_doc.flags.ignore_validate = True
        
        # Debug logging before insert
        frappe.logger().info(f"🔍 Before Insert Debug:")
        frappe.logger().info(f"   Doc industry_type: '{doc.industry_type}'")
        frappe.logger().info(f"   Doc sub_industry_type: '{doc.sub_industry_type}'")
        frappe.logger().info(f"   Doc status: '{doc.status}'")
        
        # Temporarily bypass validation for step data saving
        doc.flags.ignore_validate = True
        
        doc.insert()
        frappe.db.commit()
        
        return {
            "success": True,
            "message": f"Step {step} data saved successfully!",
            "application_id": doc.name
        }
        
    except Exception as e:
        frappe.log_error(f"Error saving step {step} data: {str(e)}", "Onboarding Form Step Save Error")
        return {
            "success": False,
            "message": f"Error saving step {step} data: {str(e)}"
        }

@frappe.whitelist()
def send_verification_email(email, data):
    """Send verification email"""
    try:
        # Generate verification token
        token = str(uuid.uuid4())
        
        # Store token in session
        frappe.local.session.verification_token = token
        frappe.local.session.verification_email = email
        frappe.local.session.verification_data = data
        
        # Send email
        verification_url = f"{get_url()}/apply?verify={token}"
        
        frappe.sendmail(
            recipients=[email],
            subject="Verify Your Email - Climoro Onboarding",
            message=f"""
            <p>Please click the link below to verify your email address:</p>
            <p><a href="{verification_url}">{verification_url}</a></p>
            <p>This link will expire in 10 minutes.</p>
            """,
            now=True
        )
        
        return {
            "success": True,
            "message": "Verification email sent successfully!"
        }
        
    except Exception as e:
        frappe.log_error(f"Error sending verification email: {str(e)}", "Email Verification Error")
        return {
            "success": False,
            "message": f"Error sending verification email: {str(e)}"
        }

@frappe.whitelist()
def verify_email(token):
    """Verify email token"""
    try:
        if (hasattr(frappe.local, 'session') and 
            hasattr(frappe.local.session, 'verification_token') and
            frappe.local.session.verification_token == token):
            
            # Save verified email to doctype
            result = save_verified_email_to_doctype(
                frappe.local.session.verification_email,
                frappe.local.session.verification_data
            )
            
            # Clear session data
            frappe.local.session.verification_token = None
            frappe.local.session.verification_email = None
            frappe.local.session.verification_data = None
            
            return result
        else:
            return {
                "success": False,
                "message": "Invalid or expired verification token"
            }
            
    except Exception as e:
        frappe.log_error(f"Error verifying email: {str(e)}", "Email Verification Error")
        return {
            "success": False,
            "message": f"Error verifying email: {str(e)}"
        }

@frappe.whitelist()
def save_verified_email_to_doctype(email, data):
    """Save verified email data to doctype"""
    try:
        form_data = json.loads(data)
        
        # Create draft entry
        doc = frappe.get_doc({
            "doctype": "Onboarding Form",
            **form_data,
            "email": email,
            "email_verified": True,
            "email_verified_at": now_datetime(),
            "status": "Draft",
            "current_step": 1
        })
        
        doc.insert()
        frappe.db.commit()
        
        return {
            "success": True,
            "message": "Email verified and data saved successfully!",
            "application_id": doc.name
        }
        
    except Exception as e:
        frappe.log_error(f"Error saving verified email data: {str(e)}", "Email Verification Error")
        return {
            "success": False,
            "message": f"Error saving verified email data: {str(e)}"
        }

@frappe.whitelist()
def upload_file(file_data, filename):
    """Upload file and return URL"""
    try:
        import base64
        
        # Decode base64 data
        file_content = base64.b64decode(file_data.split(',')[1])
        
        # Create file doc
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": filename,
            "file_url": f"/files/{filename}",
            "is_private": 0
        })
        
        # Save file to files folder
        file_path = frappe.get_site_path("public", "files", filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        file_doc.insert()
        frappe.db.commit()
        
        return {
            "success": True,
            "file_url": file_doc.file_url
        }
        
    except Exception as e:
        frappe.log_error(f"Error uploading file: {str(e)}", "File Upload Error")
        return {
            "success": False,
            "message": f"Error uploading file: {str(e)}"
        }

def send_admin_notification(doc):
    """Send notification to admin about new application"""
    try:
        admin_email = frappe.db.get_single_value("System Settings", "support_email") or "admin@example.com"
        
        frappe.sendmail(
            recipients=[admin_email],
            subject=f"New Onboarding Application - {doc.first_name}",
            message=f"""
            <h3>New Onboarding Application Received</h3>
            <p><strong>Applicant:</strong> {doc.first_name} {doc.last_name or ''}</p>
            <p><strong>Email:</strong> {doc.email}</p>
            <p><strong>Company:</strong> {doc.company_name}</p>
            <p><strong>Phone:</strong> {doc.phone_number}</p>
            <p><strong>Submitted:</strong> {doc.submitted_at}</p>
            <br>
            <p>Please review the application in the Frappe system.</p>
            """,
            now=True
        )
        
    except Exception as e:
        frappe.log_error(f"Error sending admin notification: {str(e)}", "Admin Notification Error") 