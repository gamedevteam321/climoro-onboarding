import frappe
from typing import Dict, List, Optional
from climoro_onboarding.climoro_onboarding.enhanced_workspace_access import workspace_access_manager

class RoleManagementUtils:
    """
    Utility class for managing roles in the Climoro onboarding system.
    Provides easy-to-use methods for adding new roles and updating access permissions.
    """
    
    @staticmethod
    @frappe.whitelist()
    def add_custom_role(role_name: str, level: int, description: str, 
                       can_manage_users: bool = False, permissions: List[str] = None,
                       form_fields: List[str] = None, workspaces: List[str] = None,
                       modules: List[str] = None) -> Dict:
        """
        Add a custom role with specified permissions
        
        Args:
            role_name: Name of the new role
            level: Permission level (1=highest, 4=lowest)
            description: Description of the role
            can_manage_users: Whether this role can manage other users
            permissions: List of permissions for this role
            form_fields: List of form fields that should trigger this role
            workspaces: List of workspaces this role should access
            modules: List of modules this role should access
            
        Returns:
            Dict with success status and details
        """
        try:
            if permissions is None:
                permissions = ["read"]
            
            # Validate permission level
            if level not in [1, 2, 3, 4]:
                return {"success": False, "message": "Permission level must be 1, 2, 3, or 4"}
            
            # Create role configuration
            role_config = {
                "level": level,
                "description": description,
                "can_manage_users": can_manage_users,
                "default_scopes": [],
                "permissions": permissions
            }
            
            # Add the role
            success = workspace_access_manager.add_new_role(role_name, role_config)
            
            if not success:
                return {"success": False, "message": "Failed to create role"}
            
            # Add form field mappings if provided
            if form_fields:
                for field in form_fields:
                    workspace_access_manager.config['role_mappings'][field] = role_name
            
            # Add workspace mappings if provided
            if workspaces:
                for workspace in workspaces:
                    workspace_access_manager.config['workspace_mappings'][role_name] = workspace
            
            # Add module mappings if provided
            if modules:
                workspace_access_manager.config['module_mappings'][role_name] = modules
            
            # Save configuration
            workspace_access_manager._save_config()
            
            return {
                "success": True,
                "message": f"Successfully created role: {role_name}",
                "role_config": role_config
            }
            
        except Exception as e:
            frappe.log_error(f"Error creating custom role {role_name}: {str(e)}")
            return {"success": False, "message": f"Error: {str(e)}"}
    
    @staticmethod
    @frappe.whitelist()
    def add_workspace_scope(scope_name: str, form_field: str, workspace_label: str, 
                           modules: List[str] = None, parent_scope: str = None) -> Dict:
        """
        Add a new scope with associated workspace and modules
        
        Args:
            scope_name: Name of the scope (e.g., "Scope 4 Access")
            form_field: Form field that triggers this scope
            workspace_label: Workspace label to show
            modules: Modules to unblock for this scope
            parent_scope: Parent scope if this is a sub-scope
            
        Returns:
            Dict with success status and details
        """
        try:
            if modules is None:
                modules = ["Setup"]
            
            # Generate role name from scope name
            role_name = scope_name if scope_name.endswith(" Access") else f"{scope_name} Access"
            
            # Add the scope mapping
            success = workspace_access_manager.add_scope_mapping(
                form_field, role_name, workspace_label, modules
            )
            
            if not success:
                return {"success": False, "message": "Failed to create scope mapping"}
            
            # If this is a sub-scope, add it to the parent's dependencies
            if parent_scope:
                config = workspace_access_manager.config
                if 'scope_dependencies' not in config:
                    config['scope_dependencies'] = {}
                
                if parent_scope not in config['scope_dependencies']:
                    config['scope_dependencies'][parent_scope] = []
                
                config['scope_dependencies'][parent_scope].append(role_name)
                workspace_access_manager._save_config()
            
            return {
                "success": True,
                "message": f"Successfully created scope: {scope_name}",
                "mapping": {
                    "form_field": form_field,
                    "role_name": role_name,
                    "workspace_label": workspace_label,
                    "modules": modules
                }
            }
            
        except Exception as e:
            frappe.log_error(f"Error creating workspace scope {scope_name}: {str(e)}")
            return {"success": False, "message": f"Error: {str(e)}"}
    
    @staticmethod
    @frappe.whitelist()
    def update_assigned_user_roles(new_roles: List[str]) -> Dict:
        """
        Update the available roles in the Assigned User doctype
        
        Args:
            new_roles: List of role names to add to the select options
            
        Returns:
            Dict with success status
        """
        try:
            # Get the current Assigned User doctype
            doctype_doc = frappe.get_doc("DocType", "Assigned User")
            
            # Find the user_role field
            user_role_field = None
            for field in doctype_doc.fields:
                if field.fieldname == "user_role":
                    user_role_field = field
                    break
            
            if not user_role_field:
                return {"success": False, "message": "user_role field not found"}
            
            # Get current options
            current_options = user_role_field.options.split('\n') if user_role_field.options else []
            
            # Add new roles (avoid duplicates)
            for role in new_roles:
                if role not in current_options:
                    current_options.append(role)
            
            # Update the field options
            user_role_field.options = '\n'.join(current_options)
            
            # Save the doctype
            doctype_doc.save(ignore_permissions=True)
            
            return {
                "success": True,
                "message": f"Successfully updated role options",
                "available_roles": current_options
            }
            
        except Exception as e:
            frappe.log_error(f"Error updating assigned user roles: {str(e)}")
            return {"success": False, "message": f"Error: {str(e)}"}
    
    @staticmethod
    @frappe.whitelist()
    def get_role_hierarchy() -> Dict:
        """Get the current role hierarchy"""
        return workspace_access_manager.config.get('user_role_hierarchy', {})
    
    @staticmethod
    @frappe.whitelist()
    def get_scope_mappings() -> Dict:
        """Get the current scope mappings"""
        return {
            "role_mappings": workspace_access_manager.config.get('role_mappings', {}),
            "workspace_mappings": workspace_access_manager.config.get('workspace_mappings', {}),
            "module_mappings": workspace_access_manager.config.get('module_mappings', {})
        }
    
    @staticmethod
    @frappe.whitelist()
    def validate_role_configuration() -> Dict:
        """Validate the current role configuration"""
        try:
            config = workspace_access_manager.config
            errors = []
            warnings = []
            
            # Check for orphaned mappings
            role_mappings = config.get('role_mappings', {})
            workspace_mappings = config.get('workspace_mappings', {})
            module_mappings = config.get('module_mappings', {})
            
            # Check if all roles in mappings exist in hierarchy
            hierarchy_roles = set(config.get('user_role_hierarchy', {}).keys())
            
            for form_field, role in role_mappings.items():
                if role not in hierarchy_roles and not frappe.db.exists("Role", role):
                    warnings.append(f"Role '{role}' from form field '{form_field}' not found in hierarchy or system")
            
            for role in workspace_mappings.keys():
                if role not in hierarchy_roles and not frappe.db.exists("Role", role):
                    warnings.append(f"Role '{role}' in workspace mappings not found in hierarchy or system")
            
            # Check for missing workspace mappings
            for form_field, role in role_mappings.items():
                if role not in workspace_mappings:
                    errors.append(f"Role '{role}' (from field '{form_field}') has no workspace mapping")
            
            return {
                "success": True,
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "summary": {
                    "total_roles": len(hierarchy_roles),
                    "total_form_mappings": len(role_mappings),
                    "total_workspace_mappings": len(workspace_mappings),
                    "total_module_mappings": len(module_mappings)
                }
            }
            
        except Exception as e:
            return {"success": False, "message": f"Validation error: {str(e)}"}

