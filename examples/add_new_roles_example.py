#!/usr/bin/env python3
"""
Example script showing how to add new roles to the Climoro onboarding system.

This script demonstrates various ways to extend the role system to support
additional user types and access patterns.

Usage:
    bench execute climoro_onboarding.examples.add_new_roles_example.main
"""

import frappe
from climoro_onboarding.climoro_onboarding.role_management_utils import RoleManagementUtils

def main():
    """Main function to demonstrate adding new roles"""
    print("🌱 Climoro Role Extension Examples")
    print("=" * 50)
    
    # Example 1: Add Quality Manager Role
    print("\n1. Adding Quality Manager Role...")
    quality_result = add_quality_manager()
    print(f"   Result: {quality_result['message']}")
    
    # Example 2: Add Environmental Officer Role  
    print("\n2. Adding Environmental Officer Role...")
    env_result = add_environmental_officer()
    print(f"   Result: {env_result['message']}")
    
    # Example 3: Add Compliance Officer Role
    print("\n3. Adding Compliance Officer Role...")
    compliance_result = add_compliance_officer()
    print(f"   Result: {compliance_result['message']}")
    
    # Example 4: Add Scope 4 Access
    print("\n4. Adding Scope 4 (Avoided Emissions) Access...")
    scope4_result = add_scope4_access()
    print(f"   Result: {scope4_result['message']}")
    
    # Example 5: Add Water Management Scope
    print("\n5. Adding Water Management Scope...")
    water_result = add_water_management_scope()
    print(f"   Result: {water_result['message']}")
    
    # Example 6: Update Assigned User role options
    print("\n6. Updating Assigned User role options...")
    update_result = update_assigned_user_roles()
    print(f"   Result: {update_result['message']}")
    
    # Example 7: Validate configuration
    print("\n7. Validating configuration...")
    validation_result = validate_system()
    print(f"   Valid: {validation_result.get('valid', False)}")
    if validation_result.get('errors'):
        print(f"   Errors: {validation_result['errors']}")
    if validation_result.get('warnings'):
        print(f"   Warnings: {validation_result['warnings']}")
    
    print("\n✅ Role extension examples completed!")

def add_quality_manager():
    """Add Quality Manager role for quality assurance oversight"""
    return RoleManagementUtils.add_custom_role(
        role_name="Quality Manager",
        level=2,
        description="Quality management and assurance oversight for environmental data",
        can_manage_users=False,
        permissions=["read", "write", "submit", "report"],
        form_fields=["quality_management_enabled"],  # Would need to add this field to form
        workspaces=["Quality Dashboard"],
        modules=["Quality Management", "Setup"]
    )

def add_environmental_officer():
    """Add Environmental Officer role for regulatory compliance"""
    return RoleManagementUtils.add_custom_role(
        role_name="Environmental Officer", 
        level=2,
        description="Environmental compliance and regulatory reporting specialist",
        can_manage_users=False,
        permissions=["read", "write", "report", "export"],
        modules=["Environmental Compliance", "Setup"]
    )

def add_compliance_officer():
    """Add Compliance Officer role for audit and compliance activities"""
    return RoleManagementUtils.add_custom_role(
        role_name="Compliance Officer",
        level=2,
        description="Audit and compliance oversight with export capabilities",
        can_manage_users=False,
        permissions=["read", "write", "report", "export", "submit"],
        modules=["Compliance", "Audit", "Setup"]
    )

def add_scope4_access():
    """Add Scope 4 access for avoided emissions tracking"""
    return RoleManagementUtils.add_workspace_scope(
        scope_name="Scope 4 Access",
        form_field="scopes_to_report_scope4",  # Would need to add this to onboarding form
        workspace_label="Scope 4", 
        modules=["Scope 4", "Setup"],
        parent_scope="Scope 3 Access"  # Optional: link to parent scope
    )

def add_water_management_scope():
    """Add water management scope for water footprint tracking"""
    return RoleManagementUtils.add_workspace_scope(
        scope_name="Water Management Access",
        form_field="environmental_reporting_water",  # Would need to add this field
        workspace_label="Water Management",
        modules=["Water Management", "Environmental", "Setup"]
    )

