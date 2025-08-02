import frappe
from frappe import _
from frappe.utils import now_datetime
import json


@frappe.whitelist(allow_guest=True)
def verify_resume_token(token):
    """Verify resume token and return application data"""
    try:
        if not token:
            return {
                "success": False,
                "message": "Resume token is required"
            }
        
        session_key = f"climoro_resume_{token}"
        session_data_str = frappe.cache().get_value(session_key)
        
        if not session_data_str:
            return {
                "success": False,
                "message": "Invalid or expired resume token"
            }
        
        session_data = json.loads(session_data_str)
        
        # Check if token has expired
        expires_at = session_data.get("expires_at")
        if expires_at:
            from frappe.utils import get_datetime
            if get_datetime(expires_at) < now_datetime():
                frappe.cache().delete_value(session_key)
                return {
                    "success": False,
                    "message": "Resume token has expired. Please request a new one."
                }
        
        # Get the latest application data
        email = session_data.get("email")
        if email:
            applications = frappe.get_all(
                "Onboarding Form",
                filters={"email": email, "status": "Draft"},
                fields=["name", "current_step"],
                order_by="modified desc",
                limit=1
            )
            
            if applications:
                doc = frappe.get_doc("Onboarding Form", applications[0].name)
                # Convert doc to dict and handle datetime serialization
                doc_dict = doc.as_dict()
                
                # Convert datetime objects to strings recursively
                doc_dict = convert_datetime_to_string(doc_dict)
                session_data["application_data"] = doc_dict
                session_data["current_step"] = doc.current_step or 1
                
                # Refresh the cache with updated data
                try:
                    session_data_serializable = convert_datetime_to_string(session_data)
                    frappe.cache().set_value(session_key, json.dumps(session_data_serializable), expires_in_sec=86400)
                except Exception as cache_error:
                    frappe.log_error(f"Cache refresh error: {str(cache_error)}")
        
        return {
            "success": True,
            "message": "Resume token valid",
            "session_data": session_data,
            "current_step": session_data.get("current_step", 1)
        }
        
    except Exception as e:
        frappe.log_error(f"Error verifying resume token: {str(e)}")
        return {
            "success": False,
            "message": f"Error verifying resume token: {str(e)}"
        }


def convert_datetime_to_string(obj):
    """Convert datetime objects to strings recursively"""
    if obj is None:
        return None
    elif isinstance(obj, dict):
        return {key: convert_datetime_to_string(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_datetime_to_string(item) for item in obj]
    elif hasattr(obj, 'strftime'):  # Check if it's a datetime object
        try:
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return str(obj)
    elif hasattr(obj, 'isoformat'):  # Check if it's a date object
        try:
            return obj.isoformat()
        except:
            return str(obj)
    elif isinstance(obj, (int, float, str, bool)):
        return obj
    else:
        return str(obj)


@frappe.whitelist(allow_guest=True)
def debug_resume_token(token):
    """Debug function to check token status"""
    try:
        if not token:
            return {
                "success": False,
                "message": "Token is required"
            }
        
        session_key = f"climoro_resume_{token}"
        
        # Check if token exists in cache
        session_data_str = frappe.cache().get_value(session_key)
        
        debug_info = {
            "token": token,
            "session_key": session_key,
            "cache_exists": session_data_str is not None,
            "cache_data": session_data_str
        }
        
        if session_data_str:
            try:
                session_data = json.loads(session_data_str)
                debug_info["parsed_data"] = session_data
                debug_info["email"] = session_data.get("email")
                debug_info["current_step"] = session_data.get("current_step")
                debug_info["expires_at"] = session_data.get("expires_at")
                
                # Check if application exists in database
                if session_data.get("email"):
                    applications = frappe.get_all(
                        "Onboarding Form",
                        filters={"email": session_data["email"], "status": "Draft"},
                        fields=["name", "current_step", "company_name"],
                        order_by="modified desc",
                        limit=1
                    )
                    debug_info["database_applications"] = applications
                    debug_info["application_count"] = len(applications)
                
            except json.JSONDecodeError as e:
                debug_info["json_error"] = str(e)
        
        return {
            "success": True,
            "debug_info": debug_info
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Debug error: {str(e)}",
            "debug_info": {"error": str(e)}
        }


@frappe.whitelist(allow_guest=True)
def check_current_step_debug(application_id):
    """Debug function to check current step in database"""
    try:
        if not application_id:
            return {
                "success": False,
                "message": "Application ID is required"
            }
        
        doc = frappe.get_doc("Onboarding Form", application_id)
        
        return {
            "success": True,
            "application_id": application_id,
            "current_step": doc.current_step,
            "modified": str(doc.modified),
            "modified_by": doc.modified_by,
            "status": doc.status
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error checking current step: {str(e)}"
        }


@frappe.whitelist(allow_guest=True)
def update_current_step_debug(application_id, new_step):
    """Debug function to update current step in database"""
    try:
        if not application_id:
            return {
                "success": False,
                "message": "Application ID is required"
            }
        
        if not new_step:
            return {
                "success": False,
                "message": "New step is required"
            }
        
        doc = frappe.get_doc("Onboarding Form", application_id)
        old_step = doc.current_step
        doc.current_step = int(new_step)
        doc.save()
        
        return {
            "success": True,
            "application_id": application_id,
            "old_step": old_step,
            "new_step": doc.current_step,
            "message": f"Updated current step from {old_step} to {doc.current_step}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error updating current step: {str(e)}"
        } 