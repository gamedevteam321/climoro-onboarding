import frappe
from frappe import _
from frappe.utils import now, now_datetime, get_url
import uuid
import json
import os
import datetime
import time
from datetime import timedelta


@frappe.whitelist(allow_guest=True)
def submit_onboarding_form(form_data):
    """Submit the complete onboarding form"""
    try:
        # Handle JSON string data from frontend
        if isinstance(form_data, str):
            form_data = json.loads(form_data)
        
        # Debug logging for form data
        frappe.logger().info(f"🔍 Form Data Debug:")
        frappe.logger().info(f"   Form data keys: {list(form_data.keys())}")
        frappe.logger().info(f"   First name: '{form_data.get('first_name')}'")
        frappe.logger().info(f"   Middle name: '{form_data.get('middle_name')}'")
        frappe.logger().info(f"   Last name: '{form_data.get('last_name')}'")
        frappe.logger().info(f"   Last name type: {type(form_data.get('last_name'))}")
        frappe.logger().info(f"   Last name length: {len(form_data.get('last_name', ''))}")
        frappe.logger().info(f"   Phone number: '{form_data.get('phone_number')}'")
        frappe.logger().info(f"   Email: '{form_data.get('email')}'")
        frappe.logger().info(f"   Position: '{form_data.get('position')}'")
        
        # Check if last_name is empty and try to get it from saved data
        last_name = form_data.get('last_name')
        if not last_name or last_name.strip() == '':
            frappe.logger().info(f"⚠️ Last name is empty, trying to get from saved data")
            email = form_data.get("email")
            if email:
                # Try to get saved data for this email
                existing_applications = frappe.get_all(
                    "Onboarding Form",
                    filters={"email": email},
                    fields=["last_name"],
                    order_by="modified desc",
                    limit=1
                )
                if existing_applications and existing_applications[0].get('last_name'):
                    last_name = existing_applications[0].get('last_name')
                    frappe.logger().info(f"✅ Retrieved last_name from saved data: '{last_name}'")
                    form_data['last_name'] = last_name
                else:
                    frappe.logger().info(f"❌ No saved last_name found for email: {email}")
        
        # Debug logging for GPS coordinates
        frappe.logger().info(f"🔍 GPS Coordinates Debug:")
        frappe.logger().info(f"   GPS coordinates value: '{form_data.get('gps_coordinates')}'")
        frappe.logger().info(f"   GPS coordinates type: {type(form_data.get('gps_coordinates'))}")
        
        # Debug logging for industry fields
        frappe.logger().info(f"🔍 Industry Fields Debug:")
        frappe.logger().info(f"   Industry type: '{form_data.get('industry_type')}'")
        frappe.logger().info(f"   Sub-industry type: '{form_data.get('sub_industry_type')}'")
        frappe.logger().info(f"   All form_data keys: {list(form_data.keys())}")
        frappe.logger().info(f"   Form_data type: {type(form_data)}")
        
        email = form_data.get("email")
        
        # Check if there's an existing draft application for this email
        existing_applications = frappe.get_all(
            "Onboarding Form",
            filters={"email": email, "status": "Draft"},
            fields=["name", "current_step"],
            order_by="modified desc",
            limit=1
        )
        
        if existing_applications:
            # Update existing draft application
            existing_app = existing_applications[0]
            doc_name = existing_app["name"]
            
            frappe.logger().info(f"📝 Updating existing draft application: {doc_name}")
            
            # Update the existing document
            doc = frappe.get_doc("Onboarding Form", doc_name)
            
            # Update basic fields
            doc.first_name = form_data.get("first_name")
            doc.middle_name = form_data.get("middle_name")
            doc.last_name = form_data.get("last_name")
            doc.phone_number = form_data.get("phone_number")
            doc.position = form_data.get("position")
            doc.company_name = form_data.get("company_name")
            doc.address = form_data.get("address")
            doc.gps_coordinates = form_data.get("gps_coordinates")
            doc.location_name = form_data.get("location_name")
            frappe.logger().info(f"📍 Setting GPS coordinates on doc: '{form_data.get('gps_coordinates')}'")
            frappe.logger().info(f"📍 Setting location name on doc: '{form_data.get('location_name')}'")
            doc.cin = form_data.get("cin")
            doc.gst_number = form_data.get("gst_number")
            doc.industry_type = form_data.get("industry_type")
            doc.sub_industry_type = form_data.get("sub_industry_type")
            frappe.logger().info(f"🏭 Setting industry_type: '{form_data.get('industry_type')}'")
            frappe.logger().info(f"🏭 Setting sub_industry_type: '{form_data.get('sub_industry_type')}'")
            doc.website = form_data.get("website")
            doc.letter_of_authorisation = form_data.get("letter_of_authorisation")
            
            # GHG Accounting Fields (Step 4)
            frappe.logger().info(f"🌱 GHG Accounting Fields Debug:")
            frappe.logger().info(f"   Purpose of reporting: '{form_data.get('purpose_of_reporting')}'")
            
            # Individual gas checkboxes
            frappe.logger().info(f"   Gases to report CO2: '{form_data.get('gases_to_report_co2')}'")
            frappe.logger().info(f"   Gases to report CH4: '{form_data.get('gases_to_report_ch4')}'")
            frappe.logger().info(f"   Gases to report N2O: '{form_data.get('gases_to_report_n2o')}'")
            frappe.logger().info(f"   Gases to report HFCs: '{form_data.get('gases_to_report_hfcs')}'")
            frappe.logger().info(f"   Gases to report PFCs: '{form_data.get('gases_to_report_pfcs')}'")
            frappe.logger().info(f"   Gases to report SF6: '{form_data.get('gases_to_report_sf6')}'")
            frappe.logger().info(f"   Gases to report NF3: '{form_data.get('gases_to_report_nf3')}'")
            
            # Individual scope checkboxes
            frappe.logger().info(f"   Scopes to report Scope1: '{form_data.get('scopes_to_report_scope1')}'")
            frappe.logger().info(f"   Scopes to report Scope2: '{form_data.get('scopes_to_report_scope2')}'")
            frappe.logger().info(f"   Scopes to report Scope3: '{form_data.get('scopes_to_report_scope3')}'")
            frappe.logger().info(f"   Scopes to report Reductions: '{form_data.get('scopes_to_report_reductions')}'")
            
            # Individual scope options
            frappe.logger().info(f"   Scope 1 options Process: '{form_data.get('scope_1_options_process')}'")
            frappe.logger().info(f"   Scope 1 options Stationary: '{form_data.get('scope_1_options_stationary')}'")
            frappe.logger().info(f"   Scope 1 options Mobile: '{form_data.get('scope_1_options_mobile')}'")
            frappe.logger().info(f"   Scope 1 options Fugitive: '{form_data.get('scope_1_options_fugitive')}'")
            frappe.logger().info(f"   Scope 2 options Electricity: '{form_data.get('scope_2_options_electricity')}'")
            frappe.logger().info(f"   Scope 2 options Heating: '{form_data.get('scope_2_options_heating')}'")
            frappe.logger().info(f"   Scope 2 options Cooling: '{form_data.get('scope_2_options_cooling')}'")
            frappe.logger().info(f"   Scope 3 options Upstream: '{form_data.get('scope_3_options_upstream')}'")
            frappe.logger().info(f"   Scope 3 options Downstream: '{form_data.get('scope_3_options_downstream')}'")
            frappe.logger().info(f"   Reduction options Energy Efficiency: '{form_data.get('reduction_options_energy_efficiency')}'")
            frappe.logger().info(f"   Reduction options Renewable Energy: '{form_data.get('reduction_options_renewable_energy')}'")
            frappe.logger().info(f"   Reduction options Process Optimization: '{form_data.get('reduction_options_process_optimization')}'")
            frappe.logger().info(f"   Reduction options Waste Management: '{form_data.get('reduction_options_waste_management')}'")
            frappe.logger().info(f"   Reduction options Transportation: '{form_data.get('reduction_options_transportation')}'")
            frappe.logger().info(f"   Reduction options Other: '{form_data.get('reduction_options_other')}'")
            
            doc.purpose_of_reporting = form_data.get("purpose_of_reporting")
            
            # Individual gas checkboxes
            doc.gases_to_report_co2 = form_data.get("gases_to_report_co2")
            doc.gases_to_report_ch4 = form_data.get("gases_to_report_ch4")
            doc.gases_to_report_n2o = form_data.get("gases_to_report_n2o")
            doc.gases_to_report_hfcs = form_data.get("gases_to_report_hfcs")
            doc.gases_to_report_pfcs = form_data.get("gases_to_report_pfcs")
            doc.gases_to_report_sf6 = form_data.get("gases_to_report_sf6")
            doc.gases_to_report_nf3 = form_data.get("gases_to_report_nf3")
            
            # Individual scope checkboxes
            doc.scopes_to_report_scope1 = form_data.get("scopes_to_report_scope1")
            doc.scopes_to_report_scope2 = form_data.get("scopes_to_report_scope2")
            doc.scopes_to_report_scope3 = form_data.get("scopes_to_report_scope3")
            doc.scopes_to_report_reductions = form_data.get("scopes_to_report_reductions")
            
            # Individual scope 1 options
            doc.scope_1_options_process = form_data.get("scope_1_options_process")
            doc.scope_1_options_stationary = form_data.get("scope_1_options_stationary")
            doc.scope_1_options_mobile = form_data.get("scope_1_options_mobile")
            doc.scope_1_options_fugitive = form_data.get("scope_1_options_fugitive")
            
            # Individual scope 2 options
            doc.scope_2_options_electricity = form_data.get("scope_2_options_electricity")
            doc.scope_2_options_heating = form_data.get("scope_2_options_heating")
            doc.scope_2_options_cooling = form_data.get("scope_2_options_cooling")
            
            # Individual scope 3 options
            doc.scope_3_options_upstream = form_data.get("scope_3_options_upstream")
            doc.scope_3_options_downstream = form_data.get("scope_3_options_downstream")
            
            # Individual reduction options
            doc.reduction_options_energy_efficiency = form_data.get("reduction_options_energy_efficiency")
            doc.reduction_options_renewable_energy = form_data.get("reduction_options_renewable_energy")
            doc.reduction_options_process_optimization = form_data.get("reduction_options_process_optimization")
            doc.reduction_options_waste_management = form_data.get("reduction_options_waste_management")
            doc.reduction_options_transportation = form_data.get("reduction_options_transportation")
            doc.reduction_options_other = form_data.get("reduction_options_other")
            
            # Reduction Form Fields (Step 5) - Section A: Emissions Inventory Setup
            frappe.logger().info(f"🌱 Reduction Form Fields Debug:")
            frappe.logger().info(f"   Base year: '{form_data.get('base_year')}'")
            frappe.logger().info(f"   Base year reason: '{form_data.get('base_year_reason')}'")
            
            doc.base_year = form_data.get("base_year")
            doc.base_year_reason = form_data.get("base_year_reason")
            
            # Scopes Covered
            doc.scopes_covered_scope1 = form_data.get("scopes_covered_scope1")
            doc.scopes_covered_scope2 = form_data.get("scopes_covered_scope2")
            doc.scopes_covered_scope3 = form_data.get("scopes_covered_scope3")
            
            # GHG Boundary Approach
            doc.ghg_boundary_approach_operational_control = form_data.get("ghg_boundary_approach_operational_control")
            doc.ghg_boundary_approach_financial_control = form_data.get("ghg_boundary_approach_financial_control")
            doc.ghg_boundary_approach_equity_share = form_data.get("ghg_boundary_approach_equity_share")
            
            # Scope 3 Categories Included
            doc.scope_3_categories_purchased_goods = form_data.get("scope_3_categories_purchased_goods")
            doc.scope_3_categories_capital_goods = form_data.get("scope_3_categories_capital_goods")
            doc.scope_3_categories_fuel_energy = form_data.get("scope_3_categories_fuel_energy")
            doc.scope_3_categories_transportation = form_data.get("scope_3_categories_transportation")
            doc.scope_3_categories_waste = form_data.get("scope_3_categories_waste")
            doc.scope_3_categories_business_travel = form_data.get("scope_3_categories_business_travel")
            doc.scope_3_categories_use_sold_products = form_data.get("scope_3_categories_use_sold_products")
            doc.scope_3_categories_end_life_treatment = form_data.get("scope_3_categories_end_life_treatment")
            doc.scope_3_categories_leased_assets = form_data.get("scope_3_categories_leased_assets")
            
            doc.emissions_exclusions = form_data.get("emissions_exclusions")
            
            # Section B: Emissions Reduction Targets
            doc.target_type = form_data.get("target_type")
            doc.scope_1_2_intensity_percentage = form_data.get("scope_1_2_intensity_percentage")
            doc.scope_1_2_target_year = form_data.get("scope_1_2_target_year")
            doc.scope_3_intensity_percentage = form_data.get("scope_3_intensity_percentage")
            doc.scope_3_target_year = form_data.get("scope_3_target_year")
            doc.absolute_emissions_percentage = form_data.get("absolute_emissions_percentage")
            doc.near_term_target_year = form_data.get("near_term_target_year")
            doc.long_term_target_year = form_data.get("long_term_target_year")
            
            # Target Metrics
            doc.target_metrics_absolute_emissions = form_data.get("target_metrics_absolute_emissions")
            doc.target_metrics_kgco2e_mwh = form_data.get("target_metrics_kgco2e_mwh")
            doc.target_metrics_kgco2e_tonne = form_data.get("target_metrics_kgco2e_tonne")
            doc.target_metrics_kgco2e_unit_service = form_data.get("target_metrics_kgco2e_unit_service")
            doc.target_metrics_kgco2e_usd_revenue = form_data.get("target_metrics_kgco2e_usd_revenue")
            doc.target_metrics_kgco2e_stove_year = form_data.get("target_metrics_kgco2e_stove_year")
            doc.target_metrics_kgco2e_tonne_biochar = form_data.get("target_metrics_kgco2e_tonne_biochar")
            doc.target_metrics_kgco2e_km_travelled = form_data.get("target_metrics_kgco2e_km_travelled")
            
            # Target Boundary
            doc.target_boundary_scope1_2_95_percent = form_data.get("target_boundary_scope1_2_95_percent")
            doc.target_boundary_scope3_90_percent_long_term = form_data.get("target_boundary_scope3_90_percent_long_term")
            doc.target_boundary_scope3_67_percent_near_term = form_data.get("target_boundary_scope3_67_percent_near_term")
            doc.target_boundary_prioritize_relevance = form_data.get("target_boundary_prioritize_relevance")
            
            # Section C: Mitigation Strategies
            # Operational Emissions
            doc.operational_emissions_energy_efficiency = form_data.get("operational_emissions_energy_efficiency")
            doc.operational_emissions_onsite_renewable = form_data.get("operational_emissions_onsite_renewable")
            doc.operational_emissions_offsite_renewable = form_data.get("operational_emissions_offsite_renewable")
            doc.operational_emissions_fuel_switching = form_data.get("operational_emissions_fuel_switching")
            doc.operational_emissions_process_optimization = form_data.get("operational_emissions_process_optimization")
            
            # Value Chain Emissions
            doc.value_chain_emissions_supplier_engagement = form_data.get("value_chain_emissions_supplier_engagement")
            doc.value_chain_emissions_low_carbon_materials = form_data.get("value_chain_emissions_low_carbon_materials")
            doc.value_chain_emissions_redesign_use_phase = form_data.get("value_chain_emissions_redesign_use_phase")
            doc.value_chain_emissions_optimize_logistics = form_data.get("value_chain_emissions_optimize_logistics")
            doc.value_chain_emissions_circular_economy = form_data.get("value_chain_emissions_circular_economy")
            
            # Land Sector & Removals
            doc.land_sector_removals_afforestation = form_data.get("land_sector_removals_afforestation")
            doc.land_sector_removals_soil_carbon = form_data.get("land_sector_removals_soil_carbon")
            doc.land_sector_removals_urban_greening = form_data.get("land_sector_removals_urban_greening")
            doc.land_sector_removals_biochar = form_data.get("land_sector_removals_biochar")
            doc.land_sector_removals_carbon_capture = form_data.get("land_sector_removals_carbon_capture")
            doc.land_sector_removals_certified_removals = form_data.get("land_sector_removals_certified_removals")
            
            # Residual Emissions Strategy
            doc.residual_emissions_high_quality_credits = form_data.get("residual_emissions_high_quality_credits")
            doc.residual_emissions_bvcm = form_data.get("residual_emissions_bvcm")
            doc.residual_emissions_temporary_solutions = form_data.get("residual_emissions_temporary_solutions")
            
            # Section D: Monitoring, Adjustments & Reporting
            doc.monitoring_frequency = form_data.get("monitoring_frequency")
            doc.monitoring_frequency_other_text = form_data.get("monitoring_frequency_other_text")
            doc.assurance_validation = form_data.get("assurance_validation")
            
            # GHG Tracking Tools
            doc.ghg_tracking_tools_excel = form_data.get("ghg_tracking_tools_excel")
            doc.ghg_tracking_tools_software = form_data.get("ghg_tracking_tools_software")
            doc.ghg_tracking_tools_software_name = form_data.get("ghg_tracking_tools_software_name")
            doc.ghg_tracking_tools_web_platform = form_data.get("ghg_tracking_tools_web_platform")
            
            # Recalculation Policy
            doc.recalculation_policy_structural = form_data.get("recalculation_policy_structural")
            doc.recalculation_policy_methodology = form_data.get("recalculation_policy_methodology")
            doc.recalculation_policy_boundary = form_data.get("recalculation_policy_boundary")
            
            # Progress Communication
            doc.progress_communication_esg_dashboard = form_data.get("progress_communication_esg_dashboard")
            doc.progress_communication_sustainability_report = form_data.get("progress_communication_sustainability_report")
            doc.progress_communication_cdp_disclosure = form_data.get("progress_communication_cdp_disclosure")
            doc.progress_communication_sbti_registry = form_data.get("progress_communication_sbti_registry")
            
            frappe.logger().info(f"🌱 Step 5 Fields Debug:")
            frappe.logger().info(f"   Base year: '{form_data.get('base_year')}'")
            frappe.logger().info(f"   Target type: '{form_data.get('target_type')}'")
            frappe.logger().info(f"   Monitoring frequency: '{form_data.get('monitoring_frequency')}'")
            frappe.logger().info(f"   Assurance validation: '{form_data.get('assurance_validation')}'")
            frappe.logger().info(f"   Scopes covered scope1: '{form_data.get('scopes_covered_scope1')}'")
            frappe.logger().info(f"   Scopes covered scope2: '{form_data.get('scopes_covered_scope2')}'")
            frappe.logger().info(f"   Scopes covered scope3: '{form_data.get('scopes_covered_scope3')}'")
            frappe.logger().info(f"   GHG boundary operational: '{form_data.get('ghg_boundary_approach_operational_control')}'")
            frappe.logger().info(f"   GHG boundary financial: '{form_data.get('ghg_boundary_approach_financial_control')}'")
            frappe.logger().info(f"   GHG boundary equity: '{form_data.get('ghg_boundary_approach_equity_share')}'")
            frappe.logger().info(f"   Target metrics absolute: '{form_data.get('target_metrics_absolute_emissions')}'")
            frappe.logger().info(f"   Target metrics kgco2e_mwh: '{form_data.get('target_metrics_kgco2e_mwh')}'")
            frappe.logger().info(f"   Operational emissions energy: '{form_data.get('operational_emissions_energy_efficiency')}'")
            frappe.logger().info(f"   Value chain supplier: '{form_data.get('value_chain_emissions_supplier_engagement')}'")
            frappe.logger().info(f"   Land sector afforestation: '{form_data.get('land_sector_removals_afforestation')}'")
            frappe.logger().info(f"   Residual emissions bvcm: '{form_data.get('residual_emissions_bvcm')}'")
            frappe.logger().info(f"   GHG tracking excel: '{form_data.get('ghg_tracking_tools_excel')}'")
            frappe.logger().info(f"   GHG tracking software: '{form_data.get('ghg_tracking_tools_software')}'")
            frappe.logger().info(f"   Recalculation structural: '{form_data.get('recalculation_policy_structural')}'")
            frappe.logger().info(f"   Progress communication esg: '{form_data.get('progress_communication_esg_dashboard')}'")
            
            doc.status = "Submitted"
            doc.current_step = 5
            
            # Clear existing units and users before adding new ones
            doc.units = []
            doc.assigned_users = []
            
            # Add new units
            if form_data.get("units"):
                for unit_data in form_data["units"]:
                    # Debug logging for unit data
                    frappe.logger().info(f"🔍 Unit Data Debug:")
                    frappe.logger().info(f"   Unit name: {unit_data.get('name_of_unit')}")
                    frappe.logger().info(f"   GPS coordinates: {unit_data.get('gps_coordinates')}")
                    frappe.logger().info(f"   Location name: {unit_data.get('location_name')}")
                    # Create unit document
                    unit_doc = frappe.get_doc({
                        "doctype": "Company Unit",
                        "parent": doc.name,
                        "parenttype": "Onboarding Form",
                        "parentfield": "units",
                        "type_of_unit": unit_data.get("type_of_unit"),
                        "name_of_unit": unit_data.get("name_of_unit"),
                        "size_of_unit": unit_data.get("size_of_unit"),
                        "address": unit_data.get("address"),
                        "gps_coordinates": unit_data.get("gps_coordinates"),
                        "location_name": unit_data.get("location_name"),
                        "gst": unit_data.get("gst"),
                        "phone_number": unit_data.get("phone_number"),
                        "position": unit_data.get("position")
                    })
                    
                    # Append the unit to the parent
                    doc.append("units", unit_doc)
            
            # Add new users
            if form_data.get("assigned_users"):
                for user_data in form_data["assigned_users"]:
                    # Debug logging for user data
                    frappe.logger().info(f"🔍 User Data Debug:")
                    frappe.logger().info(f"   User email: {user_data.get('email')}")
                    frappe.logger().info(f"   Assigned unit: {user_data.get('assigned_unit')}")
                    # Create user document
                    user_doc = frappe.get_doc({
                        "doctype": "Assigned User",
                        "parent": doc.name,
                        "parenttype": "Onboarding Form",
                        "parentfield": "assigned_users",
                        "assigned_unit": user_data.get("assigned_unit"),  # Store unit name directly
                        "email": user_data.get("email"),
                        "first_name": user_data.get("first_name"),
                        "user_role": user_data.get("user_role")
                    })
                    
                    # Append the user to the parent
                    doc.append("assigned_users", user_doc)
            
            doc.save()
            frappe.db.commit()
            
            frappe.logger().info(f"✅ Successfully updated existing application: {doc.name}")
            
        else:
            # Create new application if no draft exists
            frappe.logger().info(f"🆕 Creating new application for email: {email}")
            
            # Create the main onboarding form
            doc = frappe.get_doc({
                "doctype": "Onboarding Form",
                "first_name": form_data.get("first_name"),
                "middle_name": form_data.get("middle_name"),
                "last_name": form_data.get("last_name"),
                "phone_number": form_data.get("phone_number"),
                "email": form_data.get("email"),
                "position": form_data.get("position"),
                "company_name": form_data.get("company_name"),
                "address": form_data.get("address"),
                "gps_coordinates": form_data.get("gps_coordinates"),
                "location_name": form_data.get("location_name"),
                "cin": form_data.get("cin"),
                "gst_number": form_data.get("gst_number"),
                "industry_type": form_data.get("industry_type"),
                "sub_industry_type": form_data.get("sub_industry_type"),
                "website": form_data.get("website"),
                "letter_of_authorisation": form_data.get("letter_of_authorisation"),
                
                # GHG Accounting Fields (Step 4)
                "purpose_of_reporting": form_data.get("purpose_of_reporting"),
                "gases_to_report": form_data.get("gases_to_report"),
                "scopes_to_report": form_data.get("scopes_to_report"),
                "scope_1_options": form_data.get("scope_1_options"),
                "scope_2_options": form_data.get("scope_2_options"),
                "scope_3_options": form_data.get("scope_3_options"),
                "reduction_options": form_data.get("reduction_options"),
                
                # Reduction Form Fields (Step 5)
                "base_year": form_data.get("base_year"),
                "base_year_reason": form_data.get("base_year_reason"),
                "ghg_boundary_approach": form_data.get("ghg_boundary_approach"),
                "emissions_exclusions": form_data.get("emissions_exclusions"),
                
                # Scope 1 Fields
                "scope_1_target_type": form_data.get("scope_1_target_type"),
                "scope_1_intensity_reduction": form_data.get("scope_1_intensity_reduction"),
                "scope_1_reduction_percentage": form_data.get("scope_1_reduction_percentage"),
                "scope_1_target_year": form_data.get("scope_1_target_year"),
                "scope_1_mitigation_strategies": form_data.get("scope_1_mitigation_strategies"),
                
                # Scope 2 Fields
                "scope_2_target_type": form_data.get("scope_2_target_type"),
                "scope_2_intensity_reduction": form_data.get("scope_2_intensity_reduction"),
                "scope_2_reduction_percentage": form_data.get("scope_2_reduction_percentage"),
                "scope_2_target_year": form_data.get("scope_2_target_year"),
                "scope_2_mitigation_strategies": form_data.get("scope_2_mitigation_strategies"),
                
                # Scope 3 Fields
                "scope_3_categories_included": form_data.get("scope_3_categories_included"),
                "scope_3_target_type": form_data.get("scope_3_target_type"),
                "scope_3_intensity_reduction": form_data.get("scope_3_intensity_reduction"),
                "scope_3_reduction_percentage": form_data.get("scope_3_reduction_percentage"),
                "scope_3_target_year": form_data.get("scope_3_target_year"),
                "scope_3_mitigation_strategies": form_data.get("scope_3_mitigation_strategies"),
                
                # Reductions Fields
                "reduction_target_type": form_data.get("reduction_target_type"),
                "land_sector_removals": form_data.get("land_sector_removals"),
                "residual_emissions_strategy": form_data.get("residual_emissions_strategy"),
                
                # Monitoring Fields
                "monitoring_frequency": form_data.get("monitoring_frequency"),
                "monitoring_frequency_other": form_data.get("monitoring_frequency_other"),
                "assurance_validation": form_data.get("assurance_validation"),
                "ghg_tracking_tools": form_data.get("ghg_tracking_tools"),
                "ghg_software_name": form_data.get("ghg_software_name"),
                "recalculation_policy": form_data.get("recalculation_policy"),
                "progress_communication": form_data.get("progress_communication"),
                
                # Step 6: Method of Calculation
                "method_of_calculation_option_a": form_data.get("method_of_calculation_option_a"),
                "method_of_calculation_option_b": form_data.get("method_of_calculation_option_b"),
                "method_of_calculation_option_c": form_data.get("method_of_calculation_option_c"),
                "method_of_calculation_option_d": form_data.get("method_of_calculation_option_d"),
                "method_of_calculation_option_e": form_data.get("method_of_calculation_option_e"),
                
                "status": "Submitted",
                "current_step": 6
            })
            
            frappe.logger().info(f"📍 Creating new doc with GPS coordinates: '{form_data.get('gps_coordinates')}'")
            doc.insert()
            
            # Add units
            if form_data.get("units"):
                for unit_data in form_data["units"]:
                    # Create unit as child table entry
                    unit_doc = doc.append("units", {
                        "type_of_unit": unit_data.get("type_of_unit"),
                        "name_of_unit": unit_data.get("name_of_unit"),
                        "size_of_unit": unit_data.get("size_of_unit"),
                        "address": unit_data.get("address"),
                        "gps_coordinates": unit_data.get("gps_coordinates"),
                        "location_name": unit_data.get("location_name"),
                        "gst": unit_data.get("gst"),
                        "phone_number": unit_data.get("phone_number"),
                        "position": unit_data.get("position")
                    })
            
            # Add users
            if form_data.get("assigned_users"):
                for user_data in form_data["assigned_users"]:
                    # Create the assigned user as a child table entry
                    doc.append("assigned_users", {
                        "assigned_unit": user_data.get("assigned_unit"),  # Store unit name directly
                        "email": user_data.get("email"),
                        "first_name": user_data.get("first_name"),
                        "user_role": user_data.get("user_role")
                    })
            
            frappe.logger().info(f"✅ Successfully created new application: {doc.name}")
        
        # Send admin notification
        doc.send_admin_notification()
        
        return {
            "success": True,
            "message": "Onboarding form submitted successfully!",
            "application_id": doc.name
        }
        
    except Exception as e:
        frappe.logger().error(f"❌ Error submitting onboarding form: {str(e)}")
        frappe.log_error(f"Error submitting onboarding form: {str(e)}", "Climoro Onboarding Error")
        return {
            "success": False,
            "message": f"Error submitting form: {str(e)}"
        }


