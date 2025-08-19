import frappe
from typing import List, Set, Dict, Optional
import json

class WorkspaceAccessManager:
    """
    Enhanced workspace access management system for the Climoro onboarding app.
    This system provides extensible role-based workspace and module access control.
    """
    
    def __init__(self):
        # Load configuration from a JSON file for better extensibility
        self.config = self._load_config()
        
    def _load_config(self) -> Dict:
        """Load workspace access configuration from file or use defaults"""
        try:
            # Try to load from a configuration file first
            config_path = frappe.get_app_path("climoro_onboarding", "config", "workspace_access_config.json")
            with open(config_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Fall back to default configuration
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Default configuration for workspace access control"""
        return {
            "role_mappings": {
                # Main scope roles
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
            },
            
            "workspace_mappings": {
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
            },
            
            "extra_workspace_mappings": {
                "Scope 2 Access": ["Electricity"]
            },
            
            "module_mappings": {
                "Scope 1 Access": ["Scope 1", "Setup"],
                "Scope 2 Access": ["Scope 2", "Setup"],
                "Scope 3 Access": ["Scope 3", "Setup"],
                "Reduction Factor Access": ["Reduction Factor", "Setup"],
                "Scope 3 Upstream Access": ["climoro onboarding"],
                "Scope 3 Downstream Access": ["climoro onboarding"],
            },
            
            "user_role_hierarchy": {
                "Super Admin": {
                    "level": 1,
                    "description": "Highest level access - company administrator",
                    "can_manage_users": True,
                    "default_scopes": ["all"]
                },
                "Unit Manager": {
                    "level": 2,
                    "description": "Unit-level management access",
                    "can_manage_users": False,
                    "default_scopes": []
                },
                "Data Analyst": {
                    "level": 3,
                    "description": "Data analysis and reporting access",
                    "can_manage_users": False,
                    "default_scopes": []
                }
            },
            
            "readonly_doctypes": [
                "Emission Factor Master",
                "Fugitive Simple",
                "Fugitive Screening", 
                "Fugitive Scale Base",
                "GWP Reference"
            ],
            
            "always_allowed_roles": [],
            "hidden_role": "Climoro Hidden",
            "managed_modules": ["Scope 1", "Scope 2", "Scope 3", "Reduction Factor", "climoro onboarding"]
        }
    
    def add_new_role(self, role_name: str, role_config: Dict) -> bool:
        """
        Add a new user role to the system
        
        Args:
            role_name: Name of the new role
            role_config: Configuration dictionary with role details
            
        Returns:
            bool: Success status
        """
        try:
            # Validate role configuration
            required_fields = ['level', 'description', 'can_manage_users', 'default_scopes']
            if not all(field in role_config for field in required_fields):
                frappe.throw(f"Role configuration missing required fields: {required_fields}")
            
            # Add to user role hierarchy
            self.config['user_role_hierarchy'][role_name] = role_config
            
            # Create the role in Frappe if it doesn't exist
            if not frappe.db.exists("Role", role_name):
                role_doc = frappe.new_doc("Role")
                role_doc.role_name = role_name
                role_doc.desk_access = 1
                role_doc.module = "Climoro Onboarding"
                role_doc.save(ignore_permissions=True)
            
            # Save updated configuration
            self._save_config()
            
            frappe.logger().info(f"Successfully added new role: {role_name}")
            return True
            
        except Exception as e:
            frappe.log_error(f"Error adding new role {role_name}: {str(e)}")
            return False
    
    def add_scope_mapping(self, form_field: str, role_name: str, workspace_label: str, modules: List[str] = None) -> bool:
        """
        Add a new scope mapping for form fields to roles and workspaces
        
        Args:
            form_field: Form field name that triggers this role
            role_name: Role to be assigned
            workspace_label: Workspace label to be shown
            modules: List of modules to unblock
            
        Returns:
            bool: Success status
        """
        try:
            # Add form field to role mapping
            self.config['role_mappings'][form_field] = role_name
            
            # Add role to workspace mapping
            self.config['workspace_mappings'][role_name] = workspace_label
            
            # Add module mappings if provided
            if modules:
                self.config['module_mappings'][role_name] = modules
            
            # Create the role if it doesn't exist
            if not frappe.db.exists("Role", role_name):
                role_doc = frappe.new_doc("Role")
                role_doc.role_name = role_name
                role_doc.desk_access = 1
                role_doc.module = "Climoro Onboarding"
                role_doc.save(ignore_permissions=True)
            
            # Save updated configuration
            self._save_config()
            
            frappe.logger().info(f"Successfully added scope mapping: {form_field} -> {role_name} -> {workspace_label}")
            return True
            
        except Exception as e:
            frappe.log_error(f"Error adding scope mapping: {str(e)}")
            return False
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            config_dir = frappe.get_app_path("climoro_onboarding", "config")
            frappe.create_folder(config_dir)
            
            config_path = frappe.get_app_path("climoro_onboarding", "config", "workspace_access_config.json")
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            frappe.log_error(f"Error saving workspace access config: {str(e)}")
    
    def derive_roles_from_onboarding(self, onboarding_doc) -> Set[str]:
        """Derive access roles based on onboarding form selections"""
        roles: Set[str] = set()
        
        for form_field, role_name in self.config['role_mappings'].items():
            if getattr(onboarding_doc, form_field, 0):
                roles.add(role_name)
        
        return roles
    
    def get_workspaces_for_roles(self, roles: Set[str]) -> Set[str]:
        """Get workspace labels for given roles"""
        workspaces = set()
        
        for role in roles:
            workspace = self.config['workspace_mappings'].get(role)
            if workspace:
                workspaces.add(workspace)
            
            # Add extra workspaces
            extra_workspaces = self.config['extra_workspace_mappings'].get(role, [])
            workspaces.update(extra_workspaces)
        
        return workspaces
    
    def get_modules_for_roles(self, roles: Set[str]) -> Set[str]:
        """Get modules to unblock for given roles"""
        modules = set()
        
        for role in roles:
            role_modules = self.config['module_mappings'].get(role, [])
            modules.update(role_modules)
        
        return modules
    
    def ensure_roles_exist(self, role_names: Set[str]):
        """Ensure all required roles exist in the system"""
        for role_name in role_names:
            if not frappe.db.exists("Role", role_name):
                role_doc = frappe.new_doc("Role")
                role_doc.role_name = role_name
                role_doc.desk_access = 1
                role_doc.module = "Climoro Onboarding"
                role_doc.save(ignore_permissions=True)
    
    def apply_workspace_restrictions(self, selected_roles: Set[str]):
        """Apply workspace role restrictions based on selected roles"""
        all_possible_roles = set(self.config['role_mappings'].values())
        always_allowed = set(self.config['always_allowed_roles'])
        
        # Ensure each workspace has correct role restrictions
        for role_name in selected_roles.union(always_allowed):
            workspace_label = self.config['workspace_mappings'].get(role_name)
            if not workspace_label:
                continue
            
            workspace_list = frappe.get_all(
                "Workspace",
                filters={"label": workspace_label},
                fields=["name"]
            )
            
            if not workspace_list:
                continue
            
            ws = frappe.get_doc("Workspace", workspace_list[0]["name"])
            
            # Update workspace roles
            allowed_roles = selected_roles.union(always_allowed)
            ws.set("roles", [{"role": role} for role in allowed_roles if role in [role_name] + list(always_allowed)])
            
            # Ensure the required role is present
            current_roles = {row.role for row in ws.roles or []}
            if role_name not in current_roles:
                ws.append("roles", {"role": role_name})
            
            ws.save(ignore_permissions=True)
    
    def assign_roles_for_company(self, company_name: str):
        """Main method to assign roles for a company based on onboarding"""
        onboarding = self._get_latest_onboarding_for_company(company_name)
        if not onboarding:
            return
        
        selected_roles = self.derive_roles_from_onboarding(onboarding)
        if not selected_roles:
            return
        
        self.ensure_roles_exist(selected_roles)
        modules_to_unblock = self.get_modules_for_roles(selected_roles)
        
        # Update all company users
        users = frappe.get_all(
            "User",
            filters={"company": company_name, "enabled": 1},
            fields=["name"]
        )
        
        for user in users:
            user_doc = frappe.get_doc("User", user["name"])
            self._sync_user_scope_roles(user_doc, selected_roles)
            self._unblock_modules_for_user(user_doc, modules_to_unblock)
        
        # Apply workspace restrictions
        self.apply_workspace_restrictions(selected_roles)
    
    def _get_latest_onboarding_for_company(self, company_name: str):
        """Get the latest approved onboarding form for a company"""
        if not company_name:
            return None
        
        record = frappe.get_all(
            "Onboarding Form",
            filters={"company_name": company_name, "status": "Approved"},
            fields=["name"],
            order_by="modified desc",
            limit=1
        )
        
        if not record:
            return None
        
        return frappe.get_doc("Onboarding Form", record[0]["name"])
    
    def _sync_user_scope_roles(self, user_doc, desired_scope_roles: Set[str]):
        """Sync user roles with desired scope roles"""
        current_roles = {row.role for row in user_doc.roles or []}
        all_scope_roles = set(self.config['role_mappings'].values())
        
        # Remove obsolete scope roles
        to_remove = (current_roles & all_scope_roles) - desired_scope_roles
        if to_remove:
            user_doc.set("roles", [row for row in user_doc.roles or [] if row.role not in to_remove])
        
        # Add missing desired roles
        current_roles_after_remove = {row.role for row in user_doc.roles or []}
        to_add = desired_scope_roles - current_roles_after_remove
        for role in to_add:
            user_doc.append("roles", {"role": role})
        
        if to_remove or to_add:
            user_doc.save(ignore_permissions=True)
    
    def _unblock_modules_for_user(self, user_doc, modules_to_unblock: Set[str]):
        """Unblock specified modules for a user"""
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

# Global instance
workspace_access_manager = WorkspaceAccessManager()

# API functions for external use
@frappe.whitelist()
def add_new_role(role_name, level, description, can_manage_users=False, default_scopes=None):
    """API function to add a new role"""
    if default_scopes is None:
        default_scopes = []
    
    role_config = {
        "level": int(level),
        "description": description,
        "can_manage_users": bool(can_manage_users),
        "default_scopes": default_scopes
    }
    
    return workspace_access_manager.add_new_role(role_name, role_config)

@frappe.whitelist()
def add_scope_mapping(form_field, role_name, workspace_label, modules=None):
    """API function to add a new scope mapping"""
    if modules is None:
        modules = []
    elif isinstance(modules, str):
        modules = [modules]
    
    return workspace_access_manager.add_scope_mapping(form_field, role_name, workspace_label, modules)

@frappe.whitelist()
def get_available_roles():
    """Get all available roles in the system"""
    return workspace_access_manager.config['user_role_hierarchy']

@frappe.whitelist()
def get_role_mappings():
    """Get current role mappings"""
    return {
        "role_mappings": workspace_access_manager.config['role_mappings'],
        "workspace_mappings": workspace_access_manager.config['workspace_mappings'],
        "module_mappings": workspace_access_manager.config['module_mappings']
    }

# Compatibility functions for existing code
def assign_roles_for_company_based_on_onboarding(company_name: str):
    """Wrapper for backward compatibility"""
    return workspace_access_manager.assign_roles_for_company(company_name)

def assign_roles_to_new_user(doc, method=None):
    """Hook for new user creation"""
    try:
        company_name = getattr(doc, "company", None)
        if company_name:
            workspace_access_manager.assign_roles_for_company(company_name)
    except Exception as e:
        frappe.log_error(f"Error in assign_roles_to_new_user: {str(e)}")

def sync_onboarding_selection(doc, method=None):
    """Hook for onboarding form updates"""
    try:
        if getattr(doc, "status", "") == "Approved" and getattr(doc, "company_name", None):
            workspace_access_manager.assign_roles_for_company(doc.company_name)
    except Exception as e:
        frappe.log_error(f"Error in sync_onboarding_selection: {str(e)}")