# Convenience functions for common operations
@frappe.whitelist()
def add_quality_manager_role():
    """Example: Add a Quality Manager role"""
    return RoleManagementUtils.add_custom_role(
        role_name="Quality Manager",
        level=2,
        description="Quality management and assurance oversight",
        can_manage_users=False,
        permissions=["read", "write", "submit", "report"],
        modules=["Quality Management", "Setup"]
    )

@frappe.whitelist()
def add_scope_4_access():
    """Example: Add Scope 4 (avoided emissions) access"""
    return RoleManagementUtils.add_workspace_scope(
        scope_name="Scope 4 Access",
        form_field="scopes_to_report_scope4",
        workspace_label="Scope 4",
        modules=["Scope 4", "Setup"]
    )

@frappe.whitelist()
def add_compliance_officer_role():
    """Example: Add Compliance Officer role"""
    return RoleManagementUtils.add_custom_role(
        role_name="Compliance Officer",
        level=2,
        description="Regulatory compliance and reporting oversight",
        can_manage_users=False,
        permissions=["read", "write", "report", "export"],
        modules=["Compliance", "Setup"]
    )

# Quick setup function for common role additions
@frappe.whitelist()
def setup_extended_roles():
    """Setup common extended roles for the system"""
    results = []
    
    # Add Quality Manager
    result1 = add_quality_manager_role()
    results.append(("Quality Manager", result1))
    
    # Add Compliance Officer  
    result2 = add_compliance_officer_role()
    results.append(("Compliance Officer", result2))
    
    # Update Assigned User role options
    new_roles = ["Quality Manager", "Compliance Officer"]
    result3 = RoleManagementUtils.update_assigned_user_roles(new_roles)
    results.append(("Role Options Update", result3))
    
    return results
