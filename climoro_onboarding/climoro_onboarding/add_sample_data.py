#!/usr/bin/env python3
"""
Add sample data to existing onboarding form for testing enhanced table display
"""

import frappe

def add_sample_data():
    """Add sample units and users to the existing onboarding form"""
    
    # Get the existing onboarding form
    if frappe.db.exists('Onboarding Form', 'OF-2025-00001'):
        doc = frappe.get_doc('Onboarding Form', 'OF-2025-00001')
        
        print(f"📋 Found existing form: {doc.name}")
        print(f"Current units: {len(doc.units)}")
        print(f"Current users: {len(doc.assigned_users)}")
        
        # Add sample units if none exist
        if len(doc.units) == 0:
            print("➕ Adding sample units...")
            
            # Add Mumbai Office
            doc.append('units', {
                'type_of_unit': 'Office',
                'name_of_unit': 'Mumbai Headquarters',
                'size_of_unit': 5000.0,
                'address': '123 Business Street, Mumbai, Maharashtra',
                'location_name': 'Mumbai',
                'phone_number': '+91-22-12345678'
            })
            
            # Add Pune Warehouse
            doc.append('units', {
                'type_of_unit': 'Warehouse',
                'name_of_unit': 'Pune Warehouse',
                'size_of_unit': 15000.0,
                'address': '456 Industrial Area, Pune, Maharashtra',
                'location_name': 'Pune',
                'phone_number': '+91-20-87654321'
            })
            
            # Add Bangalore Factory
            doc.append('units', {
                'type_of_unit': 'Factory',
                'name_of_unit': 'Bangalore Manufacturing',
                'size_of_unit': 25000.0,
                'address': '789 Industrial Zone, Bangalore, Karnataka',
                'location_name': 'Bangalore',
                'phone_number': '+91-80-98765432'
            })
            
            print("✅ Added 3 sample units")
        
        # Add sample users if none exist
        if len(doc.assigned_users) == 0:
            print("➕ Adding sample users...")
            
            # Add Unit Manager for Mumbai
            doc.append('assigned_users', {
                'assigned_unit': 'Mumbai Headquarters',
                'first_name': 'Alice Johnson',
                'email': 'alice.johnson@example.com',
                'user_role': 'Unit Manager'
            })
            
            # Add Data Analyst for Pune
            doc.append('assigned_users', {
                'assigned_unit': 'Pune Warehouse',
                'first_name': 'Bob Smith',
                'email': 'bob.smith@example.com',
                'user_role': 'Data Analyst'
            })
            
            # Add Unit Manager for Bangalore
            doc.append('assigned_users', {
                'assigned_unit': 'Bangalore Manufacturing',
                'first_name': 'Carol Davis',
                'email': 'carol.davis@example.com',
                'user_role': 'Unit Manager'
            })
            
            # Add Data Analyst for Mumbai
            doc.append('assigned_users', {
                'assigned_unit': 'Mumbai Headquarters',
                'first_name': 'David Wilson',
                'email': 'david.wilson@example.com',
                'user_role': 'Data Analyst'
            })
            
            print("✅ Added 4 sample users")
        
        # Save the document
        try:
            doc.save(ignore_permissions=True)
            print("💾 Saved changes successfully!")
            print(f"Final units: {len(doc.units)}")
            print(f"Final users: {len(doc.assigned_users)}")
            
            # Update summary fields
            doc.update_summary_fields()
            doc.save(ignore_permissions=True)
            print("📊 Updated summary fields")
            
        except Exception as e:
            print(f"❌ Error saving: {str(e)}")
            
    else:
        print("❌ Onboarding form OF-2025-00001 not found")

if __name__ == "__main__":
    add_sample_data() 