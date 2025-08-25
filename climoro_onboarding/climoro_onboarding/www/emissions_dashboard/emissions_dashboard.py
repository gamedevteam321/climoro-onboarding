import frappe
from frappe import _

def get_context(context):
    context.title = "Emissions Dashboard"
    context.no_cache = 1
    
    # Get dashboard configuration
    dashboard_config = get_dashboard_config()
    context.dashboard_config = dashboard_config

def get_dashboard_config():
    """Get dashboard configuration with charts and layout"""
    
    # Get all charts
    charts = frappe.get_all("Dashboard Chart", 
                           filters={"is_public": 1},
                           fields=["name", "chart_name", "type", "custom_options"])
    
    # Get number cards
    number_cards = frappe.get_all("Number Card",
                                 filters={"is_public": 1},
                                 fields=["name", "label", "function"])
    
    return {
        "charts": charts,
        "number_cards": number_cards,
        "layout": {
            "columns": 2,
            "chart_height": 300
        }
    } 