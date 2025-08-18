import frappe
from typing import List, Set, Dict


# Central mapping of selections -> role names and workspaces
ROLE_MAP = {
	"scopes_to_report_scope1": "Scope 1 Access",
	"scopes_to_report_scope2": "Scope 2 Access",
	"scopes_to_report_scope3": "Scope 3 Access",
	"scopes_to_report_reductions": "Reduction Factor Access",
	# Scope 3 sub-options
	"scope_3_options_upstream": "Scope 3 Upstream Access",
	"scope_3_options_downstream": "Scope 3 Downstream Access",
}

WORKSPACE_BY_ROLE = {
	"Scope 1 Access": "Scope 1",
	"Scope 2 Access": "Scope 2",
	"Scope 3 Access": "Scope 3",
	"Reduction Factor Access": "Reduction Factor",
	"Scope 3 Upstream Access": "Upstream",
	"Scope 3 Downstream Access": "Downstream",
}

# Some Workspaces are stored under module "Setup", but the site also defines
# dedicated Module Def entries named "Scope 1", "Scope 2", "Scope 3",
# and "Reduction Factor". If those modules are blocked, the sidebar may hide
# the corresponding entries. Explicitly map roles to those Module Defs too.
MODULES_BY_ROLE = {
	"Scope 1 Access": {"Scope 1", "Setup"},
	"Scope 2 Access": {"Scope 2", "Setup"},
	"Scope 3 Access": {"Scope 3", "Setup"},
	"Reduction Factor Access": {"Reduction Factor", "Setup"},
	"Scope 3 Upstream Access": {"climoro onboarding"},
	"Scope 3 Downstream Access": {"climoro onboarding"},
}

# Doctypes that must be readable by users for the workflows to function
READONLY_DOCTYPES = {
	# Emission factors
	"Emission Factor Master",
	# Scope 1 → Fugitives
	"Fugitive Simple",
	"Fugitive Screening",
	"Fugitive Scale Base",
	# GWP reference list used by fugitives
	"GWP Reference",
}

# Always allow admins to see these workspaces
ALWAYS_ALLOWED_ROLES = {"System Manager", "Administrator", "Super Admin"}


def _ensure_roles_exist(role_names: Set[str]) -> None:
	for role_name in role_names.union(ALWAYS_ALLOWED_ROLES):
		if not frappe.db.exists("Role", role_name):
			role_doc = frappe.new_doc("Role")
			role_doc.role_name = role_name
			role_doc.desk_access = 1
			role_doc.save(ignore_permissions=True)


def _derive_roles_from_onboarding(onboarding_doc) -> Set[str]:
	roles: Set[str] = set()
	for fieldname, role_name in ROLE_MAP.items():
		if getattr(onboarding_doc, fieldname, 0):
			roles.add(role_name)
	return roles


def _get_latest_onboarding_for_company(company_name: str):
	if not company_name:
		return None
	record = frappe.get_all(
		"Onboarding Form",
		filters={"company_name": company_name, "status": "Approved"},
		fields=["name"],
		order_by="modified desc",
		limit=1,
	)
	if not record:
		return None
	return frappe.get_doc("Onboarding Form", record[0]["name"])


def _assign_roles_to_user(user_doc, role_names: Set[str]) -> None:
	existing_roles = {row.role for row in (user_doc.roles or [])}
	to_add = role_names.difference(existing_roles)
	for role in to_add:
		user_doc.append("roles", {"role": role})
	if to_add:
		user_doc.save(ignore_permissions=True)


def _sync_user_scope_roles(user_doc, desired_scope_roles: Set[str]) -> None:
	"""Ensure the user's scope-related roles match the desired set.
	Non-scope roles are preserved. Removes obsolete scope roles and adds missing ones.
	"""
	current_roles = {row.role for row in (user_doc.roles or [])}
	all_scope_roles = set(ROLE_MAP.values())
	# Remove obsolete scope roles
	to_remove = (current_roles & all_scope_roles) - desired_scope_roles
	if to_remove:
		user_doc.set(
			"roles",
			[row for row in (user_doc.roles or []) if row.role not in to_remove]
		)
	# Add missing desired roles
	to_add = desired_scope_roles - {row.role for row in (user_doc.roles or [])}
	for role in to_add:
		user_doc.append("roles", {"role": role})
	if to_remove or to_add:
		user_doc.save(ignore_permissions=True)


