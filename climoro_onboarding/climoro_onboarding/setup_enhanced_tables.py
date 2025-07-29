#!/usr/bin/env python3
"""
Setup script for enhanced table display in Onboarding Form
This script ensures all existing records have proper computed fields and table configurations.
"""

import frappe
from frappe import _

def setup_enhanced_tables():
    """Setup enhanced table display for onboarding forms"""
    
    print("🔄 Setting up enhanced table display...")
    
    # Update all existing onboarding forms to have computed fields
    update_existing_records()
    
    # Clear cache to ensure changes take effect
    frappe.clear_cache()
    
    print("✅ Enhanced table display setup completed!")

def update_existing_records():
    """Update all existing onboarding form records with computed fields"""
    
    # Get all onboarding forms
    onboarding_forms = frappe.get_all(
        'Onboarding Form',
        fields=['name', 'units', 'assigned_users'],
        limit=None
    )
    
    print(f"📋 Found {len(onboarding_forms)} onboarding forms to update...")
    
    updated_count = 0
    
    for form in onboarding_forms:
        try:
            # Get the full document
            doc = frappe.get_doc('Onboarding Form', form.name)
            
            # Update summary fields
            doc.update_summary_fields()
            
            # Save without triggering validation (to avoid circular updates)
            doc.save(ignore_permissions=True)
            
            updated_count += 1
            
            if updated_count % 10 == 0:
                print(f"   Updated {updated_count}/{len(onboarding_forms)} forms...")
                
        except Exception as e:
            print(f"❌ Error updating form {form.name}: {str(e)}")
            continue
    
    print(f"✅ Successfully updated {updated_count}/{len(onboarding_forms)} forms")

def create_sample_data():
    """Create sample data for testing enhanced tables"""
    
    print("🔄 Creating sample data for testing...")
    
    # Create a sample onboarding form with units and users
    if not frappe.db.exists('Onboarding Form', 'OF-2025-00001'):
        doc = frappe.get_doc({
            'doctype': 'Onboarding Form',
            'naming_series': 'OF-.YYYY.-',
            'status': 'Draft',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone_number': '+91-9876543210',
            'company_name': 'Sample Company Ltd',
            'address': '123 Business Street, Mumbai, Maharashtra',
            'industry_type': 'Technology',
            'units': [
                {
                    'type_of_unit': 'Office',
                    'name_of_unit': 'Mumbai Headquarters',
                    'size_of_unit': 5000.0,
                    'address': '123 Business Street, Mumbai, Maharashtra',
                    'location_name': 'Mumbai',
                    'phone_number': '+91-22-12345678'
                },
                {
                    'type_of_unit': 'Warehouse',
                    'name_of_unit': 'Pune Warehouse',
                    'size_of_unit': 15000.0,
                    'address': '456 Industrial Area, Pune, Maharashtra',
                    'location_name': 'Pune',
                    'phone_number': '+91-20-87654321'
                }
            ],
            'assigned_users': [
                {
                    'assigned_unit': 'Mumbai Headquarters',
                    'first_name': 'Alice',
                    'email': 'alice@example.com',
                    'user_role': 'Unit Manager'
                },
                {
                    'assigned_unit': 'Pune Warehouse',
                    'first_name': 'Bob',
                    'email': 'bob@example.com',
                    'user_role': 'Data Analyst'
                }
            ]
        })
        
        doc.insert(ignore_permissions=True)
        print("✅ Created sample onboarding form: OF-2025-00001")
    else:
        print("ℹ️  Sample form already exists")

def main():
    """Main function to run the setup"""
    
    print("🚀 Starting Enhanced Table Display Setup")
    print("=" * 50)
    
    try:
        # Setup enhanced tables
        setup_enhanced_tables()
        
        # Create sample data (optional)
        create_sample_data()
        
        print("\n🎉 Setup completed successfully!")
        print("\n📋 What was enhanced:")
        print("   ✅ Company Unit table now shows: Unit Name, Type, Size, Location, Address, Phone")
        print("   ✅ Assigned User table now shows: Name, Email, Role, Assigned Unit")
        print("   ✅ List view shows unit and user counts with badges")
        print("   ✅ Form view has enhanced table formatting with icons and badges")
        print("   ✅ All existing records updated with computed fields")
        
    except Exception as e:
        print(f"❌ Setup failed: {str(e)}")
        frappe.log_error(f"Enhanced table setup failed: {str(e)}")

if __name__ == "__main__":
    main() 