#!/usr/bin/env python3
"""
Setup script for Climoro Onboarding Units & Users Display
This script installs all the components for better display of units and users tables.
"""

import frappe
from frappe import _

def setup_units_display():
    """Setup all components for better units and users display"""
    
    print("🚀 Setting up Climoro Onboarding Units & Users Display...")
    print("=" * 60)
    
    try:
        # 1. Create the custom report
        create_custom_report()
        
        # 2. Create the dashboard page
        create_dashboard_page()
        
        # 3. Add virtual fields
        add_virtual_fields()
        
        # 4. Update list view settings
        update_list_view_settings()
        
        print("\n✅ Setup completed successfully!")
        print("\n📋 Available Features:")
        print("   • Enhanced List View with Units & Users Count")
        print("   • Custom Report: Units and Users Summary")
        print("   • Dashboard: /units-dashboard")
        print("   • Virtual Fields for filtering and sorting")
        
        print("\n🔗 Quick Links:")
        print("   • List View: /app/onboarding-form")
        print("   • Dashboard: /units-dashboard")
        print("   • Report: /app/units-and-users-summary")
        
    except Exception as e:
        print(f"❌ Setup failed: {str(e)}")
        frappe.log_error(f"Units display setup failed: {str(e)}")

def create_custom_report():
    """Create the custom report"""
    print("📊 Creating custom report...")
    
    if not frappe.db.exists("Report", "Units and Users Summary"):
        report_doc = frappe.get_doc({
            "doctype": "Report",
            "report_name": "Units and Users Summary",
            "ref_doctype": "Onboarding Form",
            "report_type": "Script Report",
            "module": "Climoro Onboarding",
            "is_standard": "No"
        })
        report_doc.insert()
        print("   ✅ Custom report created")
    else:
        print("   ℹ️  Custom report already exists")

def create_dashboard_page():
    """Create the dashboard page"""
    print("📈 Creating dashboard page...")
    
    if not frappe.db.exists("Page", "units-dashboard"):
        page_doc = frappe.get_doc({
            "doctype": "Page",
            "title": "Units & Users Dashboard",
            "module": "Climoro Onboarding",
            "standard": "No"
        })
        page_doc.insert()
        print("   ✅ Dashboard page created")
    else:
        print("   ℹ️  Dashboard page already exists")

def add_virtual_fields():
    """Add virtual fields for units and users count"""
    print("🔧 Adding virtual fields...")
    
    # Check if fields already exist
    existing_fields = frappe.get_meta("Onboarding Form").fields
    field_names = [field.fieldname for field in existing_fields]
    
    if "units_count" not in field_names:
        units_field = frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Onboarding Form",
            "fieldname": "units_count",
            "label": "Units Count",
            "fieldtype": "Int",
            "read_only": 1,
            "in_list_view": 1,
            "in_standard_filter": 1,
            "is_virtual": 1
        })
        units_field.insert()
        print("   ✅ Added units_count field")
    else:
        print("   ℹ️  units_count field already exists")
    
    if "users_count" not in field_names:
        users_field = frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Onboarding Form",
            "fieldname": "users_count",
            "label": "Users Count",
            "fieldtype": "Int",
            "read_only": 1,
            "in_list_view": 1,
            "in_standard_filter": 1,
            "is_virtual": 1
        })
        users_field.insert()
        print("   ✅ Added users_count field")
    else:
        print("   ℹ️  users_count field already exists")

def update_list_view_settings():
    """Update list view settings"""
    print("📋 Updating list view settings...")
    
    # Update the Onboarding Form doctype to include new fields in list view
    onboarding_form = frappe.get_doc("DocType", "Onboarding Form")
    current_list_fields = onboarding_form.list_fields or []
    
    if "units_count" not in current_list_fields:
        current_list_fields.append("units_count")
    
    if "users_count" not in current_list_fields:
        current_list_fields.append("users_count")
    
    onboarding_form.list_fields = current_list_fields
    onboarding_form.save()
    print("   ✅ List view settings updated")

if __name__ == "__main__":
    setup_units_display() 