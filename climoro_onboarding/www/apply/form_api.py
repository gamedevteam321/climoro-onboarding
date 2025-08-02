import frappe
from frappe import _
from frappe.utils import now_datetime
import json


@frappe.whitelist(allow_guest=True)
def submit_onboarding_form(form_data):
    """Submit the complete onboarding form"""
    try:
        # Handle JSON string data from frontend
        if isinstance(form_data, str):
            form_data = json.loads(form_data)
        
        # Validate required fields
        required_fields = ['email', 'first_name', 'phone_number']
        for field in required_fields:
            if not form_data.get(field):
                return {
                    "success": False,
                    "message": f"Required field '{field}' is missing"
                }
        
        email = form_data.get("email")
        
        # Check if there's an existing draft application for this email
        existing_applications = frappe.get_all(
            "Onboarding Form",
            filters={"email": email, "status": "Draft"},
            fields=["name", "current_step"],
            order_by="modified desc",
            limit=1
        )
        
        if existing_applications:
            # Update existing draft application
            existing_app = existing_applications[0]
            doc_name = existing_app["name"]
            
            doc = frappe.get_doc("Onboarding Form", doc_name)
            
            # Update all form fields
            update_form_fields(doc, form_data)
            
            # Clear existing units and users before adding new ones
            doc.units = []
            doc.assigned_users = []
            
            # Add new units and users
            add_units_and_users(doc, form_data)
            
            doc.status = "Submitted"
            doc.current_step = 5
            
            doc.save()
            frappe.db.commit()
            
        else:
            # Create new application
            doc = frappe.get_doc({
                "doctype": "Onboarding Form",
                **form_data,
                "status": "Submitted",
                "current_step": 6
            })
            
            doc.insert()
            
            # Add units and users
            add_units_and_users(doc, form_data)
        
        # Send admin notification
        send_admin_notification(doc)
        
        return {
            "success": True,
            "message": "Onboarding form submitted successfully!",
            "application_id": doc.name
        }
        
    except Exception as e:
        frappe.log_error(f"Error submitting onboarding form: {str(e)}", "Climoro Onboarding Error")
        return {
            "success": False,
            "message": f"Error submitting form: {str(e)}"
        }


@frappe.whitelist(allow_guest=True)
def get_existing_application(email):
    """Get existing application by email"""
    try:
        if not email:
            return {
                "success": False,
                "message": "Email address is required"
            }
        
        applications = frappe.get_all(
            "Onboarding Form",
            filters={"email": email},
            fields=["name", "status", "current_step", "modified"],
            order_by="modified desc",
            limit=1
        )
        
        if applications:
            return {
                "success": True,
                "application": applications[0]
            }
        else:
            return {
                "success": False,
                "message": "No existing application found"
            }
            
    except Exception as e:
        frappe.log_error(f"Error getting existing application: {str(e)}", "Climoro Onboarding Error")
        return {
            "success": False,
            "message": f"Error retrieving application: {str(e)}"
        }


@frappe.whitelist(allow_guest=True)
def save_step_data(step_data):
    """Save step data to existing draft application"""
    try:
        # Handle JSON string data from frontend
        if isinstance(step_data, str):
            step_data = json.loads(step_data)
        
        # Validate required fields
        if not step_data.get("email"):
            return {
                "success": False,
                "message": "Email is required"
            }
        
        if not step_data.get("step_number"):
            return {
                "success": False,
                "message": "Step number is required"
            }
        
        email = step_data.get("email")
        step_number = step_data.get("step_number")
        
        # Find existing draft application
        existing_applications = frappe.get_all(
            "Onboarding Form",
            filters={"email": email, "status": "Draft"},
            fields=["name", "current_step"],
            order_by="modified desc",
            limit=1
        )
        
        if not existing_applications:
            return {
                "success": False,
                "message": "No draft application found. Please start from Step 1."
            }
        
        existing_app = existing_applications[0]
        doc_name = existing_app["name"]
        
        # Update the existing document
        doc = frappe.get_doc("Onboarding Form", doc_name)
        
        # Update fields based on step number
        update_step_fields(doc, step_data, step_number)
        
        # Save the document
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        
        return {
            "success": True,
            "message": f"Step {step_number} data saved successfully",
            "current_step": doc.current_step
        }
        
    except Exception as e:
        frappe.log_error(f"Error saving step data: {str(e)}")
        return {
            "success": False,
            "message": f"Error saving step data: {str(e)}"
        }


@frappe.whitelist(allow_guest=True)
def get_saved_data():
    """Get saved form data for the current session"""
    try:
        # Get session data
        session_data = frappe.get_session()
        if not session_data:
            return {
                "success": False,
                "message": "No session found"
            }
        
        # Get the email from session
        email = session_data.get('email')
        if not email:
            return {
                "success": False,
                "message": "No email found in session"
            }
        
        # Get all application fields in a single query
        applications = frappe.get_all(
            "Onboarding Form",
            filters={"email": email},
            fields=["*"],
            order_by="creation desc",
            limit=1
        )
        
        if applications:
            return {
                "success": True,
                "data": applications[0]
            }
        else:
            return {
                "success": True,
                "data": None
            }
            
    except Exception as e:
        frappe.log_error(f"Error getting saved data: {str(e)}")
        return {
            "success": False,
            "message": f"Error retrieving saved data: {str(e)}"
        }