def _ensure_workspace_role_restrictions(all_possible_roles: Set[str]) -> None:
	# Ensure each workspace has at least its mapped role + admin roles
	roles_with_admin = all_possible_roles.union(ALWAYS_ALLOWED_ROLES)
	for role_name in roles_with_admin:
		workspace_label = WORKSPACE_BY_ROLE.get(role_name)
		if not workspace_label:
			continue

		workspace_list = frappe.get_all(
			"Workspace",
			filters={"label": workspace_label},
			fields=["name"],
		)
		if not workspace_list:
			# Workspace may not exist on this site; skip
			continue

		ws = frappe.get_doc("Workspace", workspace_list[0]["name"])
		ws_roles = {row.role for row in (ws.roles or [])}
		if role_name not in ws_roles:
			ws.append("roles", {"role": role_name})
		# Ensure admin role also present
		for admin_role in ALWAYS_ALLOWED_ROLES:
			if admin_role not in ws_roles and admin_role not in {role_name}:
				ws.append("roles", {"role": admin_role})
		ws.save(ignore_permissions=True)


def assign_roles_for_company_based_on_onboarding(company_name: str) -> None:
	onboarding = _get_latest_onboarding_for_company(company_name)
	if not onboarding:
		return

	selected_roles = _derive_roles_from_onboarding(onboarding)
	if not selected_roles:
		return

	_ensure_roles_exist(selected_roles)
	_ensure_workspace_role_restrictions(selected_roles)
	_ensure_readonly_docperms_for_roles(selected_roles)

	modules_to_unblock = _get_modules_for_roles(selected_roles)

	users = frappe.get_all(
		"User",
		filters={"company": company_name, "enabled": 1},
		fields=["name"],
	)
	for u in users:
		user_doc = frappe.get_doc("User", u["name"])
		_sync_user_scope_roles(user_doc, selected_roles)
		_unblock_modules_for_user(user_doc, modules_to_unblock)

	# Update workspace visibility for this company based on selections
	_update_workspace_visibility_for_onboarding(onboarding)


def assign_roles_to_new_user(doc, method=None):
	"""DocEvent hook: after a User is created, auto-assign roles based on the
	company's latest approved Onboarding Form selections.
	"""
	try:
		company_name = getattr(doc, "company", None)
		if not company_name:
			return
		onboarding = _get_latest_onboarding_for_company(company_name)
		if not onboarding:
			return
		selected_roles = _derive_roles_from_onboarding(onboarding)
		if not selected_roles:
			return
		_ensure_roles_exist(selected_roles)
		_ensure_workspace_role_restrictions(selected_roles)
		_ensure_readonly_docperms_for_roles(selected_roles)

		user_doc = frappe.get_doc("User", doc.name)
		_sync_user_scope_roles(user_doc, selected_roles)
		modules_to_unblock = _get_modules_for_roles(selected_roles)
		_unblock_modules_for_user(user_doc, modules_to_unblock)
		# Also align visibility (idempotent)
		onboarding = _get_latest_onboarding_for_company(company_name)
		if onboarding:
			_update_workspace_visibility_for_onboarding(onboarding)
	except Exception as e:
		frappe.log_error(f"Error in assign_roles_to_new_user: {str(e)}")


def setup_workspace_roles_for_all():
	"""Utility: ensure that workspaces have correct role restrictions for all
	possible roles defined by ROLE_MAP. Can be called manually if needed.
	"""
	all_roles = set(ROLE_MAP.values())
	_ensure_roles_exist(all_roles)
	_ensure_workspace_role_restrictions(all_roles)
	_ensure_readonly_docperms_for_roles(all_roles)


def _get_modules_for_roles(role_names: Set[str]) -> Set[str]:
	modules: Set[str] = set()
	for role in role_names:
		ws_label = WORKSPACE_BY_ROLE.get(role)
		if not ws_label:
			continue
		ws_list = frappe.get_all("Workspace", filters={"label": ws_label}, fields=["name", "module"])
		if ws_list:
			ws_doc = frappe.get_doc("Workspace", ws_list[0]["name"])
			if ws_doc.module:
				modules.add(ws_doc.module)
		# Add explicit module mapping if present
		explicit = MODULES_BY_ROLE.get(role)
		if explicit:
			modules.update(explicit)
	# Always ensure parent module for Scope 3 children is included if present
	return modules


def _unblock_modules_for_user(user_doc, modules_to_unblock: Set[str]) -> None:
	if not modules_to_unblock:
		return
	initial_count = len(user_doc.block_modules or [])
	remaining = []
	for row in user_doc.block_modules or []:
		if row.module in modules_to_unblock:
			continue
		remaining.append(row)
	if len(remaining) != initial_count:
		user_doc.set("block_modules", remaining)
		user_doc.save(ignore_permissions=True)