@frappe.whitelist(allow_guest=True)
def get_existing_application(email):
    """Get existing application by email"""
    try:
        applications = frappe.get_all(
            "Onboarding Form",
            filters={"email": email},
            fields=["name", "status", "current_step", "modified"],
            order_by="modified desc",
            limit=1
        )
        
        if applications:
            return {
                "success": True,
                "application": applications[0]
            }
        else:
            return {
                "success": False,
                "message": "No existing application found"
            }
            
    except Exception as e:
        frappe.log_error(f"Error getting existing application: {str(e)}", "Climoro Onboarding Error")
        return {
            "success": False,
            "message": f"Error retrieving application: {str(e)}"
        }


@frappe.whitelist(allow_guest=True)
def save_step_data(step_data):
    """Save step data to existing draft application"""
    try:
        # Handle JSON string data from frontend
        if isinstance(step_data, str):
            step_data = json.loads(step_data)
        
        email = step_data.get("email")
        step_number = step_data.get("step_number")
        
        # Find existing draft application
        existing_applications = frappe.get_all(
            "Onboarding Form",
            filters={"email": email, "status": "Draft"},
            fields=["name", "current_step"],
            order_by="modified desc",
            limit=1
        )
        
        if not existing_applications:
            return {
                "success": False,
                "message": "No draft application found. Please start from Step 1."
            }
        
        existing_app = existing_applications[0]
        doc_name = existing_app["name"]
        
        # Update the existing document
        doc = frappe.get_doc("Onboarding Form", doc_name)
        
        # Update fields based on step number
        if step_number == 1:
            # Step 1: Contact Details
            doc.first_name = step_data.get("first_name")
            doc.middle_name = step_data.get("middle_name")
            doc.last_name = step_data.get("last_name")
            doc.phone_number = step_data.get("phone_number")
            doc.email = step_data.get("email")
            doc.position = step_data.get("position")
            doc.current_step = 1
            
        elif step_number == 2:
            # Step 2: Company Details
            doc.company_name = step_data.get("company_name")
            doc.address = step_data.get("address")
            doc.gps_coordinates = step_data.get("gps_coordinates")
            doc.location_name = step_data.get("location_name")
            frappe.logger().info(f"📍 Setting GPS coordinates on doc: '{step_data.get('gps_coordinates')}'")
            frappe.logger().info(f"📍 Setting location name on doc: '{step_data.get('location_name')}'")
            doc.cin = step_data.get("cin")
            doc.gst_number = step_data.get("gst_number")
            doc.industry_type = step_data.get("industry_type")
            doc.sub_industry_type = step_data.get("sub_industry_type")
            doc.website = step_data.get("website")
            doc.letter_of_authorisation = step_data.get("letter_of_authorisation")
            doc.current_step = 2
            
        elif step_number == 3:
            # Step 3: Units & Users
            # Clear existing units and users
            doc.units = []
            doc.assigned_users = []
            
            # Add new units
            if step_data.get("units"):
                for unit_data in step_data["units"]:
                    # Debug logging for unit data in step save
                    frappe.logger().info(f"🔍 Step Unit Data Debug:")
                    frappe.logger().info(f"   Unit name: {unit_data.get('name_of_unit')}")
                    frappe.logger().info(f"   GPS coordinates: {unit_data.get('gps_coordinates')}")
                    frappe.logger().info(f"   Location name: {unit_data.get('location_name')}")
                    # Create unit as child table entry
                    unit_doc = doc.append("units", {
                        "type_of_unit": unit_data.get("type_of_unit"),
                        "name_of_unit": unit_data.get("name_of_unit"),
                        "size_of_unit": unit_data.get("size_of_unit"),
                        "address": unit_data.get("address"),
                        "gps_coordinates": unit_data.get("gps_coordinates"),
                        "location_name": unit_data.get("location_name"),
                        "gst": unit_data.get("gst"),
                        "phone_number": unit_data.get("phone_number"),
                        "position": unit_data.get("position")
                    })
            
            # Add new users
            if step_data.get("assigned_users"):
                for user_data in step_data["assigned_users"]:
                    # Debug logging for user data in step save
                    frappe.logger().info(f"🔍 Step User Data Debug:")
                    frappe.logger().info(f"   User email: {user_data.get('email')}")
                    frappe.logger().info(f"   Assigned unit: {user_data.get('assigned_unit')}")
                    # Create user as child table entry
                    doc.append("assigned_users", {
                        "assigned_unit": user_data.get("assigned_unit"),
                        "email": user_data.get("email"),
                        "first_name": user_data.get("first_name"),
                        "user_role": user_data.get("user_role")
                    })
            
            doc.current_step = 3
            
        elif step_number == 4:
            # Step 4: GHG Accounting
            doc.purpose_of_reporting = step_data.get("purpose_of_reporting")
            
            # Individual gas checkboxes
            doc.gases_to_report_co2 = step_data.get("gases_to_report_co2")
            doc.gases_to_report_ch4 = step_data.get("gases_to_report_ch4")
            doc.gases_to_report_n2o = step_data.get("gases_to_report_n2o")
            doc.gases_to_report_hfcs = step_data.get("gases_to_report_hfcs")
            doc.gases_to_report_pfcs = step_data.get("gases_to_report_pfcs")
            doc.gases_to_report_sf6 = step_data.get("gases_to_report_sf6")
            doc.gases_to_report_nf3 = step_data.get("gases_to_report_nf3")
            
            # Individual scope checkboxes
            doc.scopes_to_report_scope1 = step_data.get("scopes_to_report_scope1")
            doc.scopes_to_report_scope2 = step_data.get("scopes_to_report_scope2")
            doc.scopes_to_report_scope3 = step_data.get("scopes_to_report_scope3")
            doc.scopes_to_report_reductions = step_data.get("scopes_to_report_reductions")
            
            # Individual scope 1 options
            doc.scope_1_options_process = step_data.get("scope_1_options_process")
            doc.scope_1_options_stationary = step_data.get("scope_1_options_stationary")
            doc.scope_1_options_mobile = step_data.get("scope_1_options_mobile")
            doc.scope_1_options_fugitive = step_data.get("scope_1_options_fugitive")
            
            # Individual scope 2 options
            doc.scope_2_options_electricity = step_data.get("scope_2_options_electricity")
            doc.scope_2_options_heating = step_data.get("scope_2_options_heating")
            doc.scope_2_options_cooling = step_data.get("scope_2_options_cooling")
            
            # Individual scope 3 options
            doc.scope_3_options_upstream = step_data.get("scope_3_options_upstream")
            doc.scope_3_options_downstream = step_data.get("scope_3_options_downstream")
            
            # Individual reduction options
            doc.reduction_options_energy_efficiency = step_data.get("reduction_options_energy_efficiency")
            doc.reduction_options_renewable_energy = step_data.get("reduction_options_renewable_energy")
            doc.reduction_options_process_optimization = step_data.get("reduction_options_process_optimization")
            doc.reduction_options_waste_management = step_data.get("reduction_options_waste_management")
            doc.reduction_options_transportation = step_data.get("reduction_options_transportation")
            doc.reduction_options_other = step_data.get("reduction_options_other")
            
            doc.current_step = 4
            
        elif step_number == 5:
            # Step 5: Reduction Form
            # Section A: Emissions Inventory Setup
            doc.base_year = step_data.get("base_year")
            doc.base_year_reason = step_data.get("base_year_reason")
            doc.emissions_exclusions = step_data.get("emissions_exclusions")
            
            # Scopes Covered
            doc.scopes_covered_scope1 = step_data.get("scopes_covered_scope1")
            doc.scopes_covered_scope2 = step_data.get("scopes_covered_scope2")
            doc.scopes_covered_scope3 = step_data.get("scopes_covered_scope3")
            
            # GHG Boundary Approach
            doc.ghg_boundary_approach_operational_control = step_data.get("ghg_boundary_approach_operational_control")
            doc.ghg_boundary_approach_financial_control = step_data.get("ghg_boundary_approach_financial_control")
            doc.ghg_boundary_approach_equity_share = step_data.get("ghg_boundary_approach_equity_share")
            
            # Scope 3 Categories Included
            doc.scope_3_categories_purchased_goods = step_data.get("scope_3_categories_purchased_goods")
            doc.scope_3_categories_capital_goods = step_data.get("scope_3_categories_capital_goods")
            doc.scope_3_categories_fuel_energy = step_data.get("scope_3_categories_fuel_energy")
            doc.scope_3_categories_transportation = step_data.get("scope_3_categories_transportation")
            doc.scope_3_categories_waste = step_data.get("scope_3_categories_waste")
            doc.scope_3_categories_business_travel = step_data.get("scope_3_categories_business_travel")
            doc.scope_3_categories_use_sold_products = step_data.get("scope_3_categories_use_sold_products")
            doc.scope_3_categories_end_life_treatment = step_data.get("scope_3_categories_end_life_treatment")
            doc.scope_3_categories_leased_assets = step_data.get("scope_3_categories_leased_assets")
            
            # Section B: Emissions Reduction Targets
            doc.target_type = step_data.get("target_type")
            doc.scope_1_2_intensity_percentage = step_data.get("scope_1_2_intensity_percentage")
            doc.scope_1_2_target_year = step_data.get("scope_1_2_target_year")
            doc.scope_3_intensity_percentage = step_data.get("scope_3_intensity_percentage")
            doc.scope_3_target_year = step_data.get("scope_3_target_year")
            doc.absolute_emissions_percentage = step_data.get("absolute_emissions_percentage")
            doc.near_term_target_year = step_data.get("near_term_target_year")
            doc.long_term_target_year = step_data.get("long_term_target_year")
            
            # Target Metrics
            doc.target_metrics_absolute_emissions = step_data.get("target_metrics_absolute_emissions")
            doc.target_metrics_kgco2e_mwh = step_data.get("target_metrics_kgco2e_mwh")
            doc.target_metrics_kgco2e_tonne = step_data.get("target_metrics_kgco2e_tonne")
            doc.target_metrics_kgco2e_unit_service = step_data.get("target_metrics_kgco2e_unit_service")
            doc.target_metrics_kgco2e_usd_revenue = step_data.get("target_metrics_kgco2e_usd_revenue")
            doc.target_metrics_kgco2e_stove_year = step_data.get("target_metrics_kgco2e_stove_year")
            doc.target_metrics_kgco2e_tonne_biochar = step_data.get("target_metrics_kgco2e_tonne_biochar")
            doc.target_metrics_kgco2e_km_travelled = step_data.get("target_metrics_kgco2e_km_travelled")
            
            # Target Boundary
            doc.target_boundary_scope1_2_95_percent = step_data.get("target_boundary_scope1_2_95_percent")
            doc.target_boundary_scope3_90_percent_long_term = step_data.get("target_boundary_scope3_90_percent_long_term")
            doc.target_boundary_scope3_67_percent_near_term = step_data.get("target_boundary_scope3_67_percent_near_term")
            doc.target_boundary_prioritize_relevance = step_data.get("target_boundary_prioritize_relevance")
            
            # Section C: Mitigation Strategies
            # Operational Emissions
            doc.operational_emissions_energy_efficiency = step_data.get("operational_emissions_energy_efficiency")
            doc.operational_emissions_onsite_renewable = step_data.get("operational_emissions_onsite_renewable")
            doc.operational_emissions_offsite_renewable = step_data.get("operational_emissions_offsite_renewable")
            doc.operational_emissions_fuel_switching = step_data.get("operational_emissions_fuel_switching")
            doc.operational_emissions_process_optimization = step_data.get("operational_emissions_process_optimization")
            
            # Value Chain Emissions
            doc.value_chain_emissions_supplier_engagement = step_data.get("value_chain_emissions_supplier_engagement")
            doc.value_chain_emissions_low_carbon_materials = step_data.get("value_chain_emissions_low_carbon_materials")
            doc.value_chain_emissions_redesign_use_phase = step_data.get("value_chain_emissions_redesign_use_phase")
            doc.value_chain_emissions_optimize_logistics = step_data.get("value_chain_emissions_optimize_logistics")
            doc.value_chain_emissions_circular_economy = step_data.get("value_chain_emissions_circular_economy")
            
            # Land Sector & Removals
            doc.land_sector_removals_afforestation = step_data.get("land_sector_removals_afforestation")
            doc.land_sector_removals_soil_carbon = step_data.get("land_sector_removals_soil_carbon")
            doc.land_sector_removals_urban_greening = step_data.get("land_sector_removals_urban_greening")
            doc.land_sector_removals_biochar = step_data.get("land_sector_removals_biochar")
            doc.land_sector_removals_carbon_capture = step_data.get("land_sector_removals_carbon_capture")
            doc.land_sector_removals_certified_removals = step_data.get("land_sector_removals_certified_removals")
            
            # Residual Emissions Strategy
            doc.residual_emissions_high_quality_credits = step_data.get("residual_emissions_high_quality_credits")
            doc.residual_emissions_bvcm = step_data.get("residual_emissions_bvcm")
            doc.residual_emissions_temporary_solutions = step_data.get("residual_emissions_temporary_solutions")
            
            # Section D: Monitoring, Adjustments & Reporting
            doc.monitoring_frequency = step_data.get("monitoring_frequency")
            doc.monitoring_frequency_other_text = step_data.get("monitoring_frequency_other_text")
            doc.assurance_validation = step_data.get("assurance_validation")
            
            # GHG Tracking Tools
            doc.ghg_tracking_tools_excel = step_data.get("ghg_tracking_tools_excel")
            doc.ghg_tracking_tools_software = step_data.get("ghg_tracking_tools_software")
            doc.ghg_tracking_tools_software_name = step_data.get("ghg_tracking_tools_software_name")
            doc.ghg_tracking_tools_web_platform = step_data.get("ghg_tracking_tools_web_platform")
            
            # Recalculation Policy
            doc.recalculation_policy_structural = step_data.get("recalculation_policy_structural")
            doc.recalculation_policy_methodology = step_data.get("recalculation_policy_methodology")
            doc.recalculation_policy_boundary = step_data.get("recalculation_policy_boundary")
            
            # Progress Communication
            doc.progress_communication_esg_dashboard = step_data.get("progress_communication_esg_dashboard")
            doc.progress_communication_sustainability_report = step_data.get("progress_communication_sustainability_report")
            doc.progress_communication_cdp_disclosure = step_data.get("progress_communication_cdp_disclosure")
            doc.progress_communication_sbti_registry = step_data.get("progress_communication_sbti_registry")
            
            doc.current_step = 5
            
        elif step_number == 6:
            # Step 6: Method of Calculation
            doc.method_of_calculation_option_a = step_data.get("method_of_calculation_option_a")
            doc.method_of_calculation_option_b = step_data.get("method_of_calculation_option_b")
            doc.method_of_calculation_option_c = step_data.get("method_of_calculation_option_c")
            doc.method_of_calculation_option_d = step_data.get("method_of_calculation_option_d")
            doc.method_of_calculation_option_e = step_data.get("method_of_calculation_option_e")
            
            doc.current_step = 6
        
        # Save the document
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        
        return {
            "success": True,
            "message": f"Step {step_number} data saved successfully",
            "current_step": doc.current_step
        }
        
    except Exception as e:
        frappe.log_error(f"Error saving step data: {str(e)}")
        return {
            "success": False,
            "message": f"Error saving step data: {str(e)}"
        }


