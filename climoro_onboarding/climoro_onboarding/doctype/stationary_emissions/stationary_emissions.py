# Copyright (c) 2025, climoro and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class StationaryEmissions(Document):
	pass


def _is_super_user(user: str) -> bool:
	"""Return True if the user should bypass data restrictions."""
	if not user:
		return False
	if user == "Administrator":
		return True
	roles = set(frappe.get_roles(user))
	return "System Manager" in roles


def _get_user_company_and_units(user: str) -> tuple[str | None, list[str]]:
	"""Get the user's company and assigned units (if any).

	If the user has explicitly assigned units via Unit Users, return those units.
	If none are assigned, return an empty list to indicate no unit-level restriction.
	"""
	company = frappe.db.get_value("User", user, "company")
	units = []
	if company:
		# Prefer explicit mapping via Unit Users
		units = frappe.get_all(
			"Unit Users",
			filters={
				"frappe_user_id": user,
				"company": company,
			},
			pluck="assigned_unit",
		)
	return company, units or []


def get_permission_query_conditions(user: str = None) -> str | None:
	"""Row-level filter: restrict to user's company and (optionally) assigned units.

	Returning a SQL condition string applied to list queries.
	"""
	user = user or frappe.session.user
	if _is_super_user(user):
		return None

	company, units = _get_user_company_and_units(user)
	if not company:
		# No company on user → show nothing to avoid data leakage
		return "1=0"

	escaped_company = frappe.db.escape(company)
	conditions = [f"`tabStationary Emissions`.`company` = {escaped_company}"]
	if units:
		escaped_units = ", ".join(frappe.db.escape(u) for u in units)
		conditions.append(f"`tabStationary Emissions`.`unit` IN ({escaped_units})")

	return " AND ".join(conditions)


def has_permission(doc, ptype: str = None, user: str = None) -> bool:
	"""Document-level permission check aligned with query conditions."""
	user = user or frappe.session.user
	if _is_super_user(user):
		return True

	company, units = _get_user_company_and_units(user)
	if not company:
		return False
	if getattr(doc, "company", None) != company:
		return False
	# If units are assigned, enforce unit match; otherwise allow any unit within company
	if units:
		return getattr(doc, "unit", None) in set(units)
	return True
