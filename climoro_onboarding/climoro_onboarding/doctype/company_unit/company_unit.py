import frappe
from frappe.model.document import Document

class CompanyUnit(Document):
    def validate(self):
        """Validate company unit data"""
        self.validate_unit_details()
        self.validate_assigned_users()
    
    def validate_unit_details(self):
        """Validate unit details"""
        if self.name_of_unit and len(self.name_of_unit.strip()) < 2:
            frappe.throw("Unit name must be at least 2 characters long")
        
        if self.size_of_unit and self.size_of_unit <= 0:
            frappe.throw("Unit size must be greater than 0")
        
        if self.address and len(self.address.strip()) < 10:
            frappe.throw("Address must be at least 10 characters long")
    
    def validate_assigned_users(self):
        """Validate assigned users in this unit"""
        if hasattr(self, 'assigned_users') and self.assigned_users:
            for user in self.assigned_users:
                if user.email and not frappe.utils.validate_email_address(user.email):
                    frappe.throw(f"Invalid email address for user in unit {self.name_of_unit}")
                
                if user.first_name and len(user.first_name.strip()) < 2:
                    frappe.throw(f"First name must be at least 2 characters for user in unit {self.name_of_unit}") 