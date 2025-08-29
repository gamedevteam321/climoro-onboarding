# Copyright (c) 2024, Climoro Onboarding and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import validate_email_address
import secrets
import string

class UnitUsers(Document):
	def validate(self):
		# Validate email format
		if self.email:
			validate_email_address(self.email)
		
		# Validate unit belongs to same company
		if self.assigned_unit:
			self.validate_unit_company()

	
	def validate_unit_company(self):
		"""Ensure assigned unit belongs to the same company"""
		unit_company = frappe.db.get_value("Units", self.assigned_unit, "company")
		if unit_company and unit_company != self.company:
			frappe.throw(f"Unit {self.assigned_unit} belongs to {unit_company}, not {self.company}")
	
	def validate_user_creation_permissions(self):
		"""Only super admins can create user accounts"""
		if not frappe.session.user or frappe.session.user == "Administrator":
			return
		
		user_roles = frappe.get_roles(frappe.session.user)
		super_admin_roles = ["System Manager", "Administrator"]
		
		if not any(role in super_admin_roles for role in user_roles):
			frappe.throw("Only System Managers and Administrators can create user accounts")
	
	def validate_user_creation_fields(self):
		"""Validate fields needed to auto-create User (no password required)"""
		if not self.username:
			# Generate a username if not provided
			self.username = generate_username(self.first_name or "user", self.email)
		
		# Ensure email is unique for User
		if frappe.db.exists("User", self.email):
			frappe.throw(f"User with email '{self.email}' already exists")
	
	def validate_password_strength(self):
		"""Validate password meets Frappe's strength requirements"""
		password = self.password
		
		if len(password) < 8:
			frappe.throw("Password must be at least 8 characters long")
		
		# Check for repeating patterns
		if len(set(password)) < 4:
			frappe.throw("Password must contain at least 4 different characters")
		
		# Check for simple repetitions
		for i in range(len(password) - 2):
			if password[i] == password[i+1] == password[i+2]:
				frappe.throw("Password should not contain repeated characters (like 'aaa')")
		
		# Check for basic patterns
		if password.lower() in ['password', '12345678', 'abcdefgh', 'qwertyui']:
			frappe.throw("Password is too common. Please use a stronger password")
		
		# Check for character variety
		has_upper = any(c.isupper() for c in password)
		has_lower = any(c.islower() for c in password)
		has_digit = any(c.isdigit() for c in password)
		has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
		
		variety_count = sum([has_upper, has_lower, has_digit, has_special])
		if variety_count < 3:
			frappe.throw("Password must contain at least 3 of the following: uppercase letters, lowercase letters, numbers, special characters")
	
	def test_password_against_frappe_rules(self):
		"""Test password against Frappe's internal validation without creating user"""
		try:
			# Import Frappe's password testing function
			from frappe.core.doctype.user.user import test_password_strength
			
			# Test the password
			result = test_password_strength(self.password)
			
			# If result contains feedback, the password failed
			if result and result.get('feedback'):
				feedback = result['feedback']
				if 'warning' in feedback:
					warning = feedback['warning']
					if 'repeats like' in warning.lower() or 'repeated' in warning.lower():
						frappe.throw("Password contains repeating patterns. Please use the 'Generate Password' button or create a stronger password with mixed characters.")
					else:
						frappe.throw(f"Password validation failed: {warning}")
				
		except ImportError:
			# Fallback to our own validation if Frappe function not available
			self.validate_password_strength()
		except Exception as e:
			# If the test itself fails, use our validation
			self.validate_password_strength()
	
	def before_insert(self):
		# Set company from assigned unit if not set
		if self.assigned_unit and not self.company:
			self.company = frappe.db.get_value("Units", self.assigned_unit, "company")
		
		# Setup company permissions
		self.setup_company_permissions()
	
	def after_insert(self):
		# Always create a user automatically on save if not created
		if not self.user_created:
			self.create_frappe_user()
	
	def setup_company_permissions(self):
		"""Setup role-based company filtering for non-super admin users"""
		if not frappe.session.user or frappe.session.user == "Administrator":
			return
		
		# Check if user has super admin roles
		user_roles = frappe.get_roles(frappe.session.user)
		super_admin_roles = ["System Manager", "Administrator"]
		
		if not any(role in super_admin_roles for role in user_roles):
			# For non-super admin users, restrict to their company
			user_company = frappe.db.get_value("User", frappe.session.user, "company")
			if user_company and not self.company:
				self.company = user_company
			elif self.company and self.company != user_company:
				frappe.throw(f"You can only create unit users for your company: {user_company}")
	
	def create_frappe_user(self):
		"""Create a Frappe user account without password and send welcome email"""
		try:
			frappe.logger().info(f"[Unit Users] Creating user for {self.email} with role '{self.user_role}'")
			# Create user document without setting password
			user_doc = frappe.get_doc({
				"doctype": "User",
				"email": self.email,
				"username": self.username,
				"first_name": self.first_name,
				"enabled": 1,
				"user_type": "System User",
				"send_welcome_email": 1
			})
			
			# Set company field directly
			current_user_company = self.get_current_user_company()
			if current_user_company:
				user_doc.company = current_user_company
			
			# Insert the user
			user_doc.insert(ignore_permissions=True)
			
			# Assign role based on user_role field
			self.assign_user_role(user_doc.name)
			# Verify base role assignment and enforce if missing
			self._verify_and_enforce_base_roles(user_doc.name)
			# Also assign scope/reduction roles same as super admin template
			self.assign_scope_reduction_roles_from_super_admin(user_doc.name)
			# Final verification after all assignments
			self._verify_and_enforce_base_roles(user_doc.name)
			# Ensure the writes are persisted immediately
			try:
				frappe.db.commit()
			except Exception:
				pass
			
			# Create user permissions after user is created
			if current_user_company:
				self.create_user_permissions(user_doc.name, current_user_company)
			
			# Update this document
			self.db_set("user_created", 1)
			self.db_set("frappe_user_id", user_doc.name)
			
			# Send welcome email (system built-in will trigger reset)
			try:
				frappe.sendmail(
					recipients=[self.email],
					subject=f"Welcome to {frappe.db.get_value('Company', self.company, 'company_name') or 'our platform'}",
					message=f"Hello {self.first_name}, your account has been created. Please set your password using the 'Forgot Password' link on the login page: {frappe.utils.get_url()}"
				)
			except Exception:
				pass
			
			frappe.msgprint(f"User account created successfully for {self.first_name} ({self.email})")
			
		except frappe.ValidationError as e:
			frappe.throw(str(e))
		except Exception as e:
			# Shorter error message to avoid title length issues
			short_error = str(e)[:100] + "..." if len(str(e)) > 100 else str(e)
			frappe.throw(f"Failed to create user account: {short_error}")

	def _verify_and_enforce_base_roles(self, user_email: str) -> None:
		"""Ensure the chosen base role and Employee exist for the user; log state."""
		try:
			selected_raw = (self.user_role or "").strip()
			desired = []
			if selected_raw.lower().find("manager") != -1:
				desired.append("Unit Manager")
			elif selected_raw.lower().find("analyst") != -1:
				desired.append("Data Analyst")
			# Always include Employee
			desired.append("Employee")
			for role in desired:
				if not frappe.db.exists("Role", role):
					self.create_custom_role(role)
				if not frappe.db.exists("Has Role", {"parent": user_email, "role": role}):
					frappe.get_doc({
						"doctype": "Has Role",
						"parent": user_email,
						"parenttype": "User",
						"parentfield": "roles",
						"role": role,
					}).insert(ignore_permissions=True)
			# Log final role set for diagnostics
			assigned = [r.role for r in frappe.get_all("Has Role", fields=["role"], filters={"parent": user_email})]
			try:
				frappe.log_error(
					message=f"Final roles for {user_email}: {assigned} (selected={selected_raw})",
					title="Unit Users Role Assignment"
				)
			except Exception:
				pass
		except Exception:
			pass
	
	def get_current_user_company(self):
		"""Get the company of the current super admin creating this user"""
		if frappe.session.user == "Administrator":
			return self.company
		
		# For super admins, restrict users to their own company
		user_company = frappe.db.get_value("User", frappe.session.user, "company")
		return user_company or self.company
	
	def create_user_permissions(self, user_email, company):
		"""Create user permissions for company restriction"""
		try:
			# Check if User Permission already exists
			if not frappe.db.exists("User Permission", {
				"user": user_email,
				"allow": "Company",
				"for_value": company
			}):
				# Create User Permission
				user_perm = frappe.get_doc({
					"doctype": "User Permission",
					"user": user_email,
					"allow": "Company", 
					"for_value": company,
					"is_default": 1
				})
				user_perm.insert(ignore_permissions=True)
				print(f"✅ Created user permission for {user_email} on company {company}")
		except Exception as e:
			print(f"⚠️ Could not create user permission: {str(e)}")
			# Don't fail user creation if permissions fail
	
	def assign_user_role(self, user_email):
		"""Assign appropriate role based on user_role field (robust mapping)

		Uses Frappe's built-in add_roles API for reliability and idempotency.
		"""
		role_mapping = {
			"unit manager": ["Unit Manager", "Employee"],
			"data analyst": ["Data Analyst", "Employee"],
		}
		selected_raw = (self.user_role or "").strip()
		selected_key = selected_raw.lower()
		roles_to_assign = role_mapping.get(selected_key)
		if not roles_to_assign:
			# Heuristic fallback if label mismatches
			if "manager" in selected_key:
				roles_to_assign = ["Unit Manager", "Employee"]
			elif "analyst" in selected_key:
				roles_to_assign = ["Data Analyst", "Employee"]
			else:
				roles_to_assign = ["Employee"]
			# log for troubleshooting
			try:
				frappe.log_error(f"Unexpected user_role value: '{selected_raw}'", "Unit Users Role Mapping")
			except Exception:
				pass

		# Ensure roles exist before assignment
		for role in roles_to_assign:
			if not frappe.db.exists("Role", role):
				self.create_custom_role(role)

		# Assign roles via Has Role inserts to avoid User doctype permission checks
		for role in roles_to_assign:
			if not frappe.db.exists("Has Role", {"parent": user_email, "role": role}):
				frappe.get_doc({
					"doctype": "Has Role",
					"parent": user_email,
					"parenttype": "User",
					"parentfield": "roles",
					"role": role,
				}).insert(ignore_permissions=True)
		# Log for debugging if still not present
		missing = [r for r in roles_to_assign if not frappe.db.exists("Has Role", {"parent": user_email, "role": r})]
		if missing:
			try:
				frappe.log_error(
					message=f"Roles still missing after assignment for {user_email}: {missing}; selected={selected_raw}",
					title="Unit Users Role Assignment"
				)
			except Exception:
				pass

	def assign_scope_reduction_roles_from_super_admin(self, target_user: str) -> None:
		"""Assign all roles that start with 'Scope' or 'Reduction' from a super admin-like user.

		Excludes the 'Super Admin' role itself. Uses any user having the role 'Super Admin' as
		the template; falls back to 'Administrator' if none.
		"""
		try:
			# Find a reference user who has 'Super Admin' role
			reference_user = None
			ref = frappe.get_all(
				"Has Role",
				filters={"role": "Super Admin", "parenttype": "User"},
				fields=["parent"],
				limit=1,
			)
			if ref:
				reference_user = ref[0]["parent"]
			else:
				reference_user = "Administrator"

			# Collect roles from reference user
			reference_roles = frappe.get_roles(reference_user)
			roles_to_copy = [
				r for r in reference_roles if r.startswith("Scope") or r.startswith("Reduction")
			]

			# Assign to target user (skip Super Admin)
			for role in roles_to_copy:
				if role == "Super Admin":
					continue
				# Ensure role exists
				if not frappe.db.exists("Role", role):
					continue
				# Assign if not present
				if not frappe.db.exists("Has Role", {"parent": target_user, "role": role}):
					frappe.get_doc({
						"doctype": "Has Role",
						"parent": target_user,
						"parenttype": "User",
						"parentfield": "roles",
						"role": role,
					}).insert(ignore_permissions=True)
		except Exception as e:
			# Non-fatal – log and continue
			frappe.log_error(f"Error assigning scope/reduction roles: {str(e)}", "Role Assignment")
	
	def create_custom_role(self, role_name):
		"""Create custom roles if they don't exist"""
		role_permissions = {
			"Unit Manager": {
				"desk_access": 1,
				"description": "Can manage units and view reports for assigned units"
			},
			"Data Analyst": {
				"desk_access": 1,
				"description": "Can analyze data and create reports for assigned units"
			}
		}
		
		if role_name in role_permissions:
			role_doc = frappe.get_doc({
				"doctype": "Role",
				"role_name": role_name,
				"desk_access": role_permissions[role_name]["desk_access"],
				"description": role_permissions[role_name]["description"]
			})
			role_doc.insert(ignore_permissions=True)
	
	def send_welcome_email(self, user_email):
		"""Send minimal welcome email with link to set password"""
		try:
			company_name = frappe.db.get_value("Company", self.company, "company_name") or "Our Platform"
			login_url = frappe.utils.get_url()
			frappe.sendmail(
				recipients=[self.email],
				subject=f"Welcome to {company_name}",
				message=f"Hello {self.first_name},<br><br>Your account has been created. Please set your password using the 'Forgot Password' link on the login page: <a href='{login_url}'>{login_url}</a>.<br><br>Regards,<br>{company_name}",
				now=True
			)
		except Exception as e:
			frappe.log_error(f"Error sending welcome email: {str(e)}", "Welcome Email Error")

	def on_update(self):
		"""Keep linked User in sync on Unit Users update"""
		# Only super admins can sync to the core User doctype to avoid permission errors
		if not self._is_super_admin_session():
			return
		if self.frappe_user_id and self.user_created:
			self.update_frappe_user()

	def _is_super_admin_session(self) -> bool:
		"""Return True if current session has System Manager or is Administrator."""
		if frappe.session.user == "Administrator":
			return True
		user_roles = frappe.get_roles(frappe.session.user)
		return any(r in ["System Manager", "Administrator"] for r in user_roles)
	
	def update_frappe_user(self):
		"""Update the linked Frappe user when Unit User is updated"""
		try:
			user_doc = frappe.get_doc("User", self.frappe_user_id)
			
			# Update basic details
			user_doc.first_name = self.first_name
			user_doc.email = self.email
			
			# Update roles if user_role changed
			self.update_user_roles(user_doc)
			self._verify_and_enforce_base_roles(user_doc.name)
			# Sync username and company on the user
			if getattr(self, "username", None):
				user_doc.username = self.username
			if getattr(self, "company", None):
				user_doc.company = self.company
			user_doc.save(ignore_permissions=True)
			# Sync user permissions for company
			if getattr(self, "company", None):
				self.reset_user_company_permissions(user_doc.name, self.company)
			
		except Exception as e:
			frappe.log_error(f"Error updating user account: {str(e)}", "Unit User Update Error")

	def reset_user_company_permissions(self, user_email: str, company: str) -> None:
		"""Replace Company user-permission with the current company for the user."""
		try:
			frappe.db.delete("User Permission", {"user": user_email, "allow": "Company"})
			self.create_user_permissions(user_email, company)
		except Exception as e:
			frappe.log_error(f"Error syncing user permissions: {str(e)}", "User Permission Sync")

	def on_trash(self):
		"""When Unit User is deleted, disable the linked Frappe User instead of deleting.

		Uses low-level db updates to avoid controller permission checks that may block
		a non-admin actor from saving linked child docs (e.g., Notification Settings).
		"""
		user_id = None
		if getattr(self, "frappe_user_id", None):
			user_id = self.frappe_user_id
		elif self.email:
			user_id = frappe.db.get_value("User", {"email": self.email})
		if not user_id:
			return
		try:
			# Remove company-specific user permissions
			frappe.db.delete("User Permission", {"user": user_id})
			# Remove all roles from the user
			frappe.db.delete("Has Role", {"parent": user_id})
			# Disable the user via direct DB update to bypass permission checks
			frappe.db.set_value("User", user_id, {"enabled": 0}, update_modified=True)
		except Exception as e:
			frappe.log_error(f"Failed to disable user {user_id}: {str(e)}", "Unit Users on_trash")
	
	def update_user_roles(self, user_doc):
		"""Update user roles based on current user_role"""
		# Remove base roles that we control
		old_roles = ["Unit Manager", "Data Analyst", "Employee"]
		for role in old_roles:
			frappe.db.delete("Has Role", {"parent": user_doc.name, "role": role})

		# Assign base role from selection (and Employee)
		self.assign_user_role(user_doc.name)
		# Ensure at least Employee exists as a guardrail
		if not frappe.db.exists("Has Role", {"parent": user_doc.name, "role": "Employee"}):
			frappe.get_doc({
				"doctype": "Has Role",
				"parent": user_doc.name,
				"parenttype": "User",
				"parentfield": "roles",
				"role": "Employee",
			}).insert(ignore_permissions=True)
		# Reapply scope/reduction bundle from Super Admin template (handles purge internally)
		self.assign_scope_reduction_roles_from_super_admin(user_doc.name)

