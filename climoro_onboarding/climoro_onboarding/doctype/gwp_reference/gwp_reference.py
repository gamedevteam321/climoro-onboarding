import frappe
from frappe.model.document import Document

class GWPReference(Document):
    """Global Warming Potential Reference Document"""
    
    def validate(self):
        """Validate the GWP reference data"""
        if not self.chemical_name:
            frappe.throw("Chemical Name is required")
        
        if not self.chemical_formula:
            frappe.throw("Chemical Formula is required")
        
        # Ensure at least one GWP value is provided
        if not any([
            self.gwp_ar4_100yr,
            self.gwp_ar5_100yr,
            self.gwp_ar6_100yr,
            self.gwp_ar6_20yr,
            self.gwp_ar6_500yr
        ]):
            frappe.throw("At least one GWP value must be provided")

@frappe.whitelist()
def get_gwp_value(chemical_name, assessment_report="AR6", time_horizon="100yr"):
    """
    Get GWP value for a specific chemical and assessment report
    
    Args:
        chemical_name (str): Name of the chemical
        assessment_report (str): IPCC Assessment Report (AR4, AR5, AR6)
        time_horizon (str): Time horizon (20yr, 100yr, 500yr)
    
    Returns:
        float: GWP value or None if not found
    """
    try:
        field_name = f"gwp_{assessment_report.lower()}_{time_horizon}"
        
        gwp_doc = frappe.get_doc("GWP Reference", {
            "chemical_name": chemical_name,
            "is_active": 1
        })
        
        return getattr(gwp_doc, field_name, None)
    except frappe.DoesNotExistError:
        return None

@frappe.whitelist()
def get_all_gwp_values(chemical_name):
    """
    Get all GWP values for a specific chemical
    
    Args:
        chemical_name (str): Name of the chemical
    
    Returns:
        dict: Dictionary containing all GWP values
    """
    try:
        gwp_doc = frappe.get_doc("GWP Reference", {
            "chemical_name": chemical_name,
            "is_active": 1
        })
        
        return {
            "chemical_name": gwp_doc.chemical_name,
            "chemical_formula": gwp_doc.chemical_formula,
            "gwp_ar4_100yr": gwp_doc.gwp_ar4_100yr,
            "gwp_ar5_100yr": gwp_doc.gwp_ar5_100yr,
            "gwp_ar6_100yr": gwp_doc.gwp_ar6_100yr,
            "gwp_ar6_20yr": gwp_doc.gwp_ar6_20yr,
            "gwp_ar6_500yr": gwp_doc.gwp_ar6_500yr,
            "ipcc_source": gwp_doc.ipcc_source
        }
    except frappe.DoesNotExistError:
        return None

@frappe.whitelist()
def get_common_refrigerants():
    """
    Get list of common refrigerants with their GWP values
    
    Returns:
        list: List of common refrigerants
    """
    common_refrigerants = [
        "R134a", "R404A", "R410A", "R407C", "R22", 
        "R507", "R717 (Ammonia)", "R744 (CO2)"
    ]
    
    result = []
    for refrigerant in common_refrigerants:
        gwp_values = get_all_gwp_values(refrigerant)
        if gwp_values:
            result.append(gwp_values)
    
    return result 