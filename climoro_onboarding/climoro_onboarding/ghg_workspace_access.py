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
	# Scope 1 sub-options
	"scope_1_options_stationary": "Scope 1 Stationary Access",
	"scope_1_options_mobile": "Scope 1 Mobile Access",
	"scope_1_options_fugitive": "Scope 1 Fugitives Access",
	"scope_1_options_process": "Scope 1 Process Access",
	# Reduction sub-options
	"reduction_options_energy_efficiency": "Reduction Energy Efficiency Access",
	"reduction_options_renewable_energy": "Reduction Solar Access",
	"reduction_options_process_optimization": "Reduction Process Optimization Access",
	"reduction_options_waste_management": "Reduction Waste Manage Access",
	"reduction_options_transportation": "Reduction Transportation Access",
	"reduction_options_other": "Reduction Methane Recovery Access",
}

WORKSPACE_BY_ROLE = {
	"Scope 1 Access": "Scope 1",
	"Scope 2 Access": "Scope 2",
	"Scope 3 Access": "Scope 3",
	"Reduction Factor Access": "Reduction Factor",
	"Scope 3 Upstream Access": "Upstream",
	"Scope 3 Downstream Access": "Downstream",
	# Scope 1 children
	"Scope 1 Stationary Access": "Stationary Emissions",
	"Scope 1 Mobile Access": "Mobile Combustion",
	"Scope 1 Fugitives Access": "Fugitives",
	"Scope 1 Process Access": "Process",
	# Reduction children
	"Reduction Energy Efficiency Access": "Energy Efficiency",
	"Reduction Solar Access": "Solar",
	"Reduction Process Optimization Access": "Process Optimization",
	"Reduction Waste Manage Access": "Waste Manage",
	"Reduction Transportation Access": "Transportation-Upstream",
	"Reduction Methane Recovery Access": "Methane Recovery",
}