@frappe.whitelist()
def get_filtered_units(doctype, txt, searchfield, start, page_len, filters):
	"""Filter units based on user's company"""
	if frappe.session.user == "Administrator":
		return frappe.db.sql("""
			SELECT name, name_of_unit 
			FROM `tabUnits` 
			WHERE name LIKE %(txt)s OR name_of_unit LIKE %(txt)s
			ORDER BY name_of_unit
			LIMIT %(start)s, %(page_len)s
		""", {
			'txt': f'%{txt}%',
			'start': start,
			'page_len': page_len
		})
	
	user_roles = frappe.get_roles(frappe.session.user)
	super_admin_roles = ["System Manager", "Administrator"]
	
	if any(role in super_admin_roles for role in user_roles):
		# Super admin can see all units, but restrict to their company
		user_company = frappe.db.get_value("User", frappe.session.user, "company")
		if user_company:
			company_filter = "AND company = %(company)s"
			params = {
				'txt': f'%{txt}%',
				'company': user_company,
				'start': start,
				'page_len': page_len
			}
		else:
			company_filter = ""
			params = {'txt': f'%{txt}%', 'start': start, 'page_len': page_len}
	else:
		# Regular users see only their company's units
		user_company = frappe.db.get_value("User", frappe.session.user, "company")
		company_filter = "AND company = %(company)s"
		params = {
			'txt': f'%{txt}%',
			'company': user_company,
			'start': start,
			'page_len': page_len
		}
	
	return frappe.db.sql(f"""
		SELECT name, name_of_unit 
		FROM `tabUnits` 
		WHERE (name LIKE %(txt)s OR name_of_unit LIKE %(txt)s) {company_filter}
		ORDER BY name_of_unit
		LIMIT %(start)s, %(page_len)s
	""", params)

