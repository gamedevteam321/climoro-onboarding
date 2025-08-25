import frappe
from frappe import _
from frappe.utils import get_url
from frappe.website.website_generator import WebsiteGenerator

class GHGReportsViewer(WebsiteGenerator):
    def get_context(self, context):
        """Get context for the GHG Reports Viewer page"""
        context.title = _("GHG Reports Viewer")
        context.no_cache = 1
        
        # Check if user is logged in
        if not frappe.session.user or frappe.session.user == "Guest":
            frappe.throw(_("Please log in to access this page."), frappe.PermissionError)
        
        # Get user info
        user = frappe.get_doc("User", frappe.session.user)
        context.user = user
        
        # Check if user is admin
        context.is_admin = frappe.has_permission("GHG Report", "read", user=user.name)
        
        # Get user's company
        context.user_company = user.company
        
        # Get companies list (admin sees all, user sees only their company)
        if context.is_admin:
            companies = frappe.get_all("Company", fields=["name", "company_name"], limit=1000)
        else:
            companies = [{"name": user.company, "company_name": user.company}] if user.company else []
        
        context.companies = companies
        
        return context

def get_ghg_reports(company=None, date_from=None, date_to=None, user=None):
    """Get GHG reports based on filters and user permissions"""
    try:
        # Build filters
        filters = {}
        
        # Company filter
        if company:
            filters["organization_name"] = company
        elif not frappe.has_permission("GHG Report", "read", user=user):
            # Non-admin users can only see their company's reports
            user_doc = frappe.get_doc("User", user)
            if user_doc.company:
                filters["organization_name"] = user_doc.company
        
        # Date filters
        if date_from:
            filters["period_from"] = [">=", date_from]
        if date_to:
            filters["period_to"] = ["<=", date_to]
        
        # Get reports
        reports = frappe.get_all(
            "GHG Report",
            fields=[
                "name", "report_title", "organization_name", "period_from", 
                "period_to", "docstatus", "creation", "modified"
            ],
            filters=filters,
            order_by="creation desc",
            limit=1000
        )
        
        return {"success": True, "reports": reports}
        
    except Exception as e:
        frappe.log_error(f"Error getting GHG reports: {str(e)}")
        return {"success": False, "message": str(e)}

@frappe.whitelist()
def get_reports_for_viewer(company=None, date_from=None, date_to=None):
    """API endpoint to get reports for the viewer"""
    return get_ghg_reports(
        company=company,
        date_from=date_from,
        date_to=date_to,
        user=frappe.session.user
    )

@frappe.whitelist()
def create_and_generate_ghg_report(report_title, organization_name, period_from, period_to):
    """Create a new GHG report and generate PDF"""
    try:
        # Check permissions
        if not frappe.has_permission("GHG Report", "create"):
            frappe.throw(_("You don't have permission to create GHG reports."))
        
        # Create the report
        report_doc = frappe.get_doc({
            "doctype": "GHG Report",
            "report_title": report_title,
            "organization_name": organization_name,
            "period_from": period_from,
            "period_to": period_to
        })
        
        report_doc.insert()
        
        # Generate PDF
        pdf_result = report_doc.generate_pdf()
        
        if pdf_result.get("success"):
            return {
                "success": True,
                "message": "Report created and PDF generated successfully",
                "report_name": report_doc.name,
                "file_url": pdf_result.get("file_url"),
                "file_name": pdf_result.get("file_name")
            }
        else:
            return {
                "success": False,
                "message": f"Report created but PDF generation failed: {pdf_result.get('message')}",
                "report_name": report_doc.name
            }
            
    except Exception as e:
        frappe.log_error(f"Error creating and generating GHG report: {str(e)}")
        return {"success": False, "message": str(e)}