@frappe.whitelist(allow_guest=True)
def send_verification_email(email, data):
    """Send email verification after Step 1 completion"""
    try:
        if not email or not email.strip():
            return {"success": False, "message": "Email is required"}
        
        # Handle JSON string data from frontend
        if isinstance(data, str):
            data = json.loads(data)
        
        # Generate verification token
        verification_token = str(uuid.uuid4())
        
        # Store session data temporarily (expires in 24 hours)
        session_key = f"climoro_onboarding_{verification_token}"
        session_data = {
            "email": email,
            "data": data,
            "current_step": 1,
            "verified": False,
            "created_at": now()
        }
        
        # Store in cache for 24 hours (86400 seconds)
        frappe.cache().set_value(session_key, json.dumps(session_data), expires_in_sec=86400)
        
        # Create verification URL
        site_url = frappe.utils.get_url()
        verification_url = f"{site_url}/apply?verify={verification_token}"
        
        # Send verification email
        send_verification_email_to_user(email, data.get("company_name", ""), verification_url)
        
        return {
            "success": True,
            "message": "Verification email sent successfully",
            "requires_verification": True,
            "verification_token": verification_token
        }
        
    except Exception as e:
        frappe.log_error(f"Error sending verification email: {str(e)}", "Climoro Onboarding Verification Error")
        return {
            "success": False,
            "message": f"Error sending verification email: {str(e)}"
        }