def _update_workspace_visibility_for_onboarding(onboarding_doc) -> None:
	"""Set Workspace.is_hidden based on selections in the onboarding doc.
	Visible only when the corresponding scope/sub-option/reduction is selected.
	"""
	desired_visible = set()
	# Top-level scopes
	if getattr(onboarding_doc, "scopes_to_report_scope1", 0):
		desired_visible.add("Scope 1")
	if getattr(onboarding_doc, "scopes_to_report_scope2", 0):
		desired_visible.add("Scope 2")
	if getattr(onboarding_doc, "scopes_to_report_scope3", 0):
		desired_visible.add("Scope 3")
	if getattr(onboarding_doc, "scopes_to_report_reductions", 0):
		desired_visible.add("Reduction Factor")

	# Scope 1 sub-options → dedicated workspaces
	if getattr(onboarding_doc, "scope_1_options_stationary", 0):
		desired_visible.add("Stationary Emissions")
	if getattr(onboarding_doc, "scope_1_options_mobile", 0):
		desired_visible.add("Mobile Combustion")
	if getattr(onboarding_doc, "scope_1_options_fugitive", 0):
		desired_visible.add("Fugitives")
	if getattr(onboarding_doc, "scope_1_options_process", 0):
		desired_visible.add("Process")

	# Scope 3 sub-options
	if getattr(onboarding_doc, "scope_3_options_upstream", 0):
		desired_visible.add("Upstream")
	if getattr(onboarding_doc, "scope_3_options_downstream", 0):
		desired_visible.add("Downstream")

	# Reduction sub-options (if present as workspaces)
	reduction_children = [
		("Energy Efficiency", getattr(onboarding_doc, "reduction_options_energy_efficiency", 0)),
		("Solar", getattr(onboarding_doc, "reduction_options_renewable_energy", 0)),
		("Process Optimization", getattr(onboarding_doc, "reduction_options_process_optimization", 0)),
		("Waste Manage", getattr(onboarding_doc, "reduction_options_waste_management", 0)),
		("Transportation-Upstream", getattr(onboarding_doc, "reduction_options_transportation", 0)),
		("Methane Recovery", getattr(onboarding_doc, "reduction_options_other", 0)),
	]
	for label, selected in reduction_children:
		if selected:
			desired_visible.add(label)

	labels_to_manage = [
		# parents
		"Scope 1", "Scope 2", "Scope 3", "Reduction Factor", "Home",
		# Scope 1 children
		"Stationary Emissions", "Mobile Combustion", "Fugitives", "Process",
		# Scope 3 children
		"Upstream", "Downstream",
		# Reduction children
		"Energy Efficiency", "Solar", "Process Optimization", "Waste Manage", "Transportation-Upstream", "Methane Recovery",
	]

	for label in labels_to_manage:
		ws_list = frappe.get_all("Workspace", filters={"label": label}, fields=["name","is_hidden"], limit=1)
		if not ws_list:
			continue
		ws = frappe.get_doc("Workspace", ws_list[0]["name"])
		# Home should be hidden for all non-admin users
		if label == "Home":
			should_show = False
		else:
			should_show = label in desired_visible
		new_hidden = 0 if should_show else 1
		if int(ws.is_hidden or 0) != new_hidden:
			ws.is_hidden = new_hidden
			ws.save(ignore_permissions=True)


def _ensure_readonly_docperms_for_roles(role_names: Set[str]) -> None:
	for doctype in READONLY_DOCTYPES:
		for role in role_names.union(ALWAYS_ALLOWED_ROLES):
			try:
				# Skip if role does not exist
				if not frappe.db.exists("Role", role):
					continue
				exists = frappe.get_all(
					"Custom DocPerm",
					filters={"parent": doctype, "role": role, "permlevel": 0},
					limit=1,
				)
				if not exists:
					c = frappe.new_doc("Custom DocPerm")
					c.parent = doctype
					c.parenttype = "DocType"
					c.parentfield = "permissions"
					c.role = role
					c.permlevel = 0
					c.read = 1
					c.print = 1
					c.report = 1
					c.write = 0
					c.create = 0
					c.delete = 0
					c.submit = 0
					c.email = 0
					c.share = 0
					c.save(ignore_permissions=True)
			except Exception as e:
				frappe.log_error(f"Error ensuring readonly perms for {doctype}/{role}: {str(e)}")


def sync_onboarding_selection(doc, method=None):
	"""DocEvent hook: whenever Onboarding Form is updated, if it's Approved,
	re-apply roles, workspace visibility, and doc permissions according to selections.
	"""
	try:
		if getattr(doc, "status", "") == "Approved" and getattr(doc, "company_name", None):
			assign_roles_for_company_based_on_onboarding(doc.company_name)
	except Exception as e:
		frappe.log_error(f"Error in sync_onboarding_selection: {str(e)}")


