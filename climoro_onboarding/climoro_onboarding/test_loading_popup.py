#!/usr/bin/env python3
"""
Test script to verify loading popup functionality
"""

import frappe
from frappe.utils import now

@frappe.whitelist()
def test_loading_popup_functionality():
    """Test that the loading popup shows correctly during approval process"""
    
    print("🧪 Testing Loading Popup Functionality...")
    
    # Create a test onboarding form
    print("📝 Creating test onboarding form...")
    
    onboarding_form = frappe.new_doc("Onboarding Form")
    onboarding_form.naming_series = "OF-.YYYY.-"
    onboarding_form.status = "Submitted"
    onboarding_form.current_step = 3
    onboarding_form.email_verified = 1
    onboarding_form.email_verified_at = now()
    
    # Contact Details
    onboarding_form.first_name = "Test User"
    onboarding_form.phone_number = "9876543210"
    onboarding_form.email = "test@climoro.com"
    onboarding_form.position = "CEO"
    
    # Company Details
    onboarding_form.company_name = "Test Loading Popup Company"
    onboarding_form.address = "123 Test Street, Test City"
    onboarding_form.cin = "TEST123456"
    onboarding_form.gst_number = "TEST123456789"
    onboarding_form.industry_type = "Technology"
    
    # Add one unit with users
    unit1 = onboarding_form.append("units", {
        "type_of_unit": "Office",
        "name_of_unit": "Main Office",
        "size_of_unit": 5000.0,
        "address": "456 Main Street, Test City",
        "gst": "UNIT1GST123"
    })
    
    # Add users to unit
    unit1.append("assigned_users", {
        "email": "testuser1@climoro.com",
        "first_name": "Test User 1",
        "user_role": "Unit Manager"
    })
    
    unit1.append("assigned_users", {
        "email": "testuser2@climoro.com",
        "first_name": "Test User 2",
        "user_role": "Data Analyst"
    })
    
    # Save the form
    onboarding_form.insert(ignore_permissions=True)
    frappe.db.commit()
    
    print(f"✅ Created test onboarding form: {onboarding_form.name}")
    print(f"   - Company: {onboarding_form.company_name}")
    print(f"   - Status: {onboarding_form.status}")
    print(f"   - Units: {len(onboarding_form.units)}")
    print(f"   - Users: {len(onboarding_form.units[0].assigned_users) if onboarding_form.units else 0}")
    
    print("\n🎯 Testing Instructions:")
    print("1. Go to the onboarding form in the UI")
    print("2. Click the 'Approve' button")
    print("3. You should see a loading popup with spinner")
    print("4. The popup should show 'Processing Onboarding Approval'")
    print("5. The popup should disappear when approval completes")
    
    print("\n🔗 Form URL:")
    print(f"   /app/onboarding-form/{onboarding_form.name}")
    
    print("\n📋 Expected Behavior:")
    print("   ✅ Loading popup appears immediately when Approve is clicked")
    print("   ✅ Spinner animation shows during processing")
    print("   ✅ Popup shows informative message about what's happening")
    print("   ✅ Popup disappears when approval completes")
    print("   ✅ Success/error message shows after popup disappears")
    
    return {
        "success": True,
        "form_id": onboarding_form.name,
        "form_url": f"/app/onboarding-form/{onboarding_form.name}",
        "message": "Test form created successfully. Please test the loading popup in the UI."
    }

@frappe.whitelist()
def test_reject_loading_popup():
    """Test that the loading popup shows correctly during rejection process"""
    
    print("🧪 Testing Reject Loading Popup Functionality...")
    
    # Find a submitted form to test rejection
    submitted_forms = frappe.get_all(
        "Onboarding Form",
        filters={"status": "Submitted"},
        fields=["name", "company_name"],
        limit=1
    )
    
    if not submitted_forms:
        print("❌ No submitted forms found for testing rejection")
        return {"success": False, "message": "No submitted forms found"}
    
    form = submitted_forms[0]
    print(f"✅ Found submitted form: {form.name}")
    print(f"   - Company: {form.company_name}")
    
    print("\n🎯 Testing Instructions:")
    print("1. Go to the onboarding form in the UI")
    print("2. Click the 'Reject' button")
    print("3. Enter a rejection reason")
    print("4. You should see a loading popup with red spinner")
    print("5. The popup should show 'Processing Application Rejection'")
    print("6. The popup should disappear when rejection completes")
    
    print("\n🔗 Form URL:")
    print(f"   /app/onboarding-form/{form.name}")
    
    print("\n📋 Expected Behavior:")
    print("   ✅ Loading popup appears after entering rejection reason")
    print("   ✅ Red spinner animation shows during processing")
    print("   ✅ Popup shows informative message about rejection")
    print("   ✅ Popup disappears when rejection completes")
    print("   ✅ Success/error message shows after popup disappears")
    
    return {
        "success": True,
        "form_id": form.name,
        "form_url": f"/app/onboarding-form/{form.name}",
        "message": "Test form found. Please test the rejection loading popup in the UI."
    }

if __name__ == "__main__":
    # Run the test
    test_loading_popup_functionality() 