def update_form_fields(doc, form_data):
    """Update form fields with data from frontend"""
    # Basic fields
    basic_fields = [
        "first_name", "middle_name", "last_name", "phone_number", "position",
        "company_name", "address", "gps_coordinates", "location_name", "cin",
        "gst_number", "industry_type", "sub_industry_type", "website", "letter_of_authorisation"
    ]
    
    for field in basic_fields:
        if field in form_data:
            setattr(doc, field, form_data[field])
    
    # GHG Accounting Fields (Step 4)
    ghg_fields = [
        "purpose_of_reporting", "gases_to_report_co2", "gases_to_report_ch4",
        "gases_to_report_n2o", "gases_to_report_hfcs", "gases_to_report_pfcs",
        "gases_to_report_sf6", "gases_to_report_nf3", "scopes_to_report_scope1",
        "scopes_to_report_scope2", "scopes_to_report_scope3", "scopes_to_report_reductions"
    ]
    
    for field in ghg_fields:
        if field in form_data:
            setattr(doc, field, form_data[field])
    
    # Step 5 fields
    step5_fields = [
        "base_year", "base_year_reason", "target_type", "monitoring_frequency",
        "assurance_validation", "method_of_calculation_option_a", "method_of_calculation_option_b",
        "method_of_calculation_option_c", "method_of_calculation_option_d", "method_of_calculation_option_e"
    ]
    
    for field in step5_fields:
        if field in form_data:
            setattr(doc, field, form_data[field])


def update_step_fields(doc, step_data, step_number):
    """Update fields based on step number"""
    if step_number == 1:
        # Step 1: Contact Details
        basic_fields = ["first_name", "middle_name", "last_name", "phone_number", "email", "position"]
        for field in basic_fields:
            if field in step_data:
                setattr(doc, field, step_data[field])
        doc.current_step = 1
        
    elif step_number == 2:
        # Step 2: Company Details
        company_fields = ["company_name", "address", "gps_coordinates", "location_name", "cin", 
                         "gst_number", "industry_type", "sub_industry_type", "website", "letter_of_authorisation"]
        for field in company_fields:
            if field in step_data:
                setattr(doc, field, step_data[field])
        doc.current_step = 2
        
    elif step_number == 3:
        # Step 3: Units & Users
        doc.units = []
        doc.assigned_users = []
        add_units_and_users(doc, step_data)
        doc.current_step = 3
        
    elif step_number == 4:
        # Step 4: GHG Accounting
        ghg_fields = [
            "purpose_of_reporting", "gases_to_report_co2", "gases_to_report_ch4",
            "gases_to_report_n2o", "gases_to_report_hfcs", "gases_to_report_pfcs",
            "gases_to_report_sf6", "gases_to_report_nf3", "scopes_to_report_scope1",
            "scopes_to_report_scope2", "scopes_to_report_scope3", "scopes_to_report_reductions"
        ]
        for field in ghg_fields:
            if field in step_data:
                setattr(doc, field, step_data[field])
        doc.current_step = 4
        
    elif step_number == 5:
        # Step 5: Reduction Form
        step5_fields = [
            "base_year", "base_year_reason", "target_type", "monitoring_frequency",
            "assurance_validation"
        ]
        for field in step5_fields:
            if field in step_data:
                setattr(doc, field, step_data[field])
        doc.current_step = 5
        
    elif step_number == 6:
        # Step 6: Method of Calculation
        calc_fields = [
            "method_of_calculation_option_a", "method_of_calculation_option_b",
            "method_of_calculation_option_c", "method_of_calculation_option_d",
            "method_of_calculation_option_e"
        ]
        for field in calc_fields:
            if field in step_data:
                setattr(doc, field, step_data[field])
        doc.current_step = 6


def add_units_and_users(doc, data):
    """Add units and assigned users to the document"""
    # Add units
    if data.get("units"):
        for unit_data in data["units"]:
            unit_doc = doc.append("units", {
                "type_of_unit": unit_data.get("type_of_unit"),
                "name_of_unit": unit_data.get("name_of_unit"),
                "size_of_unit": unit_data.get("size_of_unit"),
                "address": unit_data.get("address"),
                "gps_coordinates": unit_data.get("gps_coordinates"),
                "location_name": unit_data.get("location_name"),
                "gst": unit_data.get("gst"),
                "phone_number": unit_data.get("phone_number"),
                "position": unit_data.get("position")
            })
    
    # Add users
    if data.get("assigned_users"):
        for user_data in data["assigned_users"]:
            doc.append("assigned_users", {
                "assigned_unit": user_data.get("assigned_unit"),
                "email": user_data.get("email"),
                "first_name": user_data.get("first_name"),
                "user_role": user_data.get("user_role")
            })


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