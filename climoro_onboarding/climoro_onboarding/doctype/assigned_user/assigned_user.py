import frappe
from frappe.model.document import Document

class AssignedUser(Document):
    def validate(self):
        """Validate assigned user data"""
        self.validate_user_details()
    
    def validate_user_details(self):
        """Validate user details"""
        if self.email and not frappe.utils.validate_email_address(self.email):
            frappe.throw("Please enter a valid email address")
        
        if self.first_name and len(self.first_name.strip()) < 2:
            frappe.throw("First name must be at least 2 characters long")
        
        if self.user_role and self.user_role not in ["Admin", "Manager", "Employee", "Viewer"]:
            frappe.throw("Please select a valid user role") 