# Additional static workspace-role links that should follow parent scope access
EXTRA_WORKSPACES_BY_ROLE = {
	"Scope 2 Access": {"Electricity"},
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

# Always-allowed roles for workspaces. Keep empty to enforce company selections for everyone.
ALWAYS_ALLOWED_ROLES = set()

# Hidden role used to block unmanaged workspaces without relying on is_hidden global flag
HIDDEN_ROLE = "Climoro Hidden"


def _ensure_roles_exist(role_names: Set[str]) -> None:
	for role_name in role_names.union(ALWAYS_ALLOWED_ROLES):
		if not frappe.db.exists("Role", role_name):
			role_doc = frappe.new_doc("Role")
			role_doc.role_name = role_name
			role_doc.desk_access = 1
			role_doc.save(ignore_permissions=True)


def _derive_roles_from_onboarding(onboarding_doc) -> Set[str]:
	roles: Set[str] = set()
	# Parent scopes
	s1 = bool(getattr(onboarding_doc, "scopes_to_report_scope1", 0))
	s2 = bool(getattr(onboarding_doc, "scopes_to_report_scope2", 0))
	s3 = bool(getattr(onboarding_doc, "scopes_to_report_scope3", 0))
	red = bool(getattr(onboarding_doc, "scopes_to_report_reductions", 0))

	if s1:
		roles.add("Scope 1 Access")
		# Scope 1 sub-options
		if getattr(onboarding_doc, "scope_1_options_stationary", 0):
			roles.add("Scope 1 Stationary Access")
		if getattr(onboarding_doc, "scope_1_options_mobile", 0):
			roles.add("Scope 1 Mobile Access")
		if getattr(onboarding_doc, "scope_1_options_fugitive", 0):
			roles.add("Scope 1 Fugitives Access")
		if getattr(onboarding_doc, "scope_1_options_process", 0):
			roles.add("Scope 1 Process Access")

	if s2:
		roles.add("Scope 2 Access")

	if s3:
		roles.add("Scope 3 Access")
		
		# Handle Scope 3 sub-options - only grant access to specifically selected options
		has_upstream = getattr(onboarding_doc, "scope_3_options_upstream", 0)
		has_downstream = getattr(onboarding_doc, "scope_3_options_downstream", 0)
		
		if has_upstream:
			roles.add("Scope 3 Upstream Access")
		if has_downstream:
			roles.add("Scope 3 Downstream Access")

	if red:
		roles.add("Reduction Factor Access")
		if getattr(onboarding_doc, "reduction_options_energy_efficiency", 0):
			roles.add("Reduction Energy Efficiency Access")
		if getattr(onboarding_doc, "reduction_options_renewable_energy", 0):
			roles.add("Reduction Solar Access")
		if getattr(onboarding_doc, "reduction_options_process_optimization", 0):
			roles.add("Reduction Process Optimization Access")
		if getattr(onboarding_doc, "reduction_options_waste_management", 0):
			roles.add("Reduction Waste Manage Access")
		if getattr(onboarding_doc, "reduction_options_transportation", 0):
			roles.add("Reduction Transportation Access")
		if getattr(onboarding_doc, "reduction_options_other", 0):
			roles.add("Reduction Methane Recovery Access")

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
		# Start with only roles we manage: scope roles + always-allowed
		allowed_set = all_possible_roles.union(ALWAYS_ALLOWED_ROLES)
		ws.set("roles", [r for r in (ws.roles or []) if r.role in allowed_set])
		ws_roles = {row.role for row in (ws.roles or [])}
		# Add required role for this workspace
		if role_name not in ws_roles:
			ws.append("roles", {"role": role_name})
		# Ensure admin roles present if configured
		for admin_role in ALWAYS_ALLOWED_ROLES:
			if admin_role not in ws_roles:
				ws.append("roles", {"role": admin_role})
		# Explicitly remove admin-type roles if not in always-allowed
		if "Super Admin" not in ALWAYS_ALLOWED_ROLES:
			ws.set("roles", [r for r in (ws.roles or []) if r.role != "Super Admin"])
		if "System Manager" not in ALWAYS_ALLOWED_ROLES:
			ws.set("roles", [r for r in (ws.roles or []) if r.role != "System Manager"])
		if "Administrator" not in ALWAYS_ALLOWED_ROLES:
			ws.set("roles", [r for r in (ws.roles or []) if r.role != "Administrator"])
		ws.save(ignore_permissions=True)

	# Ensure extra workspace-role links (e.g., Electricity -> Scope 2 Access)
	for role_name, labels in EXTRA_WORKSPACES_BY_ROLE.items():
		for label in labels:
			ws_list = frappe.get_all("Workspace", filters={"label": label}, fields=["name"])
			if not ws_list:
				continue
			ws = frappe.get_doc("Workspace", ws_list[0]["name"])
			ws_roles = {row.role for row in (ws.roles or [])}
			# Keep only managed roles here as well
			allowed_set = all_possible_roles.union(ALWAYS_ALLOWED_ROLES).union({role_name})
			ws.set("roles", [r for r in (ws.roles or []) if r.role in allowed_set])
			if role_name not in ws_roles:
				ws.append("roles", {"role": role_name})
			# Remove admin-type roles
			if "Super Admin" not in ALWAYS_ALLOWED_ROLES:
				ws.set("roles", [r for r in (ws.roles or []) if r.role != "Super Admin"])
			if "System Manager" not in ALWAYS_ALLOWED_ROLES:
				ws.set("roles", [r for r in (ws.roles or []) if r.role != "System Manager"])
			if "Administrator" not in ALWAYS_ALLOWED_ROLES:
				ws.set("roles", [r for r in (ws.roles or []) if r.role != "Administrator"])
			ws.save(ignore_permissions=True)


def _lockdown_unmanaged_workspaces() -> None:
	"""For workspaces under our managed modules but not in our managed label set,
	assign a hidden role so they don't appear to anyone by default.
	"""
	managed_modules = {"Scope 1", "Scope 2", "Scope 3", "Reduction Factor", "climoro onboarding"}
	managed_labels = set(WORKSPACE_BY_ROLE.values())
	managed_labels.update({"Scope 1", "Scope 2", "Scope 3", "Reduction Factor", "Electricity"})
	# Ensure hidden role exists
	if not frappe.db.exists("Role", HIDDEN_ROLE):
		role_doc = frappe.new_doc("Role")
		role_doc.role_name = HIDDEN_ROLE
		role_doc.desk_access = 0
		role_doc.save(ignore_permissions=True)
	# Sweep all public workspaces in managed modules
	pages = frappe.get_all(
		"Workspace",
		fields=["name", "label", "module", "public"],
		filters={"public": 1},
	)
	for p in pages:
		if not p.get("module") or p.get("module") not in managed_modules:
			continue
		label = p.get("label")
		if label in managed_labels:
			continue
		ws = frappe.get_doc("Workspace", p["name"])
		# Replace roles with only hidden role
		ws.set("roles", [])
		ws.append("roles", {"role": HIDDEN_ROLE})
		ws.save(ignore_permissions=True)


def _lockdown_by_parent_page(selected_roles: Set[str]) -> None:
	"""Lock down any public workspaces whose parent_page is a managed root,
	but label is not in the selected/allowed set.
	Enhanced to handle nested hierarchies like Scope 3 -> Upstream/Downstream -> children.
	"""
	# Ensure hidden role exists
	if not frappe.db.exists("Role", HIDDEN_ROLE):
		role_doc = frappe.new_doc("Role")
		role_doc.role_name = HIDDEN_ROLE
		role_doc.desk_access = 0
		role_doc.save(ignore_permissions=True)
	
	managed_parents = {"Scope 1", "Scope 2", "Scope 3", "Reduction Factor", "Upstream", "Downstream"}

	# Compute allowed labels strictly from selected roles
	allowed_labels = {WORKSPACE_BY_ROLE[r] for r in selected_roles if r in WORKSPACE_BY_ROLE}
	allowed_labels.update(EXTRA_WORKSPACES_BY_ROLE.get("Scope 2 Access", set()))

	# Get all workspaces to process
	pages = frappe.get_all(
		"Workspace",
		fields=["name", "label", "parent_page", "public"],
		filters={"public": 1},
	)
	
	# Enhanced logic to handle nested hierarchies
	for p in pages:
		parent = p.get("parent_page")
		label = p.get("label")
		
		# Skip if not under managed hierarchy
		if parent not in managed_parents and label not in managed_parents:
			continue
		
		# Determine if this workspace should be accessible
		should_be_accessible = False
		
		# Case 1: Direct parent-child (e.g., Scope 1 -> Stationary Emissions)
		if parent in managed_parents and label in allowed_labels:
			should_be_accessible = True
		
		# Case 2: Parent workspace itself (e.g., Scope 1, Upstream, Downstream)
		elif label in allowed_labels:
			should_be_accessible = True
			
		# Case 3: Nested hierarchy - child of Upstream/Downstream
		elif parent in ["Upstream", "Downstream"]:
			# Check if user has access to the specific parent (Upstream/Downstream)
			parent_roles = []
			if parent == "Upstream" and "Scope 3 Upstream Access" in selected_roles:
				parent_roles = ["Scope 3 Access", "Scope 3 Upstream Access"]
			elif parent == "Downstream" and "Scope 3 Downstream Access" in selected_roles:
				parent_roles = ["Scope 3 Access", "Scope 3 Downstream Access"]
			
			if parent_roles:
				should_be_accessible = True
				# Grant access to the child workspace
				ws = frappe.get_doc("Workspace", p["name"])
				ws.set("roles", [{"role": role} for role in parent_roles])
				ws.save(ignore_permissions=True)
				continue
		
		# Case 4: Upstream/Downstream workspaces themselves
		elif label in ["Upstream", "Downstream"]:
			# Only grant access if user has the specific access role for this workspace
			if (label == "Upstream" and "Scope 3 Upstream Access" in selected_roles) or \
			   (label == "Downstream" and "Scope 3 Downstream Access" in selected_roles):
				should_be_accessible = True
				# Grant appropriate access
				ws = frappe.get_doc("Workspace", p["name"])
				if label == "Upstream":
					ws.set("roles", [{"role": "Scope 3 Access"}, {"role": "Scope 3 Upstream Access"}])
				else:  # Downstream
					ws.set("roles", [{"role": "Scope 3 Access"}, {"role": "Scope 3 Downstream Access"}])
				ws.save(ignore_permissions=True)
				continue
		
		# If workspace should not be accessible, hide it
		if not should_be_accessible:
			ws = frappe.get_doc("Workspace", p["name"])
			ws.set("roles", [])
			ws.append("roles", {"role": HIDDEN_ROLE})
			ws.save(ignore_permissions=True)


def _delete_private_pages_for_users(company_name: str, selected_roles: Set[str]) -> None:
	"""Remove private workspaces for company users that would expose disallowed pages.
	Private pages bypass role gating in the sidebar, so we delete the ones under managed parents
	that are not part of the selection.
	"""
	users = frappe.get_all("User", filters={"company": company_name, "enabled": 1}, pluck="name")
	if not users:
		return
	# Build allow set like in parent lockdown
	allowed_labels = {WORKSPACE_BY_ROLE[r] for r in selected_roles if r in WORKSPACE_BY_ROLE}
	allowed_labels.update(EXTRA_WORKSPACES_BY_ROLE.get("Scope 2 Access", set()))
	managed_parents = {"Scope 1", "Scope 2", "Scope 3", "Reduction Factor"}
	for uname in users:
		privs = frappe.get_all(
			"Workspace",
			fields=["name", "title", "label", "parent_page"],
			filters={"for_user": uname},
		)
		for p in privs:
			parent = p.get("parent_page")
			label = p.get("label") or p.get("title")
			if parent in managed_parents and label not in allowed_labels and label != parent:
				try:
					frappe.delete_doc("Workspace", p["name"], ignore_permissions=True, force=True)
				except Exception:
					pass


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


def assign_roles_for_company_based_on_onboarding(company_name: str) -> None:
	onboarding = _get_latest_onboarding_for_company(company_name)
	if not onboarding:
		return

	selected_roles = _derive_roles_from_onboarding(onboarding)
	if not selected_roles:
		return

	_ensure_roles_exist(selected_roles)
	# Ensure all managed workspaces have role restrictions
	all_scope_roles = set(ROLE_MAP.values())
	_ensure_roles_exist(all_scope_roles)
	_ensure_workspace_role_restrictions(all_scope_roles)
	_lockdown_unmanaged_workspaces()
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

	# Normalize global workspace visibility; rely on role gating
	_reset_global_hidden_flags()
	_hide_home_workspace_for_all()
	_lockdown_by_parent_page(selected_roles)
	_delete_private_pages_for_users(company_name, selected_roles)


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
		all_scope_roles = set(ROLE_MAP.values())
		_ensure_roles_exist(all_scope_roles)
		_ensure_workspace_role_restrictions(all_scope_roles)
		_lockdown_unmanaged_workspaces()
		_ensure_readonly_docperms_for_roles(selected_roles)

		user_doc = frappe.get_doc("User", doc.name)
		_sync_user_scope_roles(user_doc, selected_roles)
		modules_to_unblock = _get_modules_for_roles(selected_roles)
		_unblock_modules_for_user(user_doc, modules_to_unblock)
		# Normalize global visibility
		_reset_global_hidden_flags()
		_hide_home_workspace_for_all()
		_lockdown_by_parent_page(selected_roles)
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


def _reset_global_hidden_flags():
	"""Ensure standard workspaces are visible globally (except 'Home' handled separately),
	so that role restrictions drive visibility per user/company.
	"""
	labels = [
		"Scope 1", "Scope 2", "Scope 3", "Reduction Factor",
		"Stationary Emissions", "Mobile Combustion", "Fugitives", "Process",
		"Upstream", "Downstream",
		"Energy Efficiency", "Solar", "Process Optimization", "Waste Manage", "Transportation-Upstream", "Methane Recovery",
	]
	for label in labels:
		ws = frappe.get_all("Workspace", filters={"label": label}, fields=["name","is_hidden"], limit=1)
		if not ws:
			continue
		doc = frappe.get_doc("Workspace", ws[0]["name"])
		if int(doc.is_hidden or 0) != 0:
			doc.is_hidden = 0
			doc.save(ignore_permissions=True)


def _hide_home_workspace_for_all():
	ws = frappe.get_all("Workspace", filters={"label": "Home"}, fields=["name","is_hidden"], limit=1)
	if not ws:
		return
	doc = frappe.get_doc("Workspace", ws[0]["name"])
	# Hide globally and clear roles so it won't appear for anyone
	doc.is_hidden = 1
	doc.set("roles", [])
	doc.save(ignore_permissions=True)


def sync_onboarding_selection(doc, method=None):
	"""DocEvent hook: whenever Onboarding Form is updated, if it's Approved,
	re-apply roles, and normalize global visibility to avoid cross-company impact.
	"""
	try:
		if getattr(doc, "status", "") == "Approved" and getattr(doc, "company_name", None):
			assign_roles_for_company_based_on_onboarding(doc.company_name)
	except Exception as e:
		frappe.log_error(f"Error in sync_onboarding_selection: {str(e)}")


