#!/usr/bin/env python3
"""
Test script to verify assigned users data structure
"""

import frappe

def verify_assigned_users_data():
    """Verify assigned users data in the latest form"""
    
    print("🔍 Verifying Assigned Users Data Structure")
    print("=" * 60)
    
    # Get the latest form
    latest_form = frappe.get_all(
        "Onboarding Form",
        fields=["name", "company_name", "email"],
        order_by="creation desc",
        limit=1
    )
    
    if not latest_form:
        print("❌ No onboarding forms found!")
        return
    
    form_name = latest_form[0].name
    print(f"📄 Latest Form: {form_name}")
    print(f"🏢 Company: {latest_form[0].company_name}")
    print(f"📧 Email: {latest_form[0].email}")
    
    # Get the full form document
    form = frappe.get_doc("Onboarding Form", form_name)
    
    print(f"\n📍 Units: {len(form.units)}")
    
    # Check each unit and its assigned users
    for i, unit in enumerate(form.units, 1):
        print(f"\n📍 Unit {i}: {unit.name_of_unit}")
        print(f"   Type: {unit.type_of_unit}")
        print(f"   Size: {unit.size_of_unit} sq ft")
        print(f"   Address: {unit.address}")
        
        # Check assigned users
        if hasattr(unit, 'assigned_users') and unit.assigned_users:
            print(f"   👥 Assigned Users: {len(unit.assigned_users)}")
            for j, user in enumerate(unit.assigned_users, 1):
                print(f"      {j}. {user.first_name} ({user.email}) - {user.user_role}")
        else:
            print(f"   👥 Assigned Users: 0 (No users found)")
    
    print("\n" + "=" * 60)
    print("💡 EXPLANATION:")
    print("   The assigned users are stored as CHILD TABLE entries within each unit.")
    print("   They are NOT standalone 'Assigned User' documents.")
    print("   This is why they don't appear in the 'Assigned User' list view.")
    print("\n   To see them in the UI:")
    print("   1. Go to the Onboarding Form document")
    print("   2. Click on the 'Units & Users' tab")
    print("   3. Click on a unit row to expand it")
    print("   4. The assigned users should appear below the unit details")
    
    print("\n" + "=" * 60)
    print("🔧 OPTIONS:")
    print("   Option 1: Keep current structure (child table entries)")
    print("   Option 2: Create standalone 'Assigned User' documents as well")
    print("   Option 3: Create a custom list view to show all assigned users")
    
    return form

if __name__ == "__main__":
    verify_assigned_users_data() 