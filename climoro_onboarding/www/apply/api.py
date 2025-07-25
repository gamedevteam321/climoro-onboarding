import frappe
from frappe import _
import json

@frappe.whitelist(allow_guest=True)
def submit_onboarding_form(form_data):
    """Submit onboarding form data"""
    try:
        # Parse form data
        if isinstance(form_data, str):
            form_data = json.loads(form_data)
        
        # Create new Onboarding Form document
        doc = frappe.new_doc("Onboarding Form")
        
        # Set basic fields
        doc.first_name = form_data.get('first_name')
        doc.phone_number = form_data.get('phone_number')
        doc.email = form_data.get('email')
        doc.position = form_data.get('position')
        doc.company_name = form_data.get('company_name')
        doc.address = form_data.get('address')
        doc.cin = form_data.get('cin')
        doc.gst_number = form_data.get('gst_number')
        doc.industry_type = form_data.get('industry_type')
        doc.website = form_data.get('website')
        
        # Handle file upload
        if form_data.get('letter_of_authorisation'):
            # TODO: Implement file upload handling
            doc.letter_of_authorisation = form_data.get('letter_of_authorisation')
        
        # Set status and step
        doc.status = "Submitted"
        doc.current_step = 3
        
        # Insert the document
        doc.insert()
        
        # Add units and users
        if form_data.get('units'):
            for unit_data in form_data['units']:
                unit = doc.append('units', {})
                unit.type_of_unit = unit_data.get('type_of_unit')
                unit.name_of_unit = unit_data.get('name_of_unit')
                unit.size_of_unit = unit_data.get('size_of_unit')
                unit.address = unit_data.get('address')
                unit.gst = unit_data.get('gst')
                unit.phone_number = unit_data.get('phone_number')
                unit.position = unit_data.get('position')
                
                # Add users for this unit
                if unit_data.get('assigned_users'):
                    for user_data in unit_data['assigned_users']:
                        user = unit.append('assigned_users', {})
                        user.email = user_data.get('email')
                        user.first_name = user_data.get('first_name')
                        user.user_role = user_data.get('user_role')
        
        # Save the document
        doc.save()
        
        return {
            "success": True,
            "message": "Application submitted successfully!",
            "application_id": doc.name
        }
        
    except Exception as e:
        frappe.log_error(f"Onboarding form submission error: {str(e)}")
        return {
            "success": False,
            "message": f"Error submitting application: {str(e)}"
        }

@frappe.whitelist(allow_guest=True)
def get_existing_application(email):
    """Get existing application for an email"""
    try:
        existing_apps = frappe.get_all("Onboarding Form", 
            filters={"email": email}, 
            fields=["name", "status", "current_step", "first_name", "company_name"])
        
        if existing_apps:
            return {
                "success": True,
                "application": existing_apps[0]
            }
        else:
            return {
                "success": True,
                "application": None
            }
            
    except Exception as e:
        frappe.log_error(f"Error getting existing application: {str(e)}")
        return {
            "success": False,
            "message": f"Error retrieving application: {str(e)}"
        }

@frappe.whitelist(allow_guest=True)
def save_step_data(step_data):
    """Save data for a specific step"""
    try:
        # Parse step data
        if isinstance(step_data, str):
            step_data = json.loads(step_data)
        
        application_id = step_data.get('application_id')
        step = step_data.get('step')
        data = step_data.get('data')
        
        if application_id:
            # Update existing application
            doc = frappe.get_doc("Onboarding Form", application_id)
        else:
            # Create new application
            doc = frappe.new_doc("Onboarding Form")
        
        # Update fields based on step
        if step == 1:
            doc.first_name = data.get('first_name')
            doc.phone_number = data.get('phone_number')
            doc.email = data.get('email')
            doc.position = data.get('position')
        elif step == 2:
            doc.company_name = data.get('company_name')
            doc.address = data.get('address')
            doc.cin = data.get('cin')
            doc.gst_number = data.get('gst_number')
            doc.industry_type = data.get('industry_type')
            doc.website = data.get('website')
        
        doc.current_step = step
        doc.status = "In Progress"
        
        if application_id:
            doc.save()
        else:
            doc.insert()
        
        return {
            "success": True,
            "application_id": doc.name,
            "message": f"Step {step} data saved successfully"
        }
        
    except Exception as e:
        frappe.log_error(f"Error saving step data: {str(e)}")
        return {
            "success": False,
            "message": f"Error saving data: {str(e)}"
        } 