@frappe.whitelist()
def generate_username(first_name, email):
	"""Generate a unique username based on first name and email"""
	if not first_name or not email:
		return ""
	
	# Extract name part from email
	email_prefix = email.split('@')[0]
	
	# Create base username from first name
	base_username = first_name.lower().replace(' ', '.')
	
	# If username doesn't exist, return it
	if not frappe.db.exists("User", base_username):
		return base_username
	
	# Try with email prefix
	username_with_email = f"{base_username}.{email_prefix.lower()}"
	if not frappe.db.exists("User", username_with_email):
		return username_with_email
	
	# Add numbers if still exists
	counter = 1
	while True:
		numbered_username = f"{base_username}{counter}"
		if not frappe.db.exists("User", numbered_username):
			return numbered_username
		counter += 1

@frappe.whitelist()
def generate_secure_password():
	"""Generate a secure random password that passes Frappe's validation"""
	# Create a more complex password that avoids repetition
	uppercase = string.ascii_uppercase
	lowercase = string.ascii_lowercase
	digits = string.digits
	special = "!@#$%&*"
	
	# Ensure password has at least one from each category
	password_chars = [
		secrets.choice(uppercase),
		secrets.choice(lowercase),
		secrets.choice(digits),
		secrets.choice(special)
	]
	
	# Fill the rest with random characters, avoiding repetition
	all_chars = uppercase + lowercase + digits + special
	for _ in range(8):  # Total length will be 12
		new_char = secrets.choice(all_chars)
		# Avoid immediate repetition
		while len(password_chars) > 0 and new_char == password_chars[-1]:
			new_char = secrets.choice(all_chars)
		password_chars.append(new_char)
	
	# Shuffle to avoid predictable patterns
	secrets.SystemRandom().shuffle(password_chars)
	password = ''.join(password_chars)
	
	return password
