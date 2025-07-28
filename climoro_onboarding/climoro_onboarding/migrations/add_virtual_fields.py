import frappe

def execute():
    """Add virtual fields for units and users count"""
    
    # Check if the fields already exist
    existing_fields = frappe.get_meta("Onboarding Form").fields
    field_names = [field.fieldname for field in existing_fields]
    
    if "units_count" not in field_names:
        # Add units_count virtual field
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Onboarding Form",
            "fieldname": "units_count",
            "label": "Units Count",
            "fieldtype": "Int",
            "read_only": 1,
            "in_list_view": 1,
            "in_standard_filter": 1,
            "is_virtual": 1
        }).insert()
    
    if "users_count" not in field_names:
        # Add users_count virtual field
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Onboarding Form",
            "fieldname": "users_count",
            "label": "Users Count",
            "fieldtype": "Int",
            "read_only": 1,
            "in_list_view": 1,
            "in_standard_filter": 1,
            "is_virtual": 1
        }).insert()
    
    frappe.db.commit()
    print("✅ Added virtual fields for units and users count") 