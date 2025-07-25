import frappe
from frappe.utils import now

@frappe.whitelist()
def test_approval_workflow():
    """Test the approval workflow by creating an Onboarding Form and approving it"""
    
    print("🧪 Testing Climoro Onboarding Approval Workflow...")
    
    # Create test Onboarding Form
    print("📝 Creating test Onboarding Form...")
    
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
    onboarding_form.company_name = "Test Climoro Company"
    onboarding_form.address = "123 Test Street, Test City"
    onboarding_form.cin = "TEST123456"
    onboarding_form.gst_number = "TEST123456789"
    onboarding_form.industry_type = "Manufacturing"
    
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
        "email": "unitmanager@climoro.com",
        "first_name": "Unit Manager",
        "user_role": "Unit Manager"
    })
    
    unit1.append("assigned_users", {
        "email": "dataanalyst@climoro.com",
        "first_name": "Data Analyst",
        "user_role": "Data Analyst"
    })
    
    # Save the form
    onboarding_form.insert(ignore_permissions=True)
    frappe.db.commit()
    
    print(f"✅ Created Onboarding Form: {onboarding_form.name}")
    print(f"   - Company: {onboarding_form.company_name}")
    print(f"   - Main User: {onboarding_form.email}")
    print(f"   - Units: {len(onboarding_form.units)}")
    
    # Test approval
    print("\n🚀 Testing approval workflow...")
    
    try:
        # Approve the application
        onboarding_form.approve_application()
        
        print("✅ Approval successful!")
        print(f"   - Status: {onboarding_form.status}")
        print(f"   - Approved by: {onboarding_form.approved_by}")
        
        # Check results
        if frappe.db.exists("Company", onboarding_form.company_name):
            print(f"✅ Company created: {onboarding_form.company_name}")
        
        if frappe.db.exists("User", onboarding_form.email):
            main_user = frappe.get_doc("User", onboarding_form.email)
            print(f"✅ Main user created: {main_user.email}")
            print(f"   - Roles: {[role.role for role in main_user.roles]}")
        
        # Check unit users
        for unit in onboarding_form.units:
            if unit.assigned_users:
                for assigned_user in unit.assigned_users:
                    if frappe.db.exists("User", assigned_user.email):
                        user = frappe.get_doc("User", assigned_user.email)
                        print(f"✅ Unit user: {user.email} - Roles: {[role.role for role in user.roles]}")
        
        # Check Employee records
        employees = frappe.get_all("Employee", filters={"company": onboarding_form.company_name})
        print(f"✅ Employee records created: {len(employees)}")
        
        print("\n🎉 Test completed successfully!")
        return {"success": True, "form_id": onboarding_form.name}
        
    except Exception as e:
        print(f"❌ Approval failed: {str(e)}")
        frappe.log_error(f"Approval test failed: {str(e)}")
        return {"success": False, "error": str(e)} 