@frappe.whitelist(allow_guest=True)
def verify_email(token):
    """Verify email and create draft onboarding form entry"""
    try:
        frappe.logger().info(f"🔍 verify_email called with token: {token}")
        
        if not token:
            frappe.logger().error("❌ No token provided")
            return {"success": False, "message": "Verification token is required"}
            
        session_key = f"climoro_onboarding_{token}"
        session_data_str = frappe.cache().get_value(session_key)
        
        frappe.logger().info(f"🔍 Session data from cache: {session_data_str}")
        
        if not session_data_str:
            frappe.logger().error("❌ No session data found for token")
            return {"success": False, "message": "Invalid or expired verification token"}
            
        session_data = json.loads(session_data_str)
        email = session_data.get("email")
        
        frappe.logger().info(f"📧 Email from session: {email}")
        frappe.logger().info(f"📋 Full session data: {session_data}")
        frappe.logger().info(f"📋 Session data keys: {list(session_data.keys())}")
        
        if "data" in session_data:
            frappe.logger().info(f"📋 Session data['data']: {session_data['data']}")
            frappe.logger().info(f"📋 Session data['data'] keys: {list(session_data['data'].keys()) if isinstance(session_data['data'], dict) else 'Not a dict'}")
        
        if not email:
            frappe.logger().error("❌ No email found in session data")
            return {"success": False, "message": "Email not found in session data"}
        
        # Mark as verified in session
        session_data["verified"] = True
        session_data["verified_at"] = now()
        
        frappe.logger().info(f"✅ Marked session as verified")
        
        # Update cache with verified status
        frappe.cache().set_value(session_key, json.dumps(session_data), expires_in_sec=86400)
        
        # Save/update the doctype with verified email data
        frappe.logger().info(f"💾 Calling save_verified_email_to_doctype")
        application_id = save_verified_email_to_doctype(email, session_data)
        
        frappe.logger().info(f"📋 Application ID returned: {application_id}")
        
        # Update session data with the application ID if we got one
        if application_id:
            session_data["application_id"] = application_id
            # Update cache with application ID
            frappe.cache().set_value(session_key, json.dumps(session_data), expires_in_sec=86400)
            frappe.logger().info(f"✅ Updated session with application ID: {application_id}")
        
        return {
            "success": True,
            "message": "Email verified successfully",
            "session_data": session_data,
            "email": email,
            "application_id": application_id
        }
        
    except Exception as e:
        frappe.logger().error(f"❌ Error in verify_email: {str(e)}")
        frappe.log_error(f"Error verifying email: {str(e)}", "Climoro Onboarding Verification Error")
        return {
            "success": False,
            "message": f"Error verifying email: {str(e)}"
        }


