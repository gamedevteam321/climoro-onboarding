#!/usr/bin/env python3
"""
Installation script for GHG Reports Viewer
This script sets up the custom HTML page in Frappe
"""

import frappe
from frappe import _

def install_ghg_reports_viewer():
    """Install the GHG Reports Viewer page"""
    try:
        # Check if page already exists
        if frappe.db.exists("Page", "ghg_reports_viewer"):
            frappe.msgprint(_("GHG Reports Viewer page already exists. Skipping installation."))
            return
        
        # Create the page
        page_doc = frappe.get_doc({
            "doctype": "Page",
            "name": "ghg_reports_viewer",
            "title": "GHG Reports Viewer",
            "published": 1,
            "route": "ghg_reports_viewer",
            "content": "ghg_reports_viewer.html",
            "module": "climoro_onboarding",
            "icon": "chart-line",
            "description": "View and manage GHG reports with company filtering and PDF generation"
        })
        
        page_doc.insert()
        frappe.db.commit()
        
        frappe.msgprint(_("GHG Reports Viewer page installed successfully!"))
        frappe.msgprint(_("You can now access it at: /ghg_reports_viewer"))
        
    except Exception as e:
        frappe.log_error(f"Error installing GHG Reports Viewer: {str(e)}")
        frappe.throw(f"Error installing GHG Reports Viewer: {str(e)}")

def uninstall_ghg_reports_viewer():
    """Uninstall the GHG Reports Viewer page"""
    try:
        if frappe.db.exists("Page", "ghg_reports_viewer"):
            frappe.delete_doc("Page", "ghg_reports_viewer")
            frappe.db.commit()
            frappe.msgprint(_("GHG Reports Viewer page uninstalled successfully!"))
        else:
            frappe.msgprint(_("GHG Reports Viewer page not found."))
            
    except Exception as e:
        frappe.log_error(f"Error uninstalling GHG Reports Viewer: {str(e)}")
        frappe.throw(f"Error uninstalling GHG Reports Viewer: {str(e)}")

if __name__ == "__main__":
    install_ghg_reports_viewer()
