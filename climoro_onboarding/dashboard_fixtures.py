import frappe
import json
from frappe import _

def get_dashboard_charts():
    """Create dashboard charts for emissions tracking"""
    
    return [
        # 1. Emissions by Unit Type (Donut Chart)
        {
            "doctype": "Dashboard Chart",
            "chart_name": "Emissions by Unit Type",
            "chart_type": "Group By",
            "document_type": "Stationary Emissions",
            "type": "Donut",
            "group_by_based_on": "activity_types",
            "group_by_type": "Sum",
            "aggregate_function_based_on": "etco2eq",
            "number_of_groups": 5,
            "filters_json": json.dumps([
                ["Stationary Emissions", "date", ">=", "2024-01-01"],
                ["Stationary Emissions", "date", "<=", "2024-12-31"]
            ]),
            "is_public": 1,
            "color": "#1f77b4",
            "custom_options": json.dumps({
                "height": 300,
                "axisOptions": {"shortenYAxisNumbers": 1},
                "data": {
                    "labels": ["Factory/Manufacturing Plant", "Warehouse", "Offices", "Franchise", "Others"],
                    "datasets": [{
                        "name": "Emissions by Unit Type",
                        "values": [50, 24, 19, 3, 4]
                    }]
                }
            })
        },
        
        # 2. Scope 2 Emission (Bar Chart)
        {
            "doctype": "Dashboard Chart",
            "chart_name": "Scope 2 Emission",
            "chart_type": "Sum",
            "document_type": "Electricity Purchased",
            "type": "Bar",
            "timeseries": 1,
            "timespan": "Last Year",
            "time_interval": "Monthly",
            "based_on": "date",
            "value_based_on": "etco2eq",
            "filters_json": json.dumps([
                ["Electricity Purchased", "date", ">=", "2024-01-01"],
                ["Electricity Purchased", "date", "<=", "2024-12-31"]
            ]),
            "is_public": 1,
            "color": "#1f77b4",
            "custom_options": json.dumps({
                "height": 300,
                "axisOptions": {"shortenYAxisNumbers": 1}
            })
        },
        
        # 3. Scope 3 Emission (Bar Chart)
        {
            "doctype": "Dashboard Chart",
            "chart_name": "Scope 3 Emission",
            "chart_type": "Sum",
            "document_type": "Downstream Transportation Method",
            "type": "Bar",
            "timeseries": 1,
            "timespan": "Last Year",
            "time_interval": "Monthly",
            "based_on": "date",
            "value_based_on": "etco2eq",
            "filters_json": json.dumps([
                ["Downstream Transportation Method", "date", ">=", "2024-01-01"],
                ["Downstream Transportation Method", "date", "<=", "2024-12-31"]
            ]),
            "is_public": 1,
            "color": "#8b0000",
            "custom_options": json.dumps({
                "height": 300,
                "axisOptions": {"shortenYAxisNumbers": 1}
            })
        },
        
        # 4. Division of Emissions (Donut Chart)
        {
            "doctype": "Dashboard Chart",
            "chart_name": "Division of Emissions",
            "chart_type": "Group By",
            "document_type": "Stationary Emissions",
            "type": "Donut",
            "group_by_based_on": "fuel_type",
            "group_by_type": "Sum",
            "aggregate_function_based_on": "etco2eq",
            "number_of_groups": 2,
            "filters_json": json.dumps([
                ["Stationary Emissions", "date", ">=", "2024-01-01"],
                ["Stationary Emissions", "date", "<=", "2024-12-31"]
            ]),
            "is_public": 1,
            "color": "#8b0000",
            "custom_options": json.dumps({
                "height": 300,
                "axisOptions": {"shortenYAxisNumbers": 1},
                "data": {
                    "labels": ["Upstream Emission", "Downstream Emission"],
                    "datasets": [{
                        "name": "Division of Emissions",
                        "values": [70, 30]
                    }]
                }
            })
        },
        
        # 5. Production Capacity (Line Chart)
        {
            "doctype": "Dashboard Chart",
            "chart_name": "Production Capacity",
            "chart_type": "Sum",
            "document_type": "Stationary Emissions",
            "type": "Line",
            "timeseries": 1,
            "timespan": "Last Year",
            "time_interval": "Monthly",
            "based_on": "date",
            "value_based_on": "activity_data",
            "filters_json": json.dumps([
                ["Stationary Emissions", "date", ">=", "2024-01-01"],
                ["Stationary Emissions", "date", "<=", "2024-12-31"]
            ]),
            "is_public": 1,
            "color": "#1f77b4",
            "custom_options": json.dumps({
                "height": 300,
                "axisOptions": {"shortenYAxisNumbers": 1}
            })
        }
    ]

def get_number_cards():
    """Create number cards for key metrics"""
    
    return [
        {
            "doctype": "Number Card",
            "name": "Total Emissions 2024",
            "label": "Total Emissions (tCO2e)",
            "function": "Sum",
            "aggregate_function_based_on": "etco2eq",
            "document_type": "Stationary Emissions",
            "filters_json": json.dumps([
                ["Stationary Emissions", "date", ">=", "2024-01-01"],
                ["Stationary Emissions", "date", "<=", "2024-12-31"]
            ]),
            "is_public": 1,
            "color": "#1f77b4"
        },
        {
            "doctype": "Number Card",
            "name": "Scope 2 Total",
            "label": "Scope 2 Emissions (tCO2e)",
            "function": "Sum",
            "aggregate_function_based_on": "etco2eq",
            "document_type": "Electricity Purchased",
            "filters_json": json.dumps([
                ["Electricity Purchased", "date", ">=", "2024-01-01"],
                ["Electricity Purchased", "date", "<=", "2024-12-31"]
            ]),
            "is_public": 1,
            "color": "#ff7f0e"
        },
        {
            "doctype": "Number Card",
            "name": "Scope 3 Total",
            "label": "Scope 3 Emissions (tCO2e)",
            "function": "Sum",
            "aggregate_function_based_on": "etco2eq",
            "document_type": "Downstream Transportation Method",
            "filters_json": json.dumps([
                ["Downstream Transportation Method", "date", ">=", "2024-01-01"],
                ["Downstream Transportation Method", "date", "<=", "2024-12-31"]
            ]),
            "is_public": 1,
            "color": "#8b0000"
        }
    ] 