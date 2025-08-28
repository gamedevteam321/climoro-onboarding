# Copyright (c) 2024, Climoro Onboarding and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Units(Document):
	def validate(self):
		# Validate GPS coordinates format if provided
		if self.gps_coordinates:
			self.validate_gps_coordinates()
	
	def validate_gps_coordinates(self):
		"""Validate GPS coordinates format (latitude, longitude)"""
		if not self.gps_coordinates:
			return
		
		try:
			coords = self.gps_coordinates.split(',')
			if len(coords) != 2:
				frappe.throw("GPS coordinates must be in format: latitude, longitude")
			
			lat = float(coords[0].strip())
			lng = float(coords[1].strip())
			
			if not (-90 <= lat <= 90):
				frappe.throw("Latitude must be between -90 and 90 degrees")
			
			if not (-180 <= lng <= 180):
				frappe.throw("Longitude must be between -180 and 180 degrees")
				
		except ValueError:
			frappe.throw("GPS coordinates must be valid numbers")
	
	def before_insert(self):
		# Set company-specific permissions
		self.setup_company_permissions()
	
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
				frappe.throw(f"You can only create units for your company: {user_company}")

@frappe.whitelist()
def get_user_company_filter():
	"""Get company filter for current user (used in list view)"""
	if frappe.session.user == "Administrator":
		return {}
	
	user_roles = frappe.get_roles(frappe.session.user)
	super_admin_roles = ["System Manager", "Administrator"]
	
	if any(role in super_admin_roles for role in user_roles):
		return {}  # Super admin can see all companies
	
	# Regular users see only their company
	user_company = frappe.db.get_value("User", frappe.session.user, "company")
	return {"company": user_company} if user_company else {}
