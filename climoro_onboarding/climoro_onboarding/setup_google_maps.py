# Copyright (c) 2024, Climoro Onboarding and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def setup_google_maps():
	"""
	Setup Google Maps API key in site config
	"""
	try:
		# Check if API key already exists
		api_key = frappe.conf.get("google_maps_api_key")
		
		if api_key:
			frappe.msgprint({
				title: "Google Maps API Key Already Configured",
				message: f"API key is already set in site config. Current key: {api_key[:10]}...",
				indicator: "green"
			})
			return
		
		# Show instructions for setting up API key
		frappe.msgprint({
			title: "Google Maps Setup Required",
			message: """
			<h4>📋 Setup Instructions:</h4>
			<ol>
				<li>Go to <a href="https://console.cloud.google.com/" target="_blank">Google Cloud Console</a></li>
				<li>Create a new project or select existing one</li>
				<li>Enable the following APIs:
					<ul>
						<li>Maps JavaScript API</li>
						<li>Places API</li>
						<li>Geocoding API</li>
					</ul>
				</li>
				<li>Create credentials (API Key)</li>
				<li>Restrict the API key to your domain for security</li>
			</ol>
			
			<h4>🔧 Configuration:</h4>
			<p>Add the API key to your site config:</p>
			<code>bench --site your-site.com set-config google_maps_api_key "YOUR_API_KEY_HERE"</code>
			
			<h4>✅ After Setup:</h4>
			<p>Refresh this page and the map functionality will be available.</p>
			""",
			indicator: "blue"
		})
		
	except Exception as e:
		frappe.log_error(f"Error in Google Maps setup: {str(e)}", "Google Maps Setup Error")
		frappe.msgprint({
			title: "Setup Error",
			message: f"Error during setup: {str(e)}",
			indicator: "red"
		})

def get_google_maps_status():
	"""
	Get Google Maps configuration status
	"""
	try:
		api_key = frappe.conf.get("google_maps_api_key")
		
		if api_key:
			return {
				"configured": True,
				"api_key": api_key[:10] + "..." if len(api_key) > 10 else api_key,
				"message": "Google Maps is properly configured"
			}
		else:
			return {
				"configured": False,
				"message": "Google Maps API key not configured"
			}
			
	except Exception as e:
		frappe.log_error(f"Error checking Google Maps status: {str(e)}", "Google Maps Status Error")
		return {
			"configured": False,
			"message": f"Error checking status: {str(e)}"
		}

@frappe.whitelist()
def test_google_maps_configuration():
	"""
	Test Google Maps configuration
	"""
	try:
		status = get_google_maps_status()
		
		if status["configured"]:
			frappe.msgprint({
				title: "✅ Google Maps Configuration Test",
				message: f"Google Maps is properly configured with API key: {status['api_key']}",
				indicator: "green"
			})
		else:
			frappe.msgprint({
				title: "❌ Google Maps Configuration Test",
				message: status["message"],
				indicator: "red"
			})
			
	except Exception as e:
		frappe.log_error(f"Error testing Google Maps configuration: {str(e)}", "Google Maps Test Error")
		frappe.msgprint({
			title: "Test Error",
			message: f"Error during test: {str(e)}",
			indicator: "red"
		}) 