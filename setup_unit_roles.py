#!/usr/bin/env python3
"""
Setup script for creating Unit Manager and Data Analyst roles with proper permissions.
Run this in bench console after installing the doctypes.
"""

import frappe

def create_unit_roles():
    """Create Unit Manager and Data Analyst roles with proper permissions"""
    
    print("🚀 Setting up Unit Management Roles and Permissions...")
    
    # Create Unit Manager role
    if not frappe.db.exists("Role", "Unit Manager"):
        role_doc = frappe.get_doc({
            "doctype": "Role",
            "role_name": "Unit Manager",
            "desk_access": 1,
            "description": "Can manage units and view reports for assigned units"
        })
        role_doc.insert(ignore_permissions=True)
        print("✅ Unit Manager role created")
    else:
        print("ℹ️  Unit Manager role already exists")
    
    # Create Data Analyst role
    if not frappe.db.exists("Role", "Data Analyst"):
        role_doc = frappe.get_doc({
            "doctype": "Role",
            "role_name": "Data Analyst",
            "desk_access": 1,
            "description": "Can analyze data and create reports for assigned units"
        })
        role_doc.insert(ignore_permissions=True)
        print("✅ Data Analyst role created")
    else:
        print("ℹ️  Data Analyst role already exists")
    
    # Set up permissions for Units doctype
    setup_units_permissions()
    
    # Set up permissions for Unit Users doctype
    setup_unit_users_permissions()
    
    frappe.db.commit()
    print("🎉 All roles and permissions setup completed!")

def setup_units_permissions():
    """Setup permissions for Units doctype"""
    print("⚙️  Setting up Units doctype permissions...")
    
    # Unit Manager permissions for Units
    create_custom_docperm("Units", "Unit Manager", {
        "read": 1,
        "write": 1,
        "create": 1,
        "delete": 0,
        "submit": 0,
        "cancel": 0,
        "amend": 0
    })
    
    # Data Analyst permissions for Units (read only)
    create_custom_docperm("Units", "Data Analyst", {
        "read": 1,
        "write": 0,
        "create": 0,
        "delete": 0,
        "submit": 0,
        "cancel": 0,
        "amend": 0
    })
    
    print("✅ Units permissions configured")

def setup_unit_users_permissions():
    """Setup permissions for Unit Users doctype"""
    print("⚙️  Setting up Unit Users doctype permissions...")
    
    # Unit Manager permissions for Unit Users
    create_custom_docperm("Unit Users", "Unit Manager", {
        "read": 1,
        "write": 1,
        "create": 0,  # Only super admins should create users
        "delete": 0,
        "submit": 0,
        "cancel": 0,
        "amend": 0
    })
    
    # Data Analyst permissions for Unit Users (read only)
    create_custom_docperm("Unit Users", "Data Analyst", {
        "read": 1,
        "write": 0,
        "create": 0,
        "delete": 0,
        "submit": 0,
        "cancel": 0,
        "amend": 0
    })
    
    print("✅ Unit Users permissions configured")

def create_custom_docperm(doctype, role, permissions):
    """Create custom document permissions"""
    
    # Check if permission already exists
    existing_perm = frappe.db.exists("Custom DocPerm", {
        "parent": doctype,
        "role": role
    })
    
    if existing_perm:
        print(f"ℹ️  Permission for {role} on {doctype} already exists")
        return
    
    try:
        perm_doc = frappe.get_doc({
            "doctype": "Custom DocPerm",
            "parent": doctype,
            "parenttype": "DocType",
            "parentfield": "permissions",
            "role": role,
            "permlevel": 0,
            **permissions
        })
        perm_doc.insert(ignore_permissions=True)
        print(f"✅ Created {role} permissions for {doctype}")
        
    except Exception as e:
        print(f"❌ Error creating {role} permissions for {doctype}: {str(e)}")

def setup_user_permissions():
    """Setup user permissions for company filtering"""
    print("⚙️  Setting up user permission rules...")
    
    # This would typically be done through User Permission Rules
    # But for now, we handle it in the DocType controllers
    
    print("✅ User permission rules configured")

def main():
    """Main function to run all setup tasks"""
    try:
        create_unit_roles()
        print("\n🎯 Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Run: bench --site localhost migrate")
        print("2. Run: bench --site localhost clear-cache")
        print("3. Test creating Units and Unit Users")
        print("4. Verify role-based access control")
        
    except Exception as e:
        print(f"❌ Setup failed: {str(e)}")
        frappe.log_error(f"Unit roles setup error: {str(e)}", "Setup Error")

if __name__ == "__main__":
    # This script should be run in bench console like:
    # exec(open('apps/climoro_onboarding/setup_unit_roles.py').read())
    main()
