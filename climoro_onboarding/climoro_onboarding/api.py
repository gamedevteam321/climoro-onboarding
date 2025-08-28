import frappe
import requests

@frappe.whitelist()
def get_stationary_fuel_efs(fuel_type, fuel_name, unit_preference=None, region="IN"):
    """Get emission factors for stationary fuels - Pure Climatiq API"""
    
    try:
        # Check cache first
        cached = frappe.db.get_value(
            "EF Master",
            {"fuel_type": fuel_type, "fuel_name": fuel_name},
            ["name", "efco2_mass", "efch4_mass", "efn20_mass", "efco2_energy", "efch4_energy", "efn20_energy", 
             "efco2_liquid", "efch4_liquid", "efn20_liquid", "efco2_gas", "efch4_gas", "efn20_gas"],
            as_dict=True
        )
        
        if cached and cached.get("efco2_mass"):
            cached["source"] = "cache"
            return cached
        
        # Get API key - try different methods
        api_key = None
        
        # Method 1: From frappe.conf
        api_key = frappe.conf.get("climatiq_api_key")
        
        # Method 2: If not found, try from site config directly
        if not api_key:
            try:
                import json
                import os
                config_files = [
                    "/Users/vnshkumar/Documents/Frappe-test/frappe-bench/sites/localhost/site_config.json",
                    "/Users/vnshkumar/Documents/Frappe-test/frappe-bench/sites/common_site_config.json"
                ]
                
                for config_file in config_files:
                    if os.path.exists(config_file):
                        with open(config_file, 'r') as f:
                            config = json.load(f)
                            if "climatiq_api_key" in config:
                                api_key = config["climatiq_api_key"]
                                break
            except:
                pass
        
        if not api_key:
            return {
                "not_found": True,
                "error": "Climatiq API key not found in configuration"
            }
        
        # Search Climatiq API
        headers = {
            'Authorization': f'Bearer {api_key}'
        }
        
        # Multiple search strategies for the fuel
        search_terms = [
            fuel_name.lower(),
            f"{fuel_name.lower()} stationary",
            f"{fuel_name.lower()} combustion",
            fuel_name.lower().replace('/', ' ').replace(' ', '_'),
            fuel_name.lower().replace('liquefied', 'liquid'),
            fuel_name.lower().replace('petroleum gases', 'lpg'),
        ]
        
        found_factor = None
        
        for search_term in search_terms:
            try:
                # Search using GET method
                params = {
                    "query": search_term,
                    "category": "Fuel",
                    "data_version": "^6",
                    "results_per_page": 10
                }
                
                response = requests.get(
                    "https://api.climatiq.io/data/v1/search",
                    headers=headers,
                    params=params,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get('results', [])
                    
                    # Look for relevant results
                    for result in results:
                        name = result.get('name', '').lower()
                        activity_id = result.get('activity_id')
                        
                        # Check if this result is relevant to our fuel
                        fuel_keywords = fuel_name.lower().split()
                        if (any(keyword in name for keyword in fuel_keywords) or 
                            'stationary' in name or 'combustion' in name):
                            
                            # Test estimate endpoint
                            try:
                                estimate_data = {
                                    "emission_factor": {
                                        "activity_id": activity_id,
                                        "data_version": "^6"
                                    },
                                    "parameters": {
                                        "weight": 1,
                                        "weight_unit": "tonne"
                                    }
                                }
                                
                                est_response = requests.post(
                                    "https://api.climatiq.io/data/v1/estimate",
                                    headers={
                                        'Authorization': f'Bearer {api_key}',
                                        'Content-Type': 'application/json'
                                    },
                                    json=estimate_data,
                                    timeout=10
                                )
                                
                                if est_response.status_code == 200:
                                    est_data = est_response.json()
                                    co2e = est_data.get('co2e', 0)
                                    
                                    if co2e and co2e > 0:
                                        constituent_gases = est_data.get('constituent_gases', {})
                                        
                                        found_factor = {
                                            'activity_id': activity_id,
                                            'name': result.get('name'),
                                            'co2': constituent_gases.get('co2e_total', co2e),
                                            'ch4': constituent_gases.get('ch4e_total', 0),
                                            'n2o': constituent_gases.get('n2oe_total', 0),
                                            'total_co2e': co2e,
                                            'search_term': search_term
                                        }
                                        break
                            except:
                                continue
                    
                    if found_factor:
                        break
                        
                elif response.status_code == 401:
                    return {
                        "not_found": True,
                        "error": "Climatiq API authentication failed - invalid API key"
                    }
                    
            except:
                continue
        
        # If no factors found
        if not found_factor:
            return {
                "not_found": True,
                "error": f"No emission factors found in Climatiq for {fuel_name}"
            }
        
        # Convert to our format
        if fuel_type == "Gaseous fossil":
            result = {
                "fuel_type": fuel_type,
                "fuel_name": fuel_name,
                "efco2_mass": 0.0,
                "efch4_mass": 0.0,
                "efn20_mass": 0.0,
                "efco2_energy": found_factor['co2'],
                "efch4_energy": found_factor['ch4'],
                "efn20_energy": found_factor['n2o'],
                "efco2_liquid": 0.0,
                "efch4_liquid": 0.0,
                "efn20_liquid": 0.0,
                "efco2_gas": found_factor['co2'] / 1000,
                "efch4_gas": found_factor['ch4'] / 1000,
                "efn20_gas": found_factor['n2o'] / 1000,
                "source": "climatiq",
                "climatiq_activity_id": found_factor['activity_id']
            }
        elif fuel_type == "Liquid fossil":
            result = {
                "fuel_type": fuel_type,
                "fuel_name": fuel_name,
                "efco2_mass": found_factor['co2'],
                "efch4_mass": found_factor['ch4'],
                "efn20_mass": found_factor['n2o'],
                "efco2_energy": found_factor['co2'],
                "efch4_energy": found_factor['ch4'],
                "efn20_energy": found_factor['n2o'],
                "efco2_liquid": found_factor['co2'] / 1000,
                "efch4_liquid": found_factor['ch4'] / 1000,
                "efn20_liquid": found_factor['n2o'] / 1000,
                "efco2_gas": 0.0,
                "efch4_gas": 0.0,
                "efn20_gas": 0.0,
                "source": "climatiq",
                "climatiq_activity_id": found_factor['activity_id']
            }
        else:
            # Solid fuels and biomass
            result = {
                "fuel_type": fuel_type,
                "fuel_name": fuel_name,
                "efco2_mass": found_factor['co2'],
                "efch4_mass": found_factor['ch4'],
                "efn20_mass": found_factor['n2o'],
                "efco2_energy": found_factor['co2'],
                "efch4_energy": found_factor['ch4'],
                "efn20_energy": found_factor['n2o'],
                "efco2_liquid": 0.0,
                "efch4_liquid": 0.0,
                "efn20_liquid": 0.0,
                "efco2_gas": 0.0,
                "efch4_gas": 0.0,
                "efn20_gas": 0.0,
                "source": "climatiq",
                "climatiq_activity_id": found_factor['activity_id']
            }
        
        # Save to cache
        try:
            existing = frappe.db.get_value("EF Master", 
                {"fuel_type": fuel_type, "fuel_name": fuel_name}, "name")
            
            if not existing:
                save_data = {
                    "doctype": "EF Master",
                    "fuel_type": fuel_type,
                    "fuel_name": fuel_name,
                    "efco2": result["efco2_energy"],
                    "efch4": result["efch4_energy"],
                    "efn20": result["efn20_energy"],
                    "efco2_mass": result["efco2_mass"],
                    "efch4_mass": result["efch4_mass"],
                    "efn20_mass": result["efn20_mass"],
                    "efco2_energy": result["efco2_energy"],
                    "efch4_energy": result["efch4_energy"],
                    "efn20_energy": result["efn20_energy"],
                    "efco2_liquid": result["efco2_liquid"],
                    "efch4_liquid": result["efch4_liquid"],
                    "efn20_liquid": result["efn20_liquid"],
                    "efco2_gas": result["efco2_gas"],
                    "efch4_gas": result["efch4_gas"],
                    "efn20_gas": result["efn20_gas"]
                }
                doc = frappe.get_doc(save_data)
                doc.insert(ignore_permissions=True)
                frappe.db.commit()
        except:
            pass
        
        return result
        
    except Exception as e:
        return {
            "not_found": True,
            "error": f"Error: {str(e)[:100]}"
        }
