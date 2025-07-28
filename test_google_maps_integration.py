#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for Google Maps integration in Climoro Onboarding app
"""

import frappe
from frappe import _

def test_google_maps_integration():
    """
    Test the Google Maps integration functionality
    """
    print("🧪 Testing Google Maps Integration...")
    
    # Test 1: Check if API key is configured
    print("\n1. Testing API Key Configuration...")
    try:
        api_key = frappe.conf.get("google_maps_api_key")
        if api_key:
            print(f"✅ API Key found: {api_key[:10]}...")
        else:
            print("⚠️  API Key not configured")
            print("   Run: bench --site your-site.com set-config google_maps_api_key 'YOUR_API_KEY'")
    except Exception as e:
        print(f"❌ Error checking API key: {str(e)}")
    
    # Test 2: Check if doctypes have GPS coordinates field
    print("\n2. Testing Doctype Fields...")
    
    doctypes_to_check = [
        "Onboarding Form",
        "Company Unit", 
        "Assigned User"
    ]
    
    for doctype in doctypes_to_check:
        try:
            meta = frappe.get_meta(doctype)
            fields = [df.fieldname for df in meta.fields]
            
            if "gps_coordinates" in fields:
                print(f"✅ {doctype}: GPS coordinates field found")
            else:
                print(f"❌ {doctype}: GPS coordinates field missing")
        except Exception as e:
            print(f"❌ Error checking {doctype}: {str(e)}")
    
    # Test 3: Check if JavaScript file exists
    print("\n3. Testing JavaScript Files...")
    
    js_files = [
        "climoro_onboarding/doctype/onboarding_form/onboarding_form.js"
    ]
    
    for js_file in js_files:
        try:
            file_path = frappe.get_app_path("climoro_onboarding", js_file)
            with open(file_path, 'r') as f:
                content = f.read()
                if "google.maps" in content:
                    print(f"✅ {js_file}: Google Maps code found")
                else:
                    print(f"⚠️  {js_file}: Google Maps code not found")
        except Exception as e:
            print(f"❌ Error checking {js_file}: {str(e)}")
    
    # Test 4: Test API endpoint
    print("\n4. Testing API Endpoint...")
    try:
        from climoro_onboarding.climoro_onboarding.doctype.onboarding_form.onboarding_form import get_google_maps_api_key
        result = get_google_maps_api_key()
        if result.get("success"):
            print("✅ API endpoint working correctly")
        else:
            print(f"⚠️  API endpoint returned: {result.get('message')}")
    except Exception as e:
        print(f"❌ Error testing API endpoint: {str(e)}")
    
    # Test 5: Check if sample data can be created
    print("\n5. Testing Sample Data Creation...")
    try:
        # Create a test onboarding form
        test_form = frappe.get_doc({
            "doctype": "Onboarding Form",
            "company_name": "Test Company for Maps",
            "first_name": "Test User",
            "email": "test@example.com",
            "phone_number": "1234567890",
            "address": "Test Address",
            "gps_coordinates": "28.6139, 77.2090"  # New Delhi coordinates
        })
        
        # Don't actually save, just test if it can be created
        print("✅ Sample Onboarding Form can be created with GPS coordinates")
        
        # Test company unit
        test_unit = frappe.get_doc({
            "doctype": "Company Unit",
            "type_of_unit": "Office",
            "name_of_unit": "Test Unit",
            "size_of_unit": 1000,
            "address": "Test Unit Address",
            "gps_coordinates": "19.0760, 72.8777"  # Mumbai coordinates
        })
        
        print("✅ Sample Company Unit can be created with GPS coordinates")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {str(e)}")
    
    print("\n🎉 Google Maps Integration Test Complete!")
    print("\n📋 Next Steps:")
    print("1. Configure Google Maps API key if not done")
    print("2. Test the map functionality in the UI")
    print("3. Check browser console for any JavaScript errors")
    print("4. Verify map modal opens and functions correctly")

if __name__ == "__main__":
    test_google_maps_integration() 