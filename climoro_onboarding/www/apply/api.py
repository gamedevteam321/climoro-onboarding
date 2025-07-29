import frappe
from frappe import _
from frappe.utils import now
import uuid
import json
import os
import datetime


@frappe.whitelist(allow_guest=True)
def submit_onboarding_form(form_data):
    """Submit the complete onboarding form"""
    try:
        # Handle JSON string data from frontend
        if isinstance(form_data, str):
            form_data = json.loads(form_data)
        
        # Debug logging for form data
        frappe.logger().info(f"🔍 Form Data Debug:")
        frappe.logger().info(f"   Form data keys: {list(form_data.keys())}")
        frappe.logger().info(f"   First name: '{form_data.get('first_name')}'")
        frappe.logger().info(f"   Middle name: '{form_data.get('middle_name')}'")
        frappe.logger().info(f"   Last name: '{form_data.get('last_name')}'")
        frappe.logger().info(f"   Last name type: {type(form_data.get('last_name'))}")
        frappe.logger().info(f"   Last name length: {len(form_data.get('last_name', ''))}")
        frappe.logger().info(f"   Phone number: '{form_data.get('phone_number')}'")
        frappe.logger().info(f"   Email: '{form_data.get('email')}'")
        frappe.logger().info(f"   Position: '{form_data.get('position')}'")
        
        # Check if last_name is empty and try to get it from saved data
        last_name = form_data.get('last_name')
        if not last_name or last_name.strip() == '':
            frappe.logger().info(f"⚠️ Last name is empty, trying to get from saved data")
            email = form_data.get("email")
            if email:
                # Try to get saved data for this email
                existing_applications = frappe.get_all(
                    "Onboarding Form",
                    filters={"email": email},
                    fields=["last_name"],
                    order_by="modified desc",
                    limit=1
                )
                if existing_applications and existing_applications[0].get('last_name'):
                    last_name = existing_applications[0].get('last_name')
                    frappe.logger().info(f"✅ Retrieved last_name from saved data: '{last_name}'")
                    form_data['last_name'] = last_name
                else:
                    frappe.logger().info(f"❌ No saved last_name found for email: {email}")
        
        # Debug logging for GPS coordinates
        frappe.logger().info(f"🔍 GPS Coordinates Debug:")
        frappe.logger().info(f"   GPS coordinates value: '{form_data.get('gps_coordinates')}'")
        frappe.logger().info(f"   GPS coordinates type: {type(form_data.get('gps_coordinates'))}")
        
        # Debug logging for industry fields
        frappe.logger().info(f"🔍 Industry Fields Debug:")
        frappe.logger().info(f"   Industry type: '{form_data.get('industry_type')}'")
        frappe.logger().info(f"   Sub-industry type: '{form_data.get('sub_industry_type')}'")
        frappe.logger().info(f"   All form_data keys: {list(form_data.keys())}")
        frappe.logger().info(f"   Form_data type: {type(form_data)}")
        
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
            
            frappe.logger().info(f"📝 Updating existing draft application: {doc_name}")
            
            # Update the existing document
            doc = frappe.get_doc("Onboarding Form", doc_name)
            
            # Update basic fields
            doc.first_name = form_data.get("first_name")
            doc.middle_name = form_data.get("middle_name")
            doc.last_name = form_data.get("last_name")
            doc.phone_number = form_data.get("phone_number")
            doc.position = form_data.get("position")
            doc.company_name = form_data.get("company_name")
            doc.address = form_data.get("address")
            doc.gps_coordinates = form_data.get("gps_coordinates")
            doc.location_name = form_data.get("location_name")
            frappe.logger().info(f"📍 Setting GPS coordinates on doc: '{form_data.get('gps_coordinates')}'")
            frappe.logger().info(f"📍 Setting location name on doc: '{form_data.get('location_name')}'")
            doc.cin = form_data.get("cin")
            doc.gst_number = form_data.get("gst_number")
            doc.industry_type = form_data.get("industry_type")
            doc.sub_industry_type = form_data.get("sub_industry_type")
            frappe.logger().info(f"🏭 Setting industry_type: '{form_data.get('industry_type')}'")
            frappe.logger().info(f"🏭 Setting sub_industry_type: '{form_data.get('sub_industry_type')}'")
            doc.website = form_data.get("website")
            doc.letter_of_authorisation = form_data.get("letter_of_authorisation")
            doc.status = "Submitted"
            doc.current_step = 3
            
            # Clear existing units and users
            doc.units = []
            
            # Add new units
            if form_data.get("units"):
                for unit_data in form_data["units"]:
                    # Debug logging for unit data
                    frappe.logger().info(f"🔍 Unit Data Debug:")
                    frappe.logger().info(f"   Unit name: {unit_data.get('name_of_unit')}")
                    frappe.logger().info(f"   GPS coordinates: {unit_data.get('gps_coordinates')}")
                    frappe.logger().info(f"   Location name: {unit_data.get('location_name')}")
                    # Create unit document
                    unit_doc = frappe.get_doc({
                        "doctype": "Company Unit",
                        "parent": doc.name,
                        "parenttype": "Onboarding Form",
                        "parentfield": "units",
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
                    
                    # Append the unit to the parent
                    doc.append("units", unit_doc)
            
            # Add new users
            if form_data.get("assigned_users"):
                for user_data in form_data["assigned_users"]:
                    # Debug logging for user data
                    frappe.logger().info(f"🔍 User Data Debug:")
                    frappe.logger().info(f"   User email: {user_data.get('email')}")
                    frappe.logger().info(f"   Assigned unit: {user_data.get('assigned_unit')}")
                    # Create user document
                    user_doc = frappe.get_doc({
                        "doctype": "Assigned User",
                        "parent": doc.name,
                        "parenttype": "Onboarding Form",
                        "parentfield": "assigned_users",
                        "assigned_unit": user_data.get("assigned_unit"),  # Store unit name directly
                        "email": user_data.get("email"),
                        "first_name": user_data.get("first_name"),
                        "user_role": user_data.get("user_role")
                    })
                    
                    # Append the user to the parent
                    doc.append("assigned_users", user_doc)
            
            doc.save()
            frappe.db.commit()
            
            frappe.logger().info(f"✅ Successfully updated existing application: {doc.name}")
            
        else:
            # Create new application if no draft exists
            frappe.logger().info(f"🆕 Creating new application for email: {email}")
            
            # Create the main onboarding form
            doc = frappe.get_doc({
                "doctype": "Onboarding Form",
                "first_name": form_data.get("first_name"),
                "middle_name": form_data.get("middle_name"),
                "last_name": form_data.get("last_name"),
                "phone_number": form_data.get("phone_number"),
                "email": form_data.get("email"),
                "position": form_data.get("position"),
                "company_name": form_data.get("company_name"),
                "address": form_data.get("address"),
                "gps_coordinates": form_data.get("gps_coordinates"),
                "location_name": form_data.get("location_name"),
                "cin": form_data.get("cin"),
                "gst_number": form_data.get("gst_number"),
                "industry_type": form_data.get("industry_type"),
                "sub_industry_type": form_data.get("sub_industry_type"),
                "website": form_data.get("website"),
                "letter_of_authorisation": form_data.get("letter_of_authorisation"),
                "status": "Submitted",
                "current_step": 3
            })
            
            frappe.logger().info(f"📍 Creating new doc with GPS coordinates: '{form_data.get('gps_coordinates')}'")
            doc.insert()
            
            # Add units
            if form_data.get("units"):
                for unit_data in form_data["units"]:
                    # Create unit as child table entry
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
            if form_data.get("assigned_users"):
                for user_data in form_data["assigned_users"]:
                    # Create the assigned user as a child table entry
                    doc.append("assigned_users", {
                        "assigned_unit": user_data.get("assigned_unit"),  # Store unit name directly
                        "email": user_data.get("email"),
                        "first_name": user_data.get("first_name"),
                        "user_role": user_data.get("user_role")
                    })
            
            frappe.logger().info(f"✅ Successfully created new application: {doc.name}")
        
        # Send admin notification
        doc.send_admin_notification()
        
        return {
            "success": True,
            "message": "Onboarding form submitted successfully!",
            "application_id": doc.name
        }
        
    except Exception as e:
        frappe.logger().error(f"❌ Error submitting onboarding form: {str(e)}")
        frappe.log_error(f"Error submitting onboarding form: {str(e)}", "Climoro Onboarding Error")
        return {
            "success": False,
            "message": f"Error submitting form: {str(e)}"
        }


@frappe.whitelist(allow_guest=True)
def get_existing_application(email):
    """Get existing application by email"""
    try:
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
        if step_number == 1:
            # Step 1: Contact Details
            doc.first_name = step_data.get("first_name")
            doc.middle_name = step_data.get("middle_name")
            doc.last_name = step_data.get("last_name")
            doc.phone_number = step_data.get("phone_number")
            doc.email = step_data.get("email")
            doc.position = step_data.get("position")
            doc.current_step = 1
            
        elif step_number == 2:
            # Step 2: Company Details
            doc.company_name = step_data.get("company_name")
            doc.address = step_data.get("address")
            doc.gps_coordinates = step_data.get("gps_coordinates")
            doc.location_name = step_data.get("location_name")
            frappe.logger().info(f"📍 Setting GPS coordinates on doc: '{step_data.get('gps_coordinates')}'")
            frappe.logger().info(f"📍 Setting location name on doc: '{step_data.get('location_name')}'")
            doc.cin = step_data.get("cin")
            doc.gst_number = step_data.get("gst_number")
            doc.industry_type = step_data.get("industry_type")
            doc.sub_industry_type = step_data.get("sub_industry_type")
            doc.website = step_data.get("website")
            doc.letter_of_authorisation = step_data.get("letter_of_authorisation")
            doc.current_step = 2
            
        elif step_number == 3:
            # Step 3: Units & Users
            # Clear existing units and users
            doc.units = []
            doc.assigned_users = []
            
            # Add new units
            if step_data.get("units"):
                for unit_data in step_data["units"]:
                    # Debug logging for unit data in step save
                    frappe.logger().info(f"🔍 Step Unit Data Debug:")
                    frappe.logger().info(f"   Unit name: {unit_data.get('name_of_unit')}")
                    frappe.logger().info(f"   GPS coordinates: {unit_data.get('gps_coordinates')}")
                    frappe.logger().info(f"   Location name: {unit_data.get('location_name')}")
                    # Create unit as child table entry
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
            
            # Add new users
            if step_data.get("assigned_users"):
                for user_data in step_data["assigned_users"]:
                    # Debug logging for user data in step save
                    frappe.logger().info(f"🔍 Step User Data Debug:")
                    frappe.logger().info(f"   User email: {user_data.get('email')}")
                    frappe.logger().info(f"   Assigned unit: {user_data.get('assigned_unit')}")
                    # Create user as child table entry
                    doc.append("assigned_users", {
                        "assigned_unit": user_data.get("assigned_unit"),
                        "email": user_data.get("email"),
                        "first_name": user_data.get("first_name"),
                        "user_role": user_data.get("user_role")
                    })
            
            doc.current_step = 3
        
        doc.save()
        frappe.db.commit()
        
        return {
            "success": True,
            "message": f"Step {step_number} data saved successfully",
            "application_id": doc.name
        }
        
    except Exception as e:
        frappe.logger().error(f"❌ Error saving step data: {str(e)}")
        frappe.log_error(f"Error saving step data: {str(e)}", "Climoro Onboarding Step Save Error")
        return {
            "success": False,
            "message": f"Error saving step data: {str(e)}"
        }


@frappe.whitelist(allow_guest=True)
def send_verification_email(email, data):
    """Send email verification after Step 1 completion"""
    try:
        if not email or not email.strip():
            return {"success": False, "message": "Email is required"}
        
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
        frappe.logger().info(f"🔍 verify_email called with token: {token}")
        
        if not token:
            frappe.logger().error("❌ No token provided")
            return {"success": False, "message": "Verification token is required"}
            
        session_key = f"climoro_onboarding_{token}"
        session_data_str = frappe.cache().get_value(session_key)
        
        frappe.logger().info(f"🔍 Session data from cache: {session_data_str}")
        
        if not session_data_str:
            frappe.logger().error("❌ No session data found for token")
            return {"success": False, "message": "Invalid or expired verification token"}
            
        session_data = json.loads(session_data_str)
        email = session_data.get("email")
        
        frappe.logger().info(f"📧 Email from session: {email}")
        frappe.logger().info(f"📋 Full session data: {session_data}")
        frappe.logger().info(f"📋 Session data keys: {list(session_data.keys())}")
        
        if "data" in session_data:
            frappe.logger().info(f"📋 Session data['data']: {session_data['data']}")
            frappe.logger().info(f"📋 Session data['data'] keys: {list(session_data['data'].keys()) if isinstance(session_data['data'], dict) else 'Not a dict'}")
        
        if not email:
            frappe.logger().error("❌ No email found in session data")
            return {"success": False, "message": "Email not found in session data"}
        
        # Mark as verified in session
        session_data["verified"] = True
        session_data["verified_at"] = now()
        
        frappe.logger().info(f"✅ Marked session as verified")
        
        # Update cache with verified status
        frappe.cache().set_value(session_key, json.dumps(session_data), expires_in_sec=86400)
        
        # Save/update the doctype with verified email data
        frappe.logger().info(f"💾 Calling save_verified_email_to_doctype")
        application_id = save_verified_email_to_doctype(email, session_data)
        
        frappe.logger().info(f"📋 Application ID returned: {application_id}")
        
        # Update session data with the application ID if we got one
        if application_id:
            session_data["application_id"] = application_id
            # Update cache with application ID
            frappe.cache().set_value(session_key, json.dumps(session_data), expires_in_sec=86400)
            frappe.logger().info(f"✅ Updated session with application ID: {application_id}")
        
        return {
            "success": True,
            "message": "Email verified successfully",
            "session_data": session_data,
            "email": email,
            "application_id": application_id
        }
        
    except Exception as e:
        frappe.logger().error(f"❌ Error in verify_email: {str(e)}")
        frappe.log_error(f"Error verifying email: {str(e)}", "Climoro Onboarding Verification Error")
        return {
            "success": False,
            "message": f"Error verifying email: {str(e)}"
        }


def save_verified_email_to_doctype(email, session_data):
    """Save or update doctype with verified email data"""
    try:
        # Debug logging to file (like franchise portal)
        debug_file = os.path.join(frappe.get_site_path(), 'debug_onboarding_verification.txt')
        with open(debug_file, 'a') as f:
            f.write(f"\n=== ENTER save_verified_email_to_doctype {frappe.utils.now()} ===\n")
            f.write(f"Email: {email}\n")
            f.write(f"Session data: {json.dumps(session_data)[:1000]}...\n")
        
        frappe.logger().info(f"🔍 save_verified_email_to_doctype called for email: {email}")
        frappe.logger().info(f"📋 Session data: {session_data}")
        
        # Check if application already exists for this email
        existing_applications = frappe.get_all(
            "Onboarding Form",
            filters={"email": email},
            fields=["name", "status"],
            limit=1
        )
        
        frappe.logger().info(f"🔍 Existing applications found: {existing_applications}")
        
        if existing_applications:
            # Update existing application
            existing_app = existing_applications[0]
            doc_name = existing_app["name"]
            
            frappe.logger().info(f"📝 Updating existing application: {doc_name}")
            
            # Update with verification status and basic fields
            updates = {
                "email_verified": 1,
                "email_verified_at": now(),
                "status": "Draft",
                "current_step": 1
            }
            
            # Add Step 1 data from session
            application_data = session_data.get("data", {})
            frappe.logger().info(f"📋 Application data from session: {application_data}")
            
            basic_fields = [
                "first_name", "middle_name", "last_name", "phone_number", "position"
            ]
            for field in basic_fields:
                if field in application_data and application_data[field]:
                    updates[field] = application_data[field]
                    frappe.logger().info(f"📝 Update {field} = {application_data[field]}")
                else:
                    frappe.logger().warning(f"⚠️ Missing or empty field for update: {field}")
            
            frappe.logger().info(f"📝 Updates to apply: {updates}")
            
            frappe.db.set_value("Onboarding Form", doc_name, updates)
            frappe.db.commit()
            
            frappe.logger().info(f"✅ Successfully updated existing application: {doc_name}")
            with open(debug_file, 'a') as f:
                f.write(f"✅ Updated existing application: {doc_name}\n")
            return doc_name
        else:
            # No existing application found - create new one
            frappe.logger().info(f"🆕 Creating new application for email: {email}")
            with open(debug_file, 'a') as f:
                f.write(f"🆕 Creating new application for email: {email}\n")
            
            try:
                doc = frappe.new_doc("Onboarding Form")
                doc.email = email
                doc.email_verified = 1
                doc.email_verified_at = now()
                doc.status = "Draft"
                doc.current_step = 1
                
                # Set naming series explicitly (like franchise portal)
                if not doc.naming_series:
                    doc.naming_series = "OF-.YYYY.-"
                
                # Add Step 1 data from session
                application_data = session_data.get("data", {})
                frappe.logger().info(f"📋 Application data from session: {application_data}")
                with open(debug_file, 'a') as f:
                    f.write(f"📋 Application data: {json.dumps(application_data)}\n")
                
                basic_fields = [
                    "first_name", "middle_name", "last_name", "phone_number", "position"
                ]
                for field in basic_fields:
                    if field in application_data and application_data[field]:
                        setattr(doc, field, application_data[field])
                        frappe.logger().info(f"📝 Set {field} = {application_data[field]}")
                        with open(debug_file, 'a') as f:
                            f.write(f"📝 Set {field} = {application_data[field]}\n")
                    else:
                        frappe.logger().warning(f"⚠️ Missing or empty field: {field}")
                        with open(debug_file, 'a') as f:
                            f.write(f"⚠️ Missing or empty field: {field}\n")
                
                frappe.logger().info(f"📝 Document fields set: email={doc.email}, verified={doc.email_verified}, status={doc.status}")
                frappe.logger().info(f"📝 Document first_name={getattr(doc, 'first_name', 'NOT SET')}")
                frappe.logger().info(f"📝 Document phone_number={getattr(doc, 'phone_number', 'NOT SET')}")
                
                # Use flag to prevent automatic email modification (like franchise portal)
                frappe.flags.ignore_email_uniqueness = True
                doc.insert(ignore_permissions=True)
                frappe.flags.ignore_email_uniqueness = False
                
                frappe.db.commit()
                
                frappe.logger().info(f"✅ Successfully created new application: {doc.name}")
                with open(debug_file, 'a') as f:
                    f.write(f"✅ Successfully created new application: {doc.name}\n")
                return doc.name
            except Exception as e:
                frappe.logger().error(f"❌ Exception during doc.insert: {str(e)}")
                frappe.log_error(f"Exception during doc.insert: {str(e)}", "Climoro Onboarding Doc Creation Error")
                with open(debug_file, 'a') as f:
                    f.write(f"❌ Exception during doc.insert: {str(e)}\n")
                return None
                
    except Exception as e:
        frappe.logger().error(f"❌ Error in save_verified_email_to_doctype: {str(e)}")
        frappe.log_error(f"Error saving verified email to doctype: {str(e)}", "Climoro Onboarding Doc Creation Error")
        debug_file = os.path.join(frappe.get_site_path(), 'debug_onboarding_verification.txt')
        with open(debug_file, 'a') as f:
            f.write(f"❌ Error in save_verified_email_to_doctype: {str(e)}\n")
        return None


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

# File Upload Functionality
@frappe.whitelist(allow_guest=True)
def upload_file():
    """Handle file uploads for onboarding form documents"""
    try:
        # Get uploaded file from request
        uploaded_file = frappe.request.files.get('file')
        field_name = frappe.form_dict.get('field_name')
        
        if not uploaded_file:
            return {"success": False, "message": "No file uploaded"}
        
        if not field_name:
            return {"success": False, "message": "Field name is required"}
        
        # Validate file size (25MB limit)
        max_size = 25 * 1024 * 1024  # 25MB in bytes
        file_size = len(uploaded_file.read())
        uploaded_file.seek(0)  # Reset file pointer
        
        if file_size > max_size:
            return {"success": False, "message": "File size exceeds 25MB limit"}
        
        # Validate file type
        allowed_extensions = ['.pdf', '.docx', '.doc', '.xlsx', '.xls', '.csv', '.jpg', '.jpeg', '.png', '.gif', '.bmp']
        filename = uploaded_file.filename
        file_extension = '.' + filename.split('.')[-1].lower()
        
        if file_extension not in allowed_extensions:
            return {"success": False, "message": "File type not supported"}
        
        # Create file document record in database using Frappe's proper file handling
        uploaded_file.seek(0)  # Reset file pointer
        file_content = uploaded_file.read()
        
        # Use Frappe's built-in file creation system
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": filename,
            "is_private": 1,
            "content": file_content
        })
        
        file_doc.insert(ignore_permissions=True)
        frappe.db.commit()
        
        # Use the file document's unique_url property which includes proper fid parameter
        # This ensures proper permission checking by Frappe
        site_url = frappe.utils.get_url()
        file_url = f"{site_url}{file_doc.unique_url}"
        
        return {
            "success": True,
            "message": "File uploaded successfully",
            "file_url": file_url,
            "file_name": filename,
            "file_size": file_size,
            "file_id": file_doc.name
        }
        
    except Exception as e:
        frappe.log_error(f"File upload error: {str(e)}", "Onboarding File Upload")
        return {"success": False, "message": f"Upload failed: {str(e)}"} 

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
        
        # Check if there's an existing application
        existing_applications = frappe.get_all(
            "Onboarding Form",
            filters={"email": email},
            fields=["name", "first_name", "middle_name", "last_name", "phone_number", "position", 
                   "company_name", "address", "gps_coordinates", "location_name", "cin", "gst_number", 
                   "industry_type", "website", "letter_of_authorisation"],
            order_by="creation desc",
            limit=1
        )
        
        if existing_applications:
            application = existing_applications[0]
            frappe.logger().info(f"Retrieved saved data for email: {email}")
            return {
                "success": True,
                "data": application
            }
        else:
            frappe.logger().info(f"No saved data found for email: {email}")
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