#!/usr/bin/env python3
"""
Test script to verify module blocking functionality in onboarding approval
"""

import frappe
from frappe.utils import now

@frappe.whitelist()
def test_module_blocking_workflow():
    """Test the module blocking workflow by creating an Onboarding Form and approving it"""
    
    print("🧪 Testing Climoro Onboarding Module Blocking Workflow...")
    
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
    print("\n🚀 Testing approval workflow with module blocking...")
    
    try:
        # Approve the application
        onboarding_form.approve_application()
        
        print("✅ Approval successful!")
        print(f"   - Status: {onboarding_form.status}")
        print(f"   - Approved by: {onboarding_form.approved_by}")
        
        # Check results
        if frappe.db.exists("Company", onboarding_form.company_name):
            print(f"✅ Company created: {onboarding_form.company_name}")
        
        # Check main user and module blocking
        if frappe.db.exists("User", onboarding_form.email):
            main_user = frappe.get_doc("User", onboarding_form.email)
            print(f"✅ Main user created: {main_user.email}")
            print(f"   - Roles: {[role.role for role in main_user.roles]}")
            print(f"   - Blocked modules: {len(main_user.block_modules)}")
            
            # Verify module blocking
            if main_user.block_modules:
                print(f"   - Sample blocked modules: {[bm.module for bm in main_user.block_modules[:5]]}")
            else:
                print("   ❌ No modules blocked for main user!")
        
        # Check unit users and module blocking
        for unit in onboarding_form.units:
            if unit.assigned_users:
                for assigned_user in unit.assigned_users:
                    if frappe.db.exists("User", assigned_user.email):
                        user = frappe.get_doc("User", assigned_user.email)
                        print(f"✅ Unit user: {user.email} - Roles: {[role.role for role in user.roles]}")
                        print(f"   - Blocked modules: {len(user.block_modules)}")
                        
                        # Verify module blocking
                        if user.block_modules:
                            print(f"   - Sample blocked modules: {[bm.module for bm in user.block_modules[:5]]}")
                        else:
                            print("   ❌ No modules blocked for unit user!")
        
        # Test module access verification
        print("\n🔍 Testing module access verification...")
        test_module_access()
        
        print("\n🎉 Test completed successfully!")
        return {"success": True, "form_id": onboarding_form.name}
        
    except Exception as e:
        print(f"❌ Approval failed: {str(e)}")
        frappe.log_error(f"Module blocking test failed: {str(e)}")
        return {"success": False, "error": str(e)}

def test_module_access():
    """Test that users cannot access blocked modules"""
    
    # Get all available modules
    from frappe.config import get_modules_from_all_apps
    all_modules = get_modules_from_all_apps()
    all_module_names = [m.get("module_name") for m in all_modules if m.get("module_name")]
    
    print(f"   📊 Total available modules: {len(all_module_names)}")
    
    # Test with a specific user
    test_user_email = "unitmanager@climoro.com"
    if frappe.db.exists("User", test_user_email):
        user = frappe.get_doc("User", test_user_email)
        blocked_modules = [bm.module for bm in user.block_modules]
        
        print(f"   👤 User: {test_user_email}")
        print(f"   🚫 Blocked modules: {len(blocked_modules)}")
        print(f"   ✅ Available modules: {len(all_module_names) - len(blocked_modules)}")
        
        # Verify all modules are blocked
        if len(blocked_modules) == len(all_module_names):
            print("   ✅ All modules successfully blocked!")
        else:
            print(f"   ❌ Module blocking incomplete! Expected {len(all_module_names)}, got {len(blocked_modules)}")
            
            # Show missing blocked modules
            missing_modules = set(all_module_names) - set(blocked_modules)
            if missing_modules:
                print(f"   📋 Missing blocked modules: {list(missing_modules)[:10]}")

@frappe.whitelist()
def verify_existing_users_module_blocking():
    """Verify module blocking for existing users from previous onboarding approvals"""
    
    print("🔍 Verifying module blocking for existing users...")
    
    # Get all users created from onboarding forms
    onboarding_users = frappe.get_all(
        "User",
        filters={
            "company": ["like", "%Climoro%"],
            "enabled": 1
        },
        fields=["name", "email", "company", "roles"]
    )
    
    print(f"📊 Found {len(onboarding_users)} onboarding users to verify...")
    
    for user_data in onboarding_users:
        user = frappe.get_doc("User", user_data.name)
        blocked_modules = [bm.module for bm in user.block_modules]
        
        print(f"\n👤 User: {user.email}")
        print(f"   Company: {user.company}")
        print(f"   Roles: {[role.role for role in user.roles]}")
        print(f"   Blocked modules: {len(blocked_modules)}")
        
        if blocked_modules:
            print(f"   ✅ Module blocking active")
        else:
            print(f"   ❌ No modules blocked - applying blocking now...")
            
            # Apply module blocking
            from frappe.config import get_modules_from_all_apps
            all_modules = get_modules_from_all_apps()
            
            user.set("block_modules", [])
            for module_data in all_modules:
                module_name = module_data.get("module_name")
                if module_name:
                    user.append("block_modules", {"module": module_name})
            
            user.save(ignore_permissions=True)
            print(f"   ✅ Applied module blocking to {len(all_modules)} modules")
    
    print("\n✅ Module blocking verification completed!")

if __name__ == "__main__":
    # Run the test
    test_module_blocking_workflow() 