def save_verified_email_to_doctype(email, session_data):
    """Save or update doctype with verified email data"""
    try:
        # Debug logging to file (like franchise portal)
        debug_file = os.path.join(frappe.get_site_path(), 'debug_onboarding_verification.txt')
        with open(debug_file, 'a') as f:
            f.write(f"\n=== ENTER save_verified_email_to_doctype {frappe.utils.now()} ===\n")
            f.write(f"Email: {email}\n")
            f.write(f"Session data: {json.dumps(session_data)[:1000]}...\n")
        
        frappe.logger().info(f"🔍 save_verified_email_to_doctype called for email: {email}")
        frappe.logger().info(f"📋 Session data: {session_data}")
        
        # Check if application already exists for this email
        existing_applications = frappe.get_all(
            "Onboarding Form",
            filters={"email": email},
            fields=["name", "status"],
            limit=1
        )
        
        frappe.logger().info(f"🔍 Existing applications found: {existing_applications}")
        
        if existing_applications:
            # Update existing application
            existing_app = existing_applications[0]
            doc_name = existing_app["name"]
            
            frappe.logger().info(f"📝 Updating existing application: {doc_name}")
            
            # Update with verification status and basic fields
            updates = {
                "email_verified": 1,
                "email_verified_at": now(),
                "status": "Draft",
                "current_step": 1
            }
            
            # Add Step 1 data from session
            application_data = session_data.get("data", {})
            frappe.logger().info(f"📋 Application data from session: {application_data}")
            
            basic_fields = [
                "first_name", "middle_name", "last_name", "phone_number", "position"
            ]
            for field in basic_fields:
                if field in application_data and application_data[field]:
                    updates[field] = application_data[field]
                    frappe.logger().info(f"📝 Update {field} = {application_data[field]}")
                else:
                    frappe.logger().warning(f"⚠️ Missing or empty field for update: {field}")
            
            frappe.logger().info(f"📝 Updates to apply: {updates}")
            
            frappe.db.set_value("Onboarding Form", doc_name, updates)
            frappe.db.commit()
            
            frappe.logger().info(f"✅ Successfully updated existing application: {doc_name}")
            with open(debug_file, 'a') as f:
                f.write(f"✅ Updated existing application: {doc_name}\n")
            return doc_name
        else:
            # No existing application found - create new one
            frappe.logger().info(f"🆕 Creating new application for email: {email}")
            with open(debug_file, 'a') as f:
                f.write(f"🆕 Creating new application for email: {email}\n")
            
            try:
                doc = frappe.new_doc("Onboarding Form")
                doc.email = email
                doc.email_verified = 1
                doc.email_verified_at = now()
                doc.status = "Draft"
                doc.current_step = 1
                
                # Set naming series explicitly (like franchise portal)
                if not doc.naming_series:
                    doc.naming_series = "OF-.YYYY.-"
                
                # Add Step 1 data from session
                application_data = session_data.get("data", {})
                frappe.logger().info(f"📋 Application data from session: {application_data}")
                with open(debug_file, 'a') as f:
                    f.write(f"📋 Application data: {json.dumps(application_data)}\n")
                
                basic_fields = [
                    "first_name", "middle_name", "last_name", "phone_number", "position"
                ]
                for field in basic_fields:
                    if field in application_data and application_data[field]:
                        setattr(doc, field, application_data[field])
                        frappe.logger().info(f"📝 Set {field} = {application_data[field]}")
                        with open(debug_file, 'a') as f:
                            f.write(f"📝 Set {field} = {application_data[field]}\n")
                    else:
                        frappe.logger().warning(f"⚠️ Missing or empty field: {field}")
                        with open(debug_file, 'a') as f:
                            f.write(f"⚠️ Missing or empty field: {field}\n")
                
                frappe.logger().info(f"📝 Document fields set: email={doc.email}, verified={doc.email_verified}, status={doc.status}")
                frappe.logger().info(f"📝 Document first_name={getattr(doc, 'first_name', 'NOT SET')}")
                frappe.logger().info(f"📝 Document phone_number={getattr(doc, 'phone_number', 'NOT SET')}")
                
                # Use flag to prevent automatic email modification (like franchise portal)
                frappe.flags.ignore_email_uniqueness = True
                doc.insert(ignore_permissions=True)
                frappe.flags.ignore_email_uniqueness = False
                
                frappe.db.commit()
                
                frappe.logger().info(f"✅ Successfully created new application: {doc.name}")
                with open(debug_file, 'a') as f:
                    f.write(f"✅ Successfully created new application: {doc.name}\n")
                return doc.name
            except Exception as e:
                frappe.logger().error(f"❌ Exception during doc.insert: {str(e)}")
                frappe.log_error(f"Exception during doc.insert: {str(e)}", "Climoro Onboarding Doc Creation Error")
                with open(debug_file, 'a') as f:
                    f.write(f"❌ Exception during doc.insert: {str(e)}\n")
                return None
                
    except Exception as e:
        frappe.logger().error(f"❌ Error in save_verified_email_to_doctype: {str(e)}")
        frappe.log_error(f"Error saving verified email to doctype: {str(e)}", "Climoro Onboarding Doc Creation Error")
        debug_file = os.path.join(frappe.get_site_path(), 'debug_onboarding_verification.txt')
        with open(debug_file, 'a') as f:
            f.write(f"❌ Error in save_verified_email_to_doctype: {str(e)}\n")
        return None


