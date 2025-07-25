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
            # Remove any non-digit characters for validation
            digits_only = ''.join(filter(str.isdigit, self.phone_number))
            
            # Basic phone validation - allow 7-15 digits for international numbers
            if len(digits_only) < 7:
                frappe.throw("Phone number must be at least 7 digits")
            elif len(digits_only) > 15:
                frappe.throw("Phone number cannot exceed 15 digits")
    
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

    def approve_application(self, approver=None):
        """Approve the onboarding application, create company and users, send approval email, and update status"""
        self.status = "Approved"
        self.approved_at = datetime.now()
        self.approved_by = approver or frappe.session.user
        self.create_company_and_users()
        self.send_approval_email()
        self.save()
        frappe.db.commit()

    def reject_application(self, reason=None, approver=None):
        """Reject the onboarding application, send rejection email, and update status"""
        self.status = "Rejected"
        self.rejected_at = datetime.now()
        self.rejected_by = approver or frappe.session.user
        self.rejection_reason = reason or "No reason provided"
        self.send_rejection_email()
        self.save()
        frappe.db.commit()

    def create_company_and_users(self):
        """Create company and user records based on onboarding form data"""
        try:
            # Create company first
            company_name = self._create_company()
            
            # Create user for the form submitter (contact details from Step 1)
            self._create_main_user(company_name)
            
            # Create users for each assigned user in each unit
            self._create_unit_users(company_name)
            
            frappe.db.commit()
            
        except Exception as e:
            frappe.log_error(f"Error creating company and users: {str(e)}")
            frappe.throw(f"Error creating company and users: {str(e)}")

    def _create_company(self):
        """Create company from onboarding form data"""
        company_name = self.company_name
        
        # Check if company already exists
        if frappe.db.exists("Company", company_name):
            return company_name
        
        # Generate company abbreviation
        abbr = self._generate_company_abbr(company_name)
        
        # Create the company
        company_doc = frappe.get_doc({
            "doctype": "Company",
            "company_name": company_name,
            "abbr": abbr,
            "default_currency": "INR",
            "country": "India",
            "domain": "Manufacturing",
            "email": self.email,
            "phone_no": self.phone_number,
            "company_description": f"Company created from onboarding application {self.name}",
        })
        
        company_doc.insert(ignore_permissions=True)
        frappe.logger().info(f"Created company: {company_name}")
        return company_name

    def _create_main_user(self, company_name):
        """Create user for the form submitter with Super Admin role"""
        email = self.email
        
        # Check if user already exists
        if frappe.db.exists("User", email):
            user_doc = frappe.get_doc("User", email)
            
            # Add Super Admin role if not already present
            existing_roles = [role.role for role in user_doc.roles]
            if "Super Admin" not in existing_roles:
                user_doc.append("roles", {"role": "Super Admin"})
            
            # Assign the company to the user
            user_doc.company = company_name
            user_doc.save(ignore_permissions=True)
        else:
            # Create new user with Super Admin role
            first_name = self.first_name or email.split('@')[0]
            if ' ' in first_name:
                first_name = first_name.split(' ')[0]
            
            user_doc = frappe.get_doc({
                "doctype": "User",
                "email": email,
                "first_name": first_name,
                "company": company_name,
                "user_type": "System User",
                "send_welcome_email": 1,
                "enabled": 1,
                "roles": [
                    {"role": "Super Admin"},
                ]
            })
            user_doc.insert(ignore_permissions=True)
        
        # Create Employee record
        self._create_employee_record(email, company_name, "Super Admin")
        
        frappe.logger().info(f"Created main user: {email} with Super Admin role")
        return email

    def _create_unit_users(self, company_name):
        """Create users for each assigned user in each unit"""
        if not self.units:
            return
        
        for unit in self.units:
            if unit.assigned_users:
                for assigned_user in unit.assigned_users:
                    self._create_single_unit_user(assigned_user, company_name, unit)

    def _create_single_unit_user(self, assigned_user, company_name, unit):
        """Create a single user for an assigned user in a unit"""
        email = assigned_user.email
        user_role = assigned_user.user_role
        
        # Check if user already exists
        if frappe.db.exists("User", email):
            user_doc = frappe.get_doc("User", email)
            
            # Add the role if not already present
            existing_roles = [role.role for role in user_doc.roles]
            if user_role not in existing_roles:
                user_doc.append("roles", {"role": user_role})
            
            # Assign the company to the user
            user_doc.company = company_name
            user_doc.save(ignore_permissions=True)
        else:
            # Create new user with the specified role
            first_name = assigned_user.first_name or email.split('@')[0]
            if ' ' in first_name:
                first_name = first_name.split(' ')[0]
            
            user_doc = frappe.get_doc({
                "doctype": "User",
                "email": email,
                "first_name": first_name,
                "company": company_name,
                "user_type": "System User",
                "send_welcome_email": 1,
                "enabled": 1,
                "roles": [
                    {"role": user_role},
                ]
            })
            user_doc.insert(ignore_permissions=True)
        
        # Create Employee record
        self._create_employee_record(email, company_name, user_role, unit)
        
        frappe.logger().info(f"Created unit user: {email} with role {user_role}")

    def _create_employee_record(self, email, company_name, role, unit=None):
        """Create Employee record for user"""
        try:
            # Check if Employee record already exists for this user
            existing_employee = frappe.db.get_value("Employee", {"user_id": email}, "name")
            if existing_employee:
                frappe.logger().info(f"Employee record already exists for {email}: {existing_employee}")
                return existing_employee
            
            # Get user data
            if unit:
                # For unit users, use assigned user data
                first_name = unit.get("first_name", email.split('@')[0])
                designation = role
                department = "Operations"
            else:
                # For main user, use form data
                first_name = self.first_name or email.split('@')[0]
                designation = role
                department = "Management"
            
            # Create Employee record
            employee_doc = frappe.get_doc({
                "doctype": "Employee",
                "first_name": first_name,
                "employee_name": first_name,
                "date_of_joining": frappe.utils.today(),
                "company": company_name,
                "status": 'Active',
                "user_id": email,
                "personal_email": email,
                "company_email": email,
                "designation": designation,
                "department": department,
                "employee_number": frappe.generate_hash()[:8].upper(),
            })
            
            # Use flags to bypass validations that might cause issues
            employee_doc.flags.ignore_validate = True
            employee_doc.flags.ignore_links = True
            employee_doc.flags.ignore_permissions = True
            
            employee_doc.insert(ignore_permissions=True)
            frappe.logger().info(f"Created Employee record for {email}: {employee_doc.name}")
            
            return employee_doc.name
            
        except Exception as e:
            frappe.log_error(f"Failed to create Employee record for {email}: {str(e)}")
            return None

    def _generate_company_abbr(self, company_name):
        """Generate company abbreviation"""
        # Take first letter of each word, max 3 characters
        words = company_name.split()
        abbr = ''.join(word[0].upper() for word in words[:3])
        return abbr[:3] if abbr else company_name[:3].upper()

    def send_approval_email(self):
        """Send approval email to applicant"""
        try:
            # Get created users info for email
            created_users_info = self._get_created_users_info()
            
            frappe.sendmail(
                recipients=[self.email],
                subject=f"🎉 Climoro Onboarding Approved - {self.company_name}",
                message=f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #28a745;">🎉 Congratulations! Your Climoro Onboarding has been Approved!</h2>
                    
                    <p>Dear {self.first_name},</p>
                    
                    <p>We are pleased to inform you that your onboarding application has been <strong>approved</strong>!</p>
                    
                    <div style="background: #d4edda; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #28a745;">
                        <h3 style="margin-top: 0; color: #155724;">Application Details</h3>
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 8px 0; font-weight: bold; width: 40%;">Application ID:</td>
                                <td style="padding: 8px 0;">{self.name}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; font-weight: bold;">Company Created:</td>
                                <td style="padding: 8px 0;">{self.company_name}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; font-weight: bold;">Your Account:</td>
                                <td style="padding: 8px 0;">{self.email} (Super Admin)</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; font-weight: bold;">Units Created:</td>
                                <td style="padding: 8px 0;">{len(self.units) if self.units else 0}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; font-weight: bold;">Users Created:</td>
                                <td style="padding: 8px 0;">{created_users_info['total_users']}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; font-weight: bold;">Approved By:</td>
                                <td style="padding: 8px 0;">{frappe.get_value('User', self.approved_by, 'full_name') or self.approved_by}</td>
                            </tr>
                        </table>
                    </div>
                    
                    {created_users_info['users_details']}
                    
                    <h3>Next Steps:</h3>
                    <ol>
                        <li>You will receive a welcome email with login credentials</li>
                        <li>Access your Climoro dashboard</li>
                        <li>Complete the onboarding process</li>
                        <li>Start managing your units and users</li>
                    </ol>
                    
                    <p>Welcome to Climoro!</p>
                    
                    <p>Best regards,<br>Climoro Onboarding Team</p>
                </div>
                """,
                now=True
            )
            
            # Email to internal team
            frappe.sendmail(
                recipients=["admin@climoro.com"],
                subject=f"Climoro Onboarding Approved - {self.company_name}",
                message=f"""
                <h3>Climoro Onboarding Approved & Processed</h3>
                <p><strong>Application ID:</strong> {self.name}</p>
                <p><strong>Company Created:</strong> {self.company_name}</p>
                <p><strong>Main User Created:</strong> {self.email} (Super Admin)</p>
                <p><strong>Units Created:</strong> {len(self.units) if self.units else 0}</p>
                <p><strong>Total Users Created:</strong> {created_users_info['total_users']}</p>
                <p><strong>Approved By:</strong> {frappe.get_value('User', self.approved_by, 'full_name') or self.approved_by}</p>
                <p><strong>Contact Email:</strong> {self.email}</p>
                """,
                now=True
            )
        except Exception as e:
            frappe.log_error(f"Failed to send approval email: {str(e)}")

    def _get_created_users_info(self):
        """Get information about created users for email"""
        total_users = 1  # Main user
        users_details = ""
        
        if self.units:
            for unit in self.units:
                if unit.assigned_users:
                    total_users += len(unit.assigned_users)
                    users_details += f"<h4>Unit: {unit.name_of_unit}</h4><ul>"
                    for assigned_user in unit.assigned_users:
                        users_details += f"<li>{assigned_user.email} ({assigned_user.user_role})</li>"
                    users_details += "</ul>"
        
        if users_details:
            users_details = f"""
            <h3>Created Users:</h3>
            <h4>Main User:</h4>
            <ul><li>{self.email} (Super Admin)</li></ul>
            {users_details}
            """
        
        return {
            'total_users': total_users,
            'users_details': users_details
        }

    def send_rejection_email(self):
        """Send rejection email to applicant"""
        try:
            frappe.sendmail(
                recipients=[self.email],
                subject=f"Climoro Onboarding Rejected: {self.company_name}",
                message=f"""
                We regret to inform you that your onboarding application has been rejected.<br><br>
                Reason: {self.rejection_reason}<br>
                Company: {self.company_name}<br>
                Application ID: {self.name}<br>
                """
            )
        except Exception as e:
            frappe.log_error(f"Failed to send rejection email: {str(e)}") 