#!/usr/bin/env python3
"""
Test script to verify assigned users are being saved correctly
"""

import frappe

def test_assigned_users_save():
    """Test that assigned users are saved correctly"""
    
    print("🧪 Testing Assigned Users Save Fix")
    print("=" * 50)
    
    # Create a test form with units and assigned users
    test_form = frappe.get_doc({
        "doctype": "Onboarding Form",
        "first_name": "Test User",
        "phone_number": "1234567890",
        "email": "test@example.com",
        "position": "Manager",
        "company_name": "Test Company",
        "address": "Test Address",
        "cin": "TEST123",
        "gst_number": "GST123",
        "industry_type": "Technology",
        "status": "Draft",
        "current_step": 3
    })
    
    # Add a unit with assigned users
    unit1 = test_form.append("units", {
        "type_of_unit": "Office",
        "name_of_unit": "Test Office",
        "size_of_unit": 1000,
        "address": "Test Unit Address",
        "gst": "UNIT123",
        "phone_number": "9876543210",
        "position": "Unit Manager"
    })
    
    # Add assigned users to the unit
    unit1.append("assigned_users", {
        "email": "user1@test.com",
        "first_name": "User One",
        "user_role": "Manufacturing Manager"
    })
    
    unit1.append("assigned_users", {
        "email": "user2@test.com",
        "first_name": "User Two",
        "user_role": "Analytics"
    })
    
    # Save the form
    test_form.insert()
    frappe.db.commit()
    
    print(f"✅ Created test form: {test_form.name}")
    
    # Reload the form to verify data is saved
    reloaded_form = frappe.get_doc("Onboarding Form", test_form.name)
    
    print(f"\n📊 Verification Results:")
    print(f"   Units: {len(reloaded_form.units)}")
    
    for i, unit in enumerate(reloaded_form.units, 1):
        print(f"\n   📍 Unit {i}: {unit.name_of_unit}")
        print(f"      Type: {unit.type_of_unit}")
        print(f"      Size: {unit.size_of_unit} sq ft")
        
        if hasattr(unit, 'assigned_users') and unit.assigned_users:
            print(f"      👥 Assigned Users: {len(unit.assigned_users)}")
            for j, user in enumerate(unit.assigned_users, 1):
                print(f"         {j}. {user.first_name} ({user.email}) - {user.user_role}")
        else:
            print(f"      👥 Assigned Users: 0 (❌ ISSUE: Users not saved!)")
    
    # Clean up
    frappe.delete_doc("Onboarding Form", test_form.name)
    frappe.db.commit()
    
    print(f"\n🧹 Cleaned up test form")
    print("=" * 50)
    
    return reloaded_form

if __name__ == "__main__":
    test_assigned_users_save() 