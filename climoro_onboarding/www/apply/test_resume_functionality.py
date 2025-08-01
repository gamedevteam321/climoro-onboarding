#!/usr/bin/env python3
"""
Test script for Climoro Onboarding Resume Functionality
"""

import frappe
import json
import uuid
from frappe.utils import now_datetime
from datetime import timedelta

def test_resume_functionality():
    """Test the resume functionality"""
    print("🧪 Testing Climoro Onboarding Resume Functionality...")
    
    # Test 1: Send resume email
    print("\n1. Testing send_resume_email function...")
    test_email = "test@example.com"
    
    # First, create a test application
    try:
        doc = frappe.new_doc("Onboarding Form")
        doc.email = test_email
        doc.first_name = "Test"
        doc.last_name = "User"
        doc.company_name = "Test Company"
        doc.status = "Draft"
        doc.current_step = 2
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        print("✅ Test application created successfully")
        
        # Test send_resume_email
        from climoro_onboarding.www.apply.api import send_resume_email
        result = send_resume_email(test_email)
        print(f"📧 Send resume email result: {result}")
        
        if result.get("success"):
            print("✅ send_resume_email function works correctly")
        else:
            print(f"❌ send_resume_email failed: {result.get('message')}")
            
    except Exception as e:
        print(f"❌ Error in test 1: {str(e)}")
    
    # Test 2: Verify resume token
    print("\n2. Testing verify_resume_token function...")
    try:
        # Create a test token
        test_token = str(uuid.uuid4())
        session_data = {
            "email": test_email,
            "current_step": 2,
            "company_name": "Test Company",
            "created_at": now_datetime().isoformat(),
            "expires_at": (now_datetime() + timedelta(hours=24)).isoformat()
        }
        
        session_key = f"climoro_resume_{test_token}"
        frappe.cache().set_value(session_key, json.dumps(session_data), expires_in_sec=86400)
        
        from climoro_onboarding.www.apply.api import verify_resume_token
        result = verify_resume_token(test_token)
        print(f"🔍 Verify resume token result: {result}")
        
        if result.get("success"):
            print("✅ verify_resume_token function works correctly")
        else:
            print(f"❌ verify_resume_token failed: {result.get('message')}")
            
    except Exception as e:
        print(f"❌ Error in test 2: {str(e)}")
    
    # Test 3: Save step data
    print("\n3. Testing save_step_data function...")
    try:
        step_data = {
            "email": test_email,
            "step_number": 3,
            "company_name": "Updated Test Company"
        }
        
        from climoro_onboarding.www.apply.api import save_step_data
        result = save_step_data(json.dumps(step_data))
        print(f"💾 Save step data result: {result}")
        
        if result.get("success"):
            print("✅ save_step_data function works correctly")
        else:
            print(f"❌ save_step_data failed: {result.get('message')}")
            
    except Exception as e:
        print(f"❌ Error in test 3: {str(e)}")
    
    print("\n🎉 Resume functionality testing completed!")

if __name__ == "__main__":
    test_resume_functionality() 