@frappe.whitelist(allow_guest=True)
def test_email_verification_flow():
    """Test the email verification flow"""
    try:
        # Test data
        test_email = "test@example.com"
        test_data = {
            "first_name": "Test User",
            "phone_number": "1234567890",
            "position": "Manager"
        }
        
        # Step 1: Send verification email
        result1 = send_verification_email(test_email, test_data)
        if not result1.get("success"):
            return {"success": False, "message": f"Failed to send verification email: {result1.get('message')}"}
        
        verification_token = result1.get("verification_token")
        
        # Step 2: Verify email
        result2 = verify_email(verification_token)
        if not result2.get("success"):
            return {"success": False, "message": f"Failed to verify email: {result2.get('message')}"}
        
        # Step 3: Check if doctype was created/updated
        applications = frappe.get_all(
            "Onboarding Form",
            filters={"email": test_email},
            fields=["name", "email_verified", "email_verified_at", "first_name", "status", "current_step"]
        )
        
        if not applications:
            return {"success": False, "message": "No application found after verification"}
        
        app = applications[0]
        
        return {
            "success": True,
            "message": "Email verification flow test completed successfully",
            "application_id": app.name,
            "email_verified": app.email_verified,
            "email_verified_at": app.email_verified_at,
            "first_name": app.first_name,
            "status": app.status,
            "current_step": app.current_step
        }
        
    except Exception as e:
        return {"success": False, "message": f"Test failed: {str(e)}"}


