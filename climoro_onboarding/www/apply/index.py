import frappe
from frappe import _

def get_context(context):
    """Get context for the onboarding form page"""
    context.title = _("Climoro Onboarding Form")
    context.no_cache = 1
    context.no_sidebar = 1
    
    # Get any existing application for this user
    if frappe.session.user != "Guest":
        existing_apps = frappe.get_all("Onboarding Form", 
            filters={"email": frappe.session.user}, 
            fields=["name", "status", "current_step"])
        if existing_apps:
            context.existing_app = existing_apps[0]
    
    return context 