def update_assigned_user_roles():
    """Update the Assigned User doctype with new role options"""
    new_roles = [
        "Quality Manager",
        "Environmental Officer", 
        "Compliance Officer"
    ]
    return RoleManagementUtils.update_assigned_user_roles(new_roles)

def validate_system():
    """Validate the current role configuration"""
    return RoleManagementUtils.validate_role_configuration()

# Industry-specific role examples
def add_manufacturing_roles():
    """Add roles specific to manufacturing companies"""
    results = []
    
    # Production Manager
    result = RoleManagementUtils.add_custom_role(
        role_name="Production Manager",
        level=2,
        description="Production oversight with emissions tracking responsibility",
        can_manage_users=False,
        permissions=["read", "write", "submit"],
        modules=["Production", "Scope 1", "Setup"]
    )
    results.append(("Production Manager", result))
    
    # Facilities Manager
    result = RoleManagementUtils.add_custom_role(
        role_name="Facilities Manager", 
        level=2,
        description="Facilities management with energy and utilities oversight",
        can_manage_users=False,
        permissions=["read", "write", "submit"],
        modules=["Facilities", "Scope 2", "Setup"]
    )
    results.append(("Facilities Manager", result))
    
    return results

def add_service_industry_roles():
    """Add roles specific to service industry companies"""
    results = []
    
    # Travel Coordinator
    result = RoleManagementUtils.add_custom_role(
        role_name="Travel Coordinator",
        level=3, 
        description="Business travel emissions tracking and reporting",
        can_manage_users=False,
        permissions=["read", "write"],
        modules=["Travel", "Scope 3", "Setup"]
    )
    results.append(("Travel Coordinator", result))
    
    # IT Manager
    result = RoleManagementUtils.add_custom_role(
        role_name="IT Manager",
        level=2,
        description="IT infrastructure emissions and energy management", 
        can_manage_users=False,
        permissions=["read", "write", "submit"],
        modules=["IT Infrastructure", "Scope 2", "Setup"]
    )
    results.append(("IT Manager", result))
    
    return results

# Example form field additions that would be needed
def get_required_form_fields():
    """
    Returns the form fields that would need to be added to the onboarding form
    to support the new roles and scopes defined above.
    """
    return {
        "quality_management_enabled": {
            "fieldtype": "Check",
            "label": "Enable Quality Management",
            "description": "Enable quality assurance and control processes"
        },
        "scopes_to_report_scope4": {
            "fieldtype": "Check", 
            "label": "Scope 4 (Avoided Emissions)",
            "description": "Track avoided emissions from products and services"
        },
        "environmental_reporting_water": {
            "fieldtype": "Check",
            "label": "Water Management",
            "description": "Track water usage and water footprint"
        },
        "industry_specific_manufacturing": {
            "fieldtype": "Check",
            "label": "Manufacturing Operations",
            "description": "Enable manufacturing-specific roles and workflows"
        },
        "industry_specific_services": {
            "fieldtype": "Check",
            "label": "Service Operations", 
            "description": "Enable service industry-specific roles and workflows"
        }
    }

# Example workspace definitions that would be needed
def get_required_workspaces():
    """
    Returns the workspace definitions that would need to be created
    to support the new scopes and roles.
    """
    return [
        {
            "label": "Quality Dashboard",
            "module": "Quality Management",
            "category": "Modules",
            "description": "Quality assurance dashboard and controls"
        },
        {
            "label": "Scope 4",
            "module": "Scope 4", 
            "category": "Modules",
            "parent_page": "Scope 3",
            "description": "Avoided emissions tracking and reporting"
        },
        {
            "label": "Water Management",
            "module": "Environmental",
            "category": "Modules", 
            "description": "Water usage and footprint management"
        },
        {
            "label": "Environmental Compliance",
            "module": "Environmental Compliance",
            "category": "Modules",
            "description": "Regulatory compliance and reporting"
        }
    ]

if __name__ == "__main__":
    main()