@frappe.whitelist(allow_guest=True)
def get_session_data(token):
    """Get session data for verified token"""
    try:
        if not token:
            return {"success": False, "message": "Verification token is required"}
            
        session_key = f"climoro_onboarding_{token}"
        session_data_str = frappe.cache().get_value(session_key)
        
        if not session_data_str:
            return {"success": False, "message": "Invalid or expired verification token"}
            
        session_data = json.loads(session_data_str)
        
        if not session_data.get("verified"):
            return {"success": False, "message": "Email not verified", "requires_verification": True}
        
        return {
            "success": True,
            "session_data": session_data
        }
        
    except Exception as e:
        frappe.log_error(f"Error getting session data: {str(e)}", "Climoro Onboarding Verification Error")
        return {
            "success": False,
            "message": f"Error retrieving session data: {str(e)}"
        }


def send_verification_email_to_user(email, company_name, verification_url):
    """Send verification email to the applicant"""
    subject = f"Verify Your Email - Climoro Onboarding Form"
    
    message = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #5e64ff;">Email Verification Required</h2>
        
        <p>Dear Applicant,</p>
        
        <p>Thank you for starting your Climoro onboarding process for <strong>{company_name or 'your company'}</strong>.</p>
        
        <p>To continue with your onboarding, please verify your email address by clicking the button below:</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{verification_url}" 
               style="background-color: #5e64ff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                Verify Email & Continue Onboarding
            </a>
        </div>
        
        <p style="color: #6c757d; font-size: 14px;">If the button doesn't work, copy and paste this link in your browser:</p>
        <p style="color: #5e64ff; word-break: break-all; font-size: 14px;">{verification_url}</p>
        
        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h4 style="margin-top: 0; color: #495057;">What happens next?</h4>
            <ul style="color: #6c757d; margin-bottom: 0;">
                <li>Click the verification link</li>
                <li>You'll be taken to Step 2: Company Details</li>
                <li>Complete the remaining sections</li>
                <li>Submit your complete onboarding form</li>
            </ul>
        </div>
        
        <p style="color: #dc3545; font-size: 14px;"><strong>Note:</strong> This verification link will expire in 24 hours.</p>
        
        <p>Best regards,<br>
        <strong>Climoro Team</strong></p>
    </div>
    """
    
    frappe.sendmail(
        recipients=[email],
        subject=subject,
        message=message,
        now=True
    ) 

# File Upload Functionality
@frappe.whitelist(allow_guest=True)
def upload_file():
    """Handle file uploads for onboarding form documents"""
    try:
        # Get uploaded file from request
        uploaded_file = frappe.request.files.get('file')
        field_name = frappe.form_dict.get('field_name')
        
        if not uploaded_file:
            return {"success": False, "message": "No file uploaded"}
        
        if not field_name:
            return {"success": False, "message": "Field name is required"}
        
        # Validate file size (25MB limit)
        max_size = 25 * 1024 * 1024  # 25MB in bytes
        file_size = len(uploaded_file.read())
        uploaded_file.seek(0)  # Reset file pointer
        
        if file_size > max_size:
            return {"success": False, "message": "File size exceeds 25MB limit"}
        
        # Validate file type
        allowed_extensions = ['.pdf', '.docx', '.doc', '.xlsx', '.xls', '.csv', '.jpg', '.jpeg', '.png', '.gif', '.bmp']
        filename = uploaded_file.filename
        file_extension = '.' + filename.split('.')[-1].lower()
        
        if file_extension not in allowed_extensions:
            return {"success": False, "message": "File type not supported"}
        
        # Create file document record in database using Frappe's proper file handling
        uploaded_file.seek(0)  # Reset file pointer
        file_content = uploaded_file.read()
        
        # Use Frappe's built-in file creation system
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": filename,
            "is_private": 1,
            "content": file_content
        })
        
        file_doc.insert(ignore_permissions=True)
        frappe.db.commit()
        
        # Use the file document's unique_url property which includes proper fid parameter
        # This ensures proper permission checking by Frappe
        site_url = frappe.utils.get_url()
        file_url = f"{site_url}{file_doc.unique_url}"
        
        return {
            "success": True,
            "message": "File uploaded successfully",
            "file_url": file_url,
            "file_name": filename,
            "file_size": file_size,
            "file_id": file_doc.name
        }
        
    except Exception as e:
        frappe.log_error(f"File upload error: {str(e)}", "Onboarding File Upload")
        return {"success": False, "message": f"Upload failed: {str(e)}"} 

@frappe.whitelist(allow_guest=True)
def get_saved_data():
    """Get saved form data for the current session"""
    try:
        # Get session data
        session_data = frappe.get_session()
        if not session_data:
            return {
                "success": False,
                "message": "No session found"
            }
        
        # Get the email from session
        email = session_data.get('email')
        if not email:
            return {
                "success": False,
                "message": "No email found in session"
            }
        
        # Check if there's an existing application
        existing_applications = frappe.get_all(
            "Onboarding Form",
            filters={"email": email},
            fields=["name", "first_name", "middle_name", "last_name", "phone_number", "position", 
                   "company_name", "address", "gps_coordinates", "location_name", "cin", "gst_number", 
                   "industry_type", "sub_industry_type", "website", "letter_of_authorisation",
                   # Step 4: GHG Accounting fields
                   "purpose_of_reporting",
                   # Individual gas checkboxes
                   "gases_to_report_co2", "gases_to_report_ch4", "gases_to_report_n2o", 
                   "gases_to_report_hfcs", "gases_to_report_pfcs", "gases_to_report_sf6", "gases_to_report_nf3",
                   # Individual scope checkboxes
                   "scopes_to_report_scope1", "scopes_to_report_scope2", "scopes_to_report_scope3", "scopes_to_report_reductions",
                   # Individual scope 1 options
                   "scope_1_options_process", "scope_1_options_stationary", "scope_1_options_mobile", "scope_1_options_fugitive",
                   # Individual scope 2 options
                   "scope_2_options_electricity", "scope_2_options_heating", "scope_2_options_cooling",
                   # Individual scope 3 options
                   "scope_3_options_upstream", "scope_3_options_downstream",
                   # Individual reduction options
                   "reduction_options_energy_efficiency", "reduction_options_renewable_energy", "reduction_options_process_optimization",
                   "reduction_options_waste_management", "reduction_options_transportation", "reduction_options_other",
                   # Step 5: Reduction Form fields - Section A: Emissions Inventory Setup
                   "base_year", "base_year_reason", "emissions_exclusions",
                   # Scopes Covered
                   "scopes_covered_scope1", "scopes_covered_scope2", "scopes_covered_scope3",
                   # GHG Boundary Approach
                   "ghg_boundary_approach_operational_control", "ghg_boundary_approach_financial_control", "ghg_boundary_approach_equity_share",
                   # Scope 3 Categories Included
                   "scope_3_categories_purchased_goods", "scope_3_categories_capital_goods", "scope_3_categories_fuel_energy",
                   "scope_3_categories_transportation", "scope_3_categories_waste", "scope_3_categories_business_travel",
                   "scope_3_categories_use_sold_products", "scope_3_categories_end_life_treatment", "scope_3_categories_leased_assets",
                   # Section B: Emissions Reduction Targets
                   "target_type", "scope_1_2_intensity_percentage", "scope_1_2_target_year", "scope_3_intensity_percentage",
                   "scope_3_target_year", "absolute_emissions_percentage", "near_term_target_year", "long_term_target_year",
                   # Target Metrics
                   "target_metrics_absolute_emissions", "target_metrics_kgco2e_mwh", "target_metrics_kgco2e_tonne",
                   "target_metrics_kgco2e_unit_service", "target_metrics_kgco2e_usd_revenue", "target_metrics_kgco2e_stove_year",
                   "target_metrics_kgco2e_tonne_biochar", "target_metrics_kgco2e_km_travelled",
                   # Target Boundary
                   "target_boundary_scope1_2_95_percent", "target_boundary_scope3_90_percent_long_term",
                   "target_boundary_scope3_67_percent_near_term", "target_boundary_prioritize_relevance",
                   # Section C: Mitigation Strategies - Operational Emissions
                   "operational_emissions_energy_efficiency", "operational_emissions_onsite_renewable", "operational_emissions_offsite_renewable",
                   "operational_emissions_fuel_switching", "operational_emissions_process_optimization",
                   # Value Chain Emissions
                   "value_chain_emissions_supplier_engagement", "value_chain_emissions_low_carbon_materials",
                   "value_chain_emissions_redesign_use_phase", "value_chain_emissions_optimize_logistics", "value_chain_emissions_circular_economy",
                   # Land Sector & Removals
                   "land_sector_removals_afforestation", "land_sector_removals_soil_carbon", "land_sector_removals_urban_greening",
                   "land_sector_removals_biochar", "land_sector_removals_carbon_capture", "land_sector_removals_certified_removals",
                   # Residual Emissions Strategy
                   "residual_emissions_high_quality_credits", "residual_emissions_bvcm", "residual_emissions_temporary_solutions",
                   # Section D: Monitoring, Adjustments & Reporting
                   "monitoring_frequency", "monitoring_frequency_other_text", "assurance_validation",
                   # GHG Tracking Tools
                   "ghg_tracking_tools_excel", "ghg_tracking_tools_software", "ghg_tracking_tools_software_name", "ghg_tracking_tools_web_platform",
                   # Recalculation Policy
                   "recalculation_policy_structural", "recalculation_policy_methodology", "recalculation_policy_boundary",
                   # Progress Communication
                   "progress_communication_esg_dashboard", "progress_communication_sustainability_report",
                   "progress_communication_cdp_disclosure", "progress_communication_sbti_registry",
                   # Step 6: Method of Calculation
                   "method_of_calculation_option_a", "method_of_calculation_option_b", "method_of_calculation_option_c",
                   "method_of_calculation_option_d", "method_of_calculation_option_e"],
            order_by="creation desc",
            limit=1
        )
        
        if existing_applications:
            application = existing_applications[0]
            frappe.logger().info(f"Retrieved saved data for email: {email}")
            return {
                "success": True,
                "data": application
            }
        else:
            frappe.logger().info(f"No saved data found for email: {email}")
            return {
                "success": True,
                "data": None
            }
            
    except Exception as e:
        frappe.log_error(f"Error getting saved data: {str(e)}")
        return {
            "success": False,
            "message": f"Error retrieving saved data: {str(e)}"
        } 

@frappe.whitelist(allow_guest=True)
def send_resume_email(email):
    """Send resume email to user with unique token"""
    try:
        if not email:
            return {
                "success": False,
                "message": "Email address is required"
            }
        
        # Check if there's an existing draft application
        existing_applications = frappe.get_all(
            "Onboarding Form",
            filters={"email": email, "status": "Draft"},
            fields=["name", "current_step", "company_name"],
            order_by="modified desc",
            limit=1
        )
        
        if not existing_applications:
            return {
                "success": False,
                "message": "No incomplete application found for this email address. Please start a new application."
            }
        
        application = existing_applications[0]
        
        # Generate unique resume token
        resume_token = str(uuid.uuid4())
        
        # Create resume URL
        site_url = get_url()
        resume_url = f"{site_url}/apply?resume={resume_token}"
        
        # Store session data in cache for 24 hours
        session_data = {
            "email": email,
            "application_id": application.name,
            "current_step": application.current_step or 1,
            "company_name": application.company_name,
            "created_at": now_datetime().isoformat(),
            "expires_at": (now_datetime() + timedelta(hours=24)).isoformat()
        }
        
        session_key = f"climoro_resume_{resume_token}"
        frappe.cache().set_value(session_key, json.dumps(session_data), expires_in_sec=86400)  # 24 hours
        
        # Send resume email
        send_resume_email_to_user(email, application.company_name, resume_url)
        
        return {
            "success": True,
            "message": "Resume link sent to your email address. Please check your inbox."
        }
        
    except Exception as e:
        frappe.log_error(f"Error sending resume email: {str(e)}")
        return {
            "success": False,
            "message": f"Error sending resume email: {str(e)}"
        }


def send_resume_email_to_user(email, company_name, resume_url):
    """Send resume email with custom climoro template"""
    subject = "Resume Your Climoro Onboarding Application"
    message = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; margin-bottom: 30px;">
                <img src="/assets/climoro_onboarding/images/climoro.png" alt="Climoro Logo" style="max-width: 200px; height: auto;">
            </div>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                <h2 style="color: #2c3e50; margin-top: 0;">Resume Your Onboarding Application</h2>
                <p style="color: #555; line-height: 1.6;">
                    Dear {company_name or 'Valued Customer'},
                </p>
                <p style="color: #555; line-height: 1.6;">
                    We noticed you started your Climoro onboarding application but didn't complete it. 
                    You can resume your application from where you left off by clicking the button below.
                </p>
                <p style="color: #555; line-height: 1.6;">
                    <strong>Important:</strong> This link will expire in 24 hours for security reasons.
                </p>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href='{resume_url}' style="background: #28a745; color: white; padding: 15px 30px; border-radius: 5px; text-decoration: none; font-weight: bold; display: inline-block;">
                    🔄 Resume Application
                </a>
            </div>
            
            <div style="background: #e9ecef; padding: 15px; border-radius: 5px; margin-top: 20px;">
                <p style="color: #6c757d; margin: 0; font-size: 14px;">
                    <strong>Need help?</strong> If you have any questions about your onboarding process, 
                    please don't hesitate to contact our support team.
                </p>
            </div>
            
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; text-align: center;">
                <p style="color: #6c757d; font-size: 12px; margin: 0;">
                    Best regards,<br>
                    The Climoro Team
                </p>
            </div>
        </div>
    """
    
    frappe.sendmail(
        recipients=[email], 
        subject=subject, 
        message=message, 
        now=True
    )


@frappe.whitelist(allow_guest=True)
def verify_resume_token(token):
    """Verify resume token and return application data"""
    try:
        if not token:
            return {
                "success": False,
                "message": "Resume token is required"
            }
        
        session_key = f"climoro_resume_{token}"
        session_data_str = frappe.cache().get_value(session_key)
        
        if not session_data_str:
            return {
                "success": False,
                "message": "Invalid or expired resume token"
            }
        
        session_data = json.loads(session_data_str)
        
        # Check if token has expired
        expires_at = session_data.get("expires_at")
        if expires_at:
            from frappe.utils import get_datetime
            if get_datetime(expires_at) < now_datetime():
                frappe.cache().delete_value(session_key)
                return {
                    "success": False,
                    "message": "Resume token has expired. Please request a new one."
                }
        
        # Get the latest application data
        email = session_data.get("email")
        if email:
            applications = frappe.get_all(
                "Onboarding Form",
                filters={"email": email, "status": "Draft"},
                fields=["name", "current_step"],
                order_by="modified desc",
                limit=1
            )
            
            if applications:
                doc = frappe.get_doc("Onboarding Form", applications[0].name)
                # Convert doc to dict and handle datetime serialization
                doc_dict = doc.as_dict()
                # Convert datetime objects to strings
                for key, value in doc_dict.items():
                    if hasattr(value, 'strftime'):  # Check if it's a datetime object
                        doc_dict[key] = value.strftime('%Y-%m-%d %H:%M:%S')
                session_data["application_data"] = doc_dict
                session_data["current_step"] = doc.current_step or 1
                
                # Refresh the cache with updated data
                frappe.cache().set_value(session_key, json.dumps(session_data), expires_in_sec=86400)
        
        return {
            "success": True,
            "message": "Resume token valid",
            "session_data": session_data,
            "current_step": session_data.get("current_step", 1)
        }
        
    except Exception as e:
        frappe.log_error(f"Error verifying resume token: {str(e)}")
        return {
            "success": False,
            "message": f"Error verifying resume token: {str(e)}"
        }

@frappe.whitelist(allow_guest=True)
def debug_resume_token(token):
    """Debug function to check token status"""
    try:
        if not token:
            return {
                "success": False,
                "message": "Token is required"
            }
        
        session_key = f"climoro_resume_{token}"
        
        # Check if token exists in cache
        session_data_str = frappe.cache().get_value(session_key)
        
        debug_info = {
            "token": token,
            "session_key": session_key,
            "cache_exists": session_data_str is not None,
            "cache_data": session_data_str
        }
        
        if session_data_str:
            try:
                session_data = json.loads(session_data_str)
                debug_info["parsed_data"] = session_data
                debug_info["email"] = session_data.get("email")
                debug_info["current_step"] = session_data.get("current_step")
                debug_info["expires_at"] = session_data.get("expires_at")
                
                # Check if application exists in database
                if session_data.get("email"):
                    applications = frappe.get_all(
                        "Onboarding Form",
                        filters={"email": session_data["email"], "status": "Draft"},
                        fields=["name", "current_step", "company_name"],
                        order_by="modified desc",
                        limit=1
                    )
                    debug_info["database_applications"] = applications
                    debug_info["application_count"] = len(applications)
                
            except json.JSONDecodeError as e:
                debug_info["json_error"] = str(e)
        
        return {
            "success": True,
            "debug_info": debug_info
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Debug error: {str(e)}",
            "debug_info": {"error": str(e)}
        }

@frappe.whitelist(allow_guest=True)
def check_current_step_debug(application_id):
    """Debug function to check current step in database"""
    try:
        if not application_id:
            return {
                "success": False,
                "message": "Application ID is required"
            }
        
        doc = frappe.get_doc("Onboarding Form", application_id)
        
        return {
            "success": True,
            "application_id": application_id,
            "current_step": doc.current_step,
            "modified": str(doc.modified),
            "modified_by": doc.modified_by,
            "status": doc.status
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error checking current step: {str(e)}"
        }

@frappe.whitelist(allow_guest=True)
def update_current_step_debug(application_id, new_step):
    """Debug function to update current step in database"""
    try:
        if not application_id:
            return {
                "success": False,
                "message": "Application ID is required"
            }
        
        if not new_step:
            return {
                "success": False,
                "message": "New step is required"
            }
        
        doc = frappe.get_doc("Onboarding Form", application_id)
        old_step = doc.current_step
        doc.current_step = int(new_step)
        doc.save()
        
        return {
            "success": True,
            "application_id": application_id,
            "old_step": old_step,
            "new_step": doc.current_step,
            "message": f"Updated current step from {old_step} to {doc.current_step}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error updating current step: {str(e)}"
        }