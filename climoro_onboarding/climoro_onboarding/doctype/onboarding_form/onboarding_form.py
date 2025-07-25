import frappe
from frappe.model.document import Document
from datetime import datetime

class OnboardingForm(Document):
    def before_insert(self):
        """Set creation timestamp"""
        self.created_at = datetime.now()
    
    def before_save(self):
        """Set modification timestamp"""
        self.modified_at = datetime.now()
    
    def validate(self):
        """Validate the application data"""
        self.validate_email()
        self.validate_phone()
        self.validate_company_details()
    
    def validate_email(self):
        """Validate email format"""
        if self.email and not frappe.utils.validate_email_address(self.email):
            frappe.throw("Please enter a valid email address")
    
    def validate_phone(self):
        """Validate phone number format"""
        if self.phone_number:
            # Basic phone validation - can be enhanced
            if len(self.phone_number) < 10:
                frappe.throw("Phone number must be at least 10 digits")
    
    def validate_company_details(self):
        """Validate company details"""
        if self.company_name and len(self.company_name.strip()) < 2:
            frappe.throw("Company name must be at least 2 characters long")
        
        if self.cin and len(self.cin.strip()) < 5:
            frappe.throw("CIN must be at least 5 characters long")
        
        if self.gst_number and len(self.gst_number.strip()) < 10:
            frappe.throw("GST Number must be at least 10 characters long")
    
    def on_submit(self):
        """Handle application submission"""
        self.status = "Submitted"
        self.send_admin_notification()
    
    def send_admin_notification(self):
        """Send notification to admin about new application"""
        try:
            frappe.sendmail(
                recipients=["admin@climoro.com"],
                subject=f"New Climoro Onboarding Form: {self.company_name}",
                message=f"""
                A new onboarding form has been submitted:
                
                Company: {self.company_name}
                Contact: {self.first_name}
                Email: {self.email}
                Phone: {self.phone_number}
                
                Application ID: {self.name}
                """
            )
        except Exception as e:
            frappe.log_error(f"Failed to send admin notification: {str(e)}") 