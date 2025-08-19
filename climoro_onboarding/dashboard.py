import frappe
from frappe import _

def get_stationary_emissions_dashboard(data=None):
    """Get dashboard data for Stationary Emissions"""
    return {
        "fieldname": "stationary_emissions",
        "non_standard_fieldnames": {
            "Company": "company"
        },
        "transactions": [
            {
                "label": _("Emissions"),
                "items": ["Stationary Emissions"]
            }
        ],
        "charts": [
            {
                "name": "Monthly Emissions",
                "chart_name": "Monthly Stationary Emissions",
                "chart_type": "Sum",
                "document_type": "Stationary Emissions",
                "type": "Bar",
                "timeseries": 1,
                "timespan": "Last Year",
                "time_interval": "Monthly",
                "based_on": "date",
                "value_based_on": "etco2eq"
            }
        ]
    }

def get_electricity_dashboard(data=None):
    """Get dashboard data for Electricity Purchased"""
    return {
        "fieldname": "electricity_purchased",
        "non_standard_fieldnames": {
            "Company": "company"
        },
        "transactions": [
            {
                "label": _("Scope 2"),
                "items": ["Electricity Purchased"]
            }
        ],
        "charts": [
            {
                "name": "Monthly Electricity Emissions",
                "chart_name": "Monthly Electricity Emissions",
                "chart_type": "Sum",
                "document_type": "Electricity Purchased",
                "type": "Bar",
                "timeseries": 1,
                "timespan": "Last Year",
                "time_interval": "Monthly",
                "based_on": "date",
                "value_based_on": "etco2eq"
            }
        ]
    }

def get_transportation_dashboard(data=None):
    """Get dashboard data for Downstream Transportation"""
    return {
        "fieldname": "downstream_transportation",
        "non_standard_fieldnames": {
            "Company": "company"
        },
        "transactions": [
            {
                "label": _("Scope 3"),
                "items": ["Downstream Transportation Method"]
            }
        ],
        "charts": [
            {
                "name": "Monthly Transportation Emissions",
                "chart_name": "Monthly Transportation Emissions",
                "chart_type": "Sum",
                "document_type": "Downstream Transportation Method",
                "type": "Bar",
                "timeseries": 1,
                "timespan": "Last Year",
                "time_interval": "Monthly",
                "based_on": "date",
                "value_based_on": "etco2eq"
            }
        ]
    } 