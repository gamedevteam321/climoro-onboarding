import frappe
from frappe import _
from frappe.utils import now
from frappe.model.document import Document
from datetime import datetime

class OnboardingForm(Document):
    def on_update(self):
        """Whenever the form is updated, if it's Approved, resync roles/visibility
        for users of this company so changes to scopes/sub-options take effect.
        """
        try:
            if getattr(self, "status", "") == "Approved" and getattr(self, "company_name", None):
                from climoro_onboarding.climoro_onboarding.ghg_workspace_access import assign_roles_for_company_based_on_onboarding
                assign_roles_for_company_based_on_onboarding(self.company_name)
        except Exception as e:
            frappe.log_error(f"Error syncing onboarding selection on update for {self.name}: {str(e)}")
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
        self.validate_sub_industry_type()
    
    def update_summary_fields(self):
        """Update the summary fields with current data"""
        try:
            # Calculate total units
            self.total_units = len(self.units) if self.units else 0
            
            # Calculate total users across all units
            total_users = 0
            units_summary_parts = []
            
            if self.units:
                for unit in self.units:
                    unit_users = len(unit.assigned_users) if unit.assigned_users else 0
                    total_users += unit_users
                    
                    # Create summary for this unit
                    unit_summary = f"{unit.name_of_unit} ({unit.type_of_unit})"
                    if unit_users > 0:
                        unit_summary += f" - {unit_users} users"
                    units_summary_parts.append(unit_summary)
            
            self.total_users = total_users
            
            # Create units summary text
            if units_summary_parts:
                self.units_summary = " | ".join(units_summary_parts)
            else:
                self.units_summary = "No units added"
                
        except Exception as e:
            frappe.log_error(f"Error updating summary fields: {str(e)}")
            # Set default values if calculation fails
            self.total_units = 0
            self.total_users = 0
            self.units_summary = "Error calculating summary"
    
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
    
    def validate_sub_industry_type(self):
        """Validate sub-industry type against the selected industry type"""
        if not self.sub_industry_type:
            return  # Allow empty sub-industry type
        
        if not self.industry_type:
            frappe.throw("Industry Type must be selected before selecting Sub-Industry Type")
        
        # Get valid sub-industry options for the selected industry type
        valid_options = get_sub_industry_options(self.industry_type)
        
        # Debug logging
        frappe.logger().info(f"🔍 Sub-Industry Validation Debug:")
        frappe.logger().info(f"   Industry Type: '{self.industry_type}'")
        frappe.logger().info(f"   Sub-Industry Type: '{self.sub_industry_type}'")
        frappe.logger().info(f"   Valid Options: {valid_options}")
        frappe.logger().info(f"   Is Valid: {self.sub_industry_type in valid_options}")
        
        if self.sub_industry_type not in valid_options:
            frappe.throw(f"Sub-Industry Type '{self.sub_industry_type}' is not valid for Industry Type '{self.industry_type}'. Please select a valid option.")
    
    def on_submit(self):
        """Handle application submission"""
        self.status = "Submitted"
        self.send_admin_notification()
    
    def send_admin_notification(self):
        """Send notification to admin about new submission"""
        try:
            # Create notification for admin
            notification = frappe.get_doc({
                "doctype": "Notification Log",
                "subject": f"New Onboarding Application: {self.company_name}",
                "for_user": "Administrator",
                "type": "Mention",
                "document_type": "Onboarding Form",
                "document_name": self.name
            })
            notification.insert(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(f"Error sending admin notification: {str(e)}")

    def approve_application(self, approver=None):
        """Approve the onboarding application, create company and users, send approval email, and update status"""
        self.status = "Approved"
        self.approved_at = datetime.now()
        self.approved_by = approver or frappe.session.user
        self.create_company_and_users()
        # Assign GHG workspace roles to all company users based on selections
        try:
            from climoro_onboarding.climoro_onboarding.ghg_workspace_access import assign_roles_for_company_based_on_onboarding
            assign_roles_for_company_based_on_onboarding(self.company_name)
        except Exception as e:
            frappe.log_error(f"Error assigning GHG workspace roles: {str(e)}")
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
            
            # Block all modules for existing user
            self._block_all_modules_for_user(user_doc)
            
            user_doc.save(ignore_permissions=True)
        else:
            # Create new user with Super Admin role
            # Use the first_name from form, or generate a proper name from email
            if self.first_name and self.first_name.strip():
                first_name = self.first_name.strip()
                # Take only the first part if it contains spaces
                if ' ' in first_name:
                    first_name = first_name.split(' ')[0]
            else:
                # Generate a proper name from email prefix
                email_prefix = email.split('@')[0]
                # Convert to title case and replace common prefixes
                first_name = email_prefix.replace('_', ' ').replace('-', ' ').title()
                # Take only the first part if it contains spaces
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
            
            # Block all modules for new user
            self._block_all_modules_for_user(user_doc)
            
            user_doc.insert(ignore_permissions=True)
        
        frappe.logger().info(f"Created main user: {email} with Super Admin role (all modules blocked)")
        return email

    def _create_unit_users(self, company_name):
        """Create users for each assigned user in each unit"""
        if not self.assigned_users:
            return
        
        for assigned_user in self.assigned_users:
            # Find the corresponding unit for this assigned user
            unit_name = assigned_user.assigned_unit
            unit = None
            
            # Find the unit by name
            if self.units:
                for u in self.units:
                    if u.name_of_unit == unit_name:
                        unit = u
                        break
            
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
            
            # Block all modules for existing user
            self._block_all_modules_for_user(user_doc)
            
            user_doc.save(ignore_permissions=True)
        else:
            # Create new user with the specified role
            # Use the first_name from assigned_user, or generate a proper name from email
            if assigned_user.first_name and assigned_user.first_name.strip():
                first_name = assigned_user.first_name.strip()
                # Take only the first part if it contains spaces
                if ' ' in first_name:
                    first_name = first_name.split(' ')[0]
            else:
                # Generate a proper name from email prefix
                email_prefix = email.split('@')[0]
                # Convert to title case and replace common prefixes
                first_name = email_prefix.replace('_', ' ').replace('-', ' ').title()
                # Take only the first part if it contains spaces
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
            
            # Block all modules for new user
            self._block_all_modules_for_user(user_doc)
            
            user_doc.insert(ignore_permissions=True)
        
        frappe.logger().info(f"Created unit user: {email} with role {user_role} (all modules blocked)")

    def _block_all_modules_for_user(self, user_doc):
        """Block all available modules for a user"""
        try:
            # Get all available modules from the system
            from frappe.config import get_modules_from_all_apps
            all_modules = get_modules_from_all_apps()
            
            # Clear existing blocked modules
            user_doc.set("block_modules", [])
            
            # Add all modules to blocked modules
            for module_data in all_modules:
                module_name = module_data.get("module_name")
                if module_name:
                    user_doc.append("block_modules", {"module": module_name})
            
            frappe.logger().info(f"Blocked {len(all_modules)} modules for user {user_doc.email}")
            
        except Exception as e:
            frappe.log_error(f"Error blocking modules for user {user_doc.email}: {str(e)}")
            # Continue with user creation even if module blocking fails

    def _generate_company_abbr(self, company_name):
        """Generate unique company abbreviation"""
        # Take first letter of each word, max 3 characters
        words = company_name.split()
        base_abbr = ''.join(word[0].upper() for word in words[:3])
        base_abbr = base_abbr[:3] if base_abbr else company_name[:3].upper()
        
        # Ensure we have at least something
        if not base_abbr:
            base_abbr = "COM"
        
        # Check if base abbreviation is available
        if not frappe.db.exists("Company", {"abbr": base_abbr}):
            return base_abbr
        
        # If base abbreviation exists, try variations with numbers
        counter = 1
        while counter <= 99:  # Limit to prevent infinite loop
            variant_abbr = f"{base_abbr[:2]}{counter}"  # Keep first 2 chars + number
            if not frappe.db.exists("Company", {"abbr": variant_abbr}):
                return variant_abbr
            counter += 1
        
        # If all variations from 1-99 are taken, try different approach
        # Use first 2 characters + random suffix
        import random
        import string
        for _ in range(10):  # Try 10 random combinations
            random_suffix = random.choice(string.ascii_uppercase)
            variant_abbr = f"{base_abbr[:2]}{random_suffix}"
            if not frappe.db.exists("Company", {"abbr": variant_abbr}):
                return variant_abbr
        
        # Last resort: use timestamp-based suffix
        from frappe.utils import now_datetime
        timestamp_suffix = str(now_datetime().microsecond)[-2:]
        return f"{base_abbr[:1]}{timestamp_suffix}"

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
        
        if self.assigned_users:
            total_users += len(self.assigned_users)
            
            # Group users by unit
            unit_users = {}
            for assigned_user in self.assigned_users:
                unit_name = assigned_user.assigned_unit
                if unit_name not in unit_users:
                    unit_users[unit_name] = []
                unit_users[unit_name].append(assigned_user)
            
            # Create details for each unit
            for unit_name, users in unit_users.items():
                users_details += f"<h4>Unit: {unit_name}</h4><ul>"
                for assigned_user in users:
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

    def get_units_count(self):
        """Get the number of units in this onboarding form"""
        return len(self.units) if self.units else 0
    
    def get_users_count(self):
        """Get the total number of users (main user + all unit users)"""
        total_users = 1  # Main user (form submitter)
        
        if self.assigned_users:
            total_users += len(self.assigned_users)
        
        return total_users
    
    def get_units_summary(self):
        """Get a summary of all units and their users"""
        summary = []
        
        if self.units:
            for unit in self.units:
                unit_info = {
                    'name': unit.name_of_unit,
                    'type': unit.type_of_unit,
                    'size': unit.size_of_unit,
                    'address': unit.address,
                    'users_count': 0,
                    'users': []
                }
                
                if hasattr(unit, 'assigned_users') and unit.assigned_users:
                    unit_info['users_count'] = len(unit.assigned_users)
                    for user in unit.assigned_users:
                        unit_info['users'].append({
                            'email': user.email,
                            'first_name': user.first_name,
                            'role': user.user_role
                        })
                
                summary.append(unit_info)
        
        return summary

@frappe.whitelist()
def refresh_all_summaries():
    """Refresh summary fields for all Onboarding Form documents"""
    try:
        forms = frappe.get_all("Onboarding Form", fields=["name"])
        updated_count = 0
        
        for form in forms:
            try:
                doc = frappe.get_doc("Onboarding Form", form.name)
                # Removed update_summary_fields() call
                doc.save(ignore_permissions=True)
                updated_count += 1
            except Exception as e:
                frappe.log_error(f"Error updating summary for {form.name}: {str(e)}")
        
        frappe.db.commit()
        return f"Updated {updated_count} forms"
        
    except Exception as e:
        frappe.log_error(f"Error in refresh_all_summaries: {str(e)}")
        return f"Error: {str(e)}"

@frappe.whitelist()
def approve_application(docname):
    """Approve the onboarding application"""
    try:
        print(f"=== DEBUG: Starting approval for {docname} ===")
        doc = frappe.get_doc("Onboarding Form", docname)
        print(f"=== DEBUG: Current status before approval: {doc.status} ===")
        doc.approve_application()
        print(f"=== DEBUG: Status after approval: {doc.status} ===")
        return {"success": True, "message": "Application approved successfully"}
    except Exception as e:
        print(f"=== DEBUG: Error in approval: {str(e)} ===")
        frappe.log_error(f"Error approving application {docname}: {str(e)}")
        return {"success": False, "message": str(e)}

@frappe.whitelist()
def reject_application(docname, reason=None):
    """Reject the onboarding application"""
    try:
        doc = frappe.get_doc("Onboarding Form", docname)
        doc.reject_application(reason=reason)
        return {"success": True, "message": "Application rejected successfully"}
    except Exception as e:
        frappe.log_error(f"Error rejecting application {docname}: {str(e)}")
        return {"success": False, "message": str(e)}

@frappe.whitelist()
def get_sub_industry_options(industry_type):
    """Get sub-industry options based on selected industry type"""
    
    industry_sub_types = {
        "Energy": [
            "Oil & Gas Extraction",
            "Oil Refining",
            "Natural Gas Transmission & Distribution",
            "Coal Mining & Processing",
            "Renewable Energy (Solar, Wind, Hydro, etc.)",
            "Power Generation (Thermal)",
            "Transmission & Distribution (Electric Utilities)"
        ],
        "Manufacturing": [
            "Cement & Lime Production",
            "Iron & Steel",
            "Aluminum",
            "Chemicals & Fertilizers",
            "Glass & Ceramics",
            "Paper & Pulp",
            "Food & Beverage",
            "Textiles & Apparel",
            "Plastics & Rubber",
            "Electronics & Electrical Equipment",
            "Machinery & Tools",
            "Automobile & Parts Manufacturing"
        ],
        "Construction": [
            "Commercial Construction",
            "Residential Construction",
            "Infrastructure (Roads, Bridges, etc.)",
            "Cement/Concrete On-site Mixing",
            "Demolition & Waste Handling"
        ],
        "Transportation & Logistics": [
            "Freight (Road, Rail, Air, Sea)",
            "Passenger Transport (Buses, Airlines, Rail)",
            "Warehousing & Distribution",
            "Shipping & Port Operations",
            "Courier & Postal Services"
        ],
        "Retail & Consumer Goods": [
            "Fashion & Apparel",
            "Food Retail & Supermarkets",
            "Electronics & Appliances",
            "E-commerce",
            "Department Stores"
        ],
        "Chemical & Petrochemical": [
            "Basic Chemicals",
            "Specialty Chemicals",
            "Agrochemicals",
            "Petrochemical Derivatives",
            "Pharmaceuticals"
        ],
        "Financial & Insurance Services": [
            "Banks & Lending Institutions",
            "Investment Firms",
            "Insurance",
            "Asset Management",
            "Fintech"
        ],
        "Real Estate & Property Management": [
            "Commercial Real Estate",
            "Residential Real Estate",
            "Property Development",
            "Facility Management"
        ],
        "Services": [
            "IT & Data Centers",
            "Hospitality (Hotels, Resorts)",
            "Education (Universities, Schools)",
            "Healthcare (Hospitals, Clinics)",
            "Professional Services (Legal, Consulting)"
        ],
        "Agriculture, Forestry & Land Use": [
            "Crop Cultivation",
            "Livestock (Cattle, Poultry, etc.)",
            "Dairy Farming",
            "Aquaculture",
            "Agroforestry",
            "Timber & Logging",
            "Land Restoration"
        ],
        "Waste Management": [
            "Solid Waste Collection",
            "Landfilling",
            "Waste-to-Energy",
            "Composting",
            "Wastewater Treatment",
            "Recycling Operations"
        ],
        "Water Supply & Treatment": [
            "Water Utilities",
            "Desalination Plants",
            "Irrigation Systems",
            "Stormwater Management"
        ],
        "Telecommunications": [
            "Data Transmission Services",
            "Mobile Network Operations",
            "Satellite Communications",
            "Cable & Broadcasting"
        ],
        "Government & Public Administration": [
            "Defense & Military Operations",
            "Municipal Services",
            "Urban Planning",
            "Public Infrastructure"
        ],
        "Aviation & Aerospace": [
            "Commercial Airlines",
            "Private Aviation",
            "Aircraft Manufacturing",
            "Airport Operations"
        ],
        "Mining & Quarrying": [
            "Metal Ore Mining",
            "Non-metallic Mineral Extraction",
            "Rare Earth Elements",
            "Quarry Operations"
        ],
        "Fossil Fuel Supply Chain": [
            "Exploration & Production",
            "Midstream (Pipelines, Storage)",
            "Downstream (Retail Fuel, Gas Stations)"
        ],
        "Fisheries & Marine": [
            "Industrial Fishing",
            "Aquaculture",
            "Seafood Processing",
            "Marine Transport"
        ],
        "Media, Entertainment & Culture": [
            "Streaming Services",
            "Publishing",
            "Events & Exhibitions",
            "Film Production"
        ],
        "Carbon Market & Climate Services": [
            "Project Developers (RE, Cookstoves, AFOLU)",
            "MRV Providers",
            "Carbon Credit Traders & Registries",
            "Environmental Consulting"
        ]
    }
    
    if industry_type and industry_type in industry_sub_types:
        return industry_sub_types[industry_type]
    else:
        return []

@frappe.whitelist(allow_guest=True)
def get_google_maps_api_key():
    """Get Google Maps API key from site configuration"""
    try:
        api_key = frappe.conf.get('google_maps_api_key')
        if not api_key:
            # Try to get from common site config
            api_key = frappe.get_site_config().get('google_maps_api_key')
        
        if api_key:
            return {"success": True, "api_key": api_key}
        else:
            return {"success": False, "message": "Google Maps API key not configured"}
    except Exception as e:
        frappe.log_error(f"Error getting Google Maps API key: {str(e)}")
        return {"success": False, "message": f"Error: {str(e)}"} 