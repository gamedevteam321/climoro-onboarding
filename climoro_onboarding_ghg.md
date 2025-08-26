# Report: Climoro Onboarding + GHG Accounting Forms 

Dear [Senior’s Name],

Following a code-level review of both repositories, here is the **comprehensive report** covering tech stack, workflows, real roles, and now a full list of **DocTypes with their usage**.

---

## 1) Tech Stack Overview
- **Framework:** Frappe (Python, MariaDB/MySQL, Redis, Node.js/webpack).
- **Backend:** Python (DocType controllers, hooks, workflow logic, CO₂e calculations).
- **Frontend:** HTML/CSS + JavaScript (validation, form logic, UX helpers).
- **Database:** MariaDB/MySQL via Frappe ORM.
- **Background Jobs:** Redis queue for heavy operations.
- **Reference Data:** IPCC GWP CSV for CO₂e conversion.
- **CI/Security (Onboarding):** pre-commit (ruff/eslint/prettier/pyupgrade), Semgrep, pip‑audit.
- **Licensing:** Onboarding → MIT; GHG Forms → no license file (needs confirmation).

---

## 2) Climoro Onboarding — Workflow & Roles

### Purpose
- Manages user/company onboarding.
- Controls workspace visibility until prerequisites are satisfied.
- Collects KYC, company profile, and optional geolocation.

### Workflow
1. **Signup** → Applicant created.
2. **Visibility control** → Only Onboarding workspace visible.
3. **Data capture** → company profile, KYC, facility location.
4. **Validation** → admin review.
5. **Access grant** → roles elevated (e.g., System Manager, Company User) and GHG workspace becomes visible.

### Roles Reality
- **System Manager** → full access.
- **All** → default broad access (must be restricted for production).
- **Applicant** → minimal access during onboarding.
- Other site-level roles seen in config: **Climoro User**, **Unit Manager**, **Data Analyst**, **Super Admin**, **Guest**.

---

## 3) GHG Accounting Forms — Workflow & Roles

### Purpose
Provides full coverage of GHG Protocol Scopes 1, 2, 3 with emissions calculations and reporting.

### Workflow
1. **Emission Factor setup** (System Manager configures).
2. **Activity Data entry** in Scope 1/2/3 forms.
3. **Validation & Conversion** → activity × EF, apply GWP.
4. **Aggregation** → by Scope/category/gas.
5. **Reporting** → consolidated GHG emissions report.

### Roles Reality
- No GHG-specific roles coded.
- **System Manager** controls configurations and data.
- **All** role has create/write on some DocTypes by default.

---

## 4) DocTypes Inventory & Usage

### Onboarding App DocTypes
1. **Applicant** – Created at signup; stores initial user/company details.
2. **Workspace Visibility Settings** – Manages which workspaces are shown based on role/progress.
3. **Module Block Rules** – Defines which modules are blocked until approval.
4. **Maps Integration Settings** – Stores API keys and settings for Google Maps.
5. **Enhanced Table Config** – Settings for improved child table rendering.

*(Usage: These DocTypes are primarily administrative and configuration-based, ensuring onboarding control and better UX.)*

### GHG Accounting Forms DocTypes

**Scope 1: Direct Emissions**
1. **Stationary Emissions** – Records stationary combustion (boilers, generators). Fields: Fuel type, quantity, EF, CO₂/CH₄/N₂O, CO₂e.
2. **Emission Factor Master** – Stores emission factors for fuels/activities. Used for all Scope 1 & 2 calculations.
3. **Mobile Combustion** – Captures vehicle/machinery fuel data.
4. **Fugitive Emissions** – Tracks refrigerant use/leaks with GWP factors.

**Scope 2: Indirect Energy**
5. **Electricity Consumption** – Captures purchased electricity (kWh, location, grid factor).

**Scope 3: Value Chain**
6. **Purchased Goods & Services** – Inputs for upstream emissions from suppliers.
7. **Capital Goods** – Tracks embodied emissions from capital purchases.
8. **Waste Generated in Operations** – Records waste type, disposal method, EF.
9. **Business Travel** – Tracks passenger-km by mode (air, rail, car).
10. **Employee Commuting** – Daily commuting activity and emission factors.
11. **Upstream T&D** – Transportation/distribution upstream.
12. **Upstream Leased Assets** – Captures leased asset emissions.
13. **Downstream T&D** – Transportation/distribution downstream.
14. **Use of Sold Products** – Estimates emissions from product use.
15. **End-of-Life Treatment** – Product disposal/end-of-life impacts.
16. **Downstream Leased Assets** – Emissions from leased assets downstream.
17. **Franchises** – Emissions from franchise operations.
18. **Investments** – Equity/debt/projected emissions from investments.

**Reporting**
19. **GHG Report** – Consolidates emissions across all scopes; presents totals by category and gas.

---

## 5) Combined End-to-End Flow
1. User signs up → Applicant created.
2. Onboarding collects company/KYC; module blocking applied.
3. Admin approves → user elevated to System Manager/Company User.
4. GHG workspace unlocked.
5. System Manager configures Emission Factors.
6. Users enter Scope 1/2/3 data into respective DocTypes.
7. System validates and calculates CO₂e.
8. Report module aggregates results for review/export.

---

## 6) Strengths
- Onboarding app provides controlled entry and data collection.
- GHG app provides full Scope 1–3 coverage with detailed category forms.
- Frappe audit trails ensure traceability.
- Modular design: easy to extend with new categories.

## 7) Gaps & Risks
- Permissions default to “All” → must be restricted.
- GHG repo lacks README, license, and release tags.
- Automated test coverage incomplete.
- No governance process yet for EF updates.

---

## 8) Key Questions to Expect
- Which ERPNext versions are supported?
- How will emission factors be governed and updated?
- Are permissions hardened (avoiding broad “All”)?
- Does the system align with GHG Protocol & ISO 14064?
- How customizable are the DocTypes and reports?
- What is the roadmap (dashboards, dMRV integration, AI/Carbon GPT)?

---

**Conclusion:**  
The Onboarding app ensures structured access and data capture, while the GHG Forms app delivers full emissions accounting. Real roles are limited to **System Manager** and **All** defaults; no GHG-specific roles exist. For production, permissions must be hardened, a role model defined, and documentation/licensing formalized.

## Appendix — All DocTypes with Usage (from code)
> Enumerates every DocType found in the provided code packages, with usage notes and key fields (truncated to the most important).

### Onboarding / GHG DocTypes

| Doctype | Usage | Key Fields (sample) | Path |
|---|---|---|---|
| Emission Factor Master | Master list of fuel/activity emission factors used in calculations. | fuel_type (Select), fuel_name (Data), efco2 (Float), efch4 (Float), efn20 (Float), efco2_energy (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/emission_factor_master/emission_factor_master.json` |
| GWP Reference | Application DocType; see key fields for context. | chemical_name (Data), chemical_formula (Data), gwp_ar5_100yr (Float), gwp_ar6_100yr (Float), gwp_ar6_20yr (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/gwp_reference/gwp_reference.json` |
| Mobile Combustion Transportation Method | Record mobile combustion activity (vehicles/equipment) for Scope 1. | naming_series (Select), s_no (Int), date (Date), transportation_type (Select), distance_traveled (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/mobile_combustion_transportation_method/mobile_combustion_transportation_method.json` |
| Users Summary Table | Application DocType; see key fields for context. |  | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/users_summary_table/users_summary_table.json` |
| Downstream Waste Method | Application DocType; see key fields for context. | naming_series (Select), s_no (Int), date (Date), waste_category (Select), waste_generated (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/downstream_waste_method/downstream_waste_method.json` |
| Downstream Transportation & Distribution Method | Scope 3: Transportation and distribution. | s_no (Int), date (Date), transportation_type (Select), distance_traveled (Float), weight_transported (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/downstream_transportation___distribution_method/downstream_transportation___distribution_method.json` |
| Site Facility | Facility/site record; may store Maps coordinates. | site_name (Data), address (Small Text), latitude (Float), longitude (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/site_facility/site_facility.json` |
| Purchased Goods & Services Method | Scope 3 upstream: Purchased Goods & Services activity inputs. | date (Date), supplier (Data), category (Select), amount (Float), unit (Data) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/purchased_goods___services_method/purchased_goods___services_method.json` |
| Upstream Electricity T&D Method | Scope 3: Transportation and distribution. | date (Date), electricity_purchased (Float), grid_factor (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/upstream_electricity_t___d_method/upstream_electricity_t___d_method.json` |
| Workspace Visibility Rule | Frappe workspace config (visibility/gating). | role (Link), workspace (Link), enabled (Check) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/workspace_visibility_rule/workspace_visibility_rule.json` |
| Upstream Transportation & Distribution Method | Scope 3: Transportation and distribution. | date (Date), transportation_type (Select), distance_traveled (Float), weight_transported (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/upstream_transportation___distribution_method/upstream_transportation___distribution_method.json` |
| Fugitive Emissions | Capture refrigerant/gas activity for fugitive emissions with GWP conversion. | date (Date), equipment_selection (Select), refrigerant_type (Select), quantity (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/fugitive_emissions/fugitive_emissions.json` |
| Emission Factor Master Item | Master list of fuel/activity emission factors used in calculations. | fuel_type (Select), fuel_name (Data), efco2 (Float), efch4 (Float), efn20 (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/emission_factor_master_item/emission_factor_master_item.json` |
| Upstream Franchises Method | Scope 3 downstream: Franchises. | date (Date), franchise_name (Data), activity (Data/Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/upstream_franchises_method/upstream_franchises_method.json` |
| Applicant | Onboarding: Applicant record created at signup. | first_name (Data), email (Data), status (Select) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/applicant/applicant.json` |
| Electricity | Capture purchased/imported electricity for Scope 2. | date (Date), meter_id (Data), kwh (Float), grid_factor (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/electricity/electricity.json` |
| Capital Goods Method | Scope 3 upstream: Capital Goods activity inputs. | date (Date), vendor (Data), amount (Float), category (Select) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/capital_goods_method/capital_goods_method.json` |
| Fugitive Screening | Capture refrigerant/gas activity for fugitive emissions with GWP conversion. | s_no (Int), date (Date), equipment_selection (Select), approach_type (Data), gwp_refrigeration (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/fugitive_screening/fugitive_screening.json` |
| Stationary Emissions | Record stationary combustion activity (boilers/gensets) for Scope 1. | fuel_type (Select), quantity (Float), unit (Data), efco2 (Float), efch4 (Float), efn20 (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/stationary_emissions/stationary_emissions.json` |
| GHG Boundary | Application DocType; see key fields for context. | organization (Link), boundaries (Table), notes (Small Text) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/ghg_boundary/ghg_boundary.json` |
| GHG Boundary Line | Application DocType; see key fields for context. | business_unit (Data), location (Data), purpose (Small Text), included (Check), reason_exclusion (Small Text) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/ghg_boundary_line/ghg_boundary_line.json` |
| Downstream Transportation Method | Scope 3: Transportation and distribution. | date (Date), transport_mode (Select), distance (Float), weight (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/downstream_transportation_method/downstream_transportation_method.json` |
| Stationary Emissions (Child Table) | Record stationary combustion activity (boilers/gensets) for Scope 1. | fuel_type (Select), quantity (Float), unit (Data), efco2 (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/stationary_emissions/stationary_emissions.json` |
| Upstream Leased Assets Method | Scope 3: Leased assets activity. | date (Date), asset_type (Select), activity (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/upstream_leased_assets_method/upstream_leased_assets_method.json` |
| Business Travel Method | Scope 3 upstream: Business travel (passenger-km) inputs. | date (Date), travel_mode (Select), passenger_km (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/business_travel_method/business_travel_method.json` |
| Employee Commuting Method | Scope 3 upstream: Employee commuting. | date (Date), mode (Select), distance (Float), employees (Int) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/employee_commuting_method/employee_commuting_method.json` |
| Upstream Transportation Method | Scope 3: Transportation and distribution. | date (Date), transport_mode (Select), distance (Float), weight (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/upstream_transportation_method/upstream_transportation_method.json` |
| Upstream Fuel & Energy Activities Method | Application DocType; see key fields for context. | date (Date), fuel_type (Select), amount (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/upstream_fuel___energy_activities_method/upstream_fuel___energy_activities_method.json` |
| Use of Sold Products Method | Scope 3 downstream: Use phase of sold products. | date (Date), product (Data), usage (Float), unit (Data) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/use_of_sold_products_method/use_of_sold_products_method.json` |
| Downstream Leased Assets Method | Scope 3: Leased assets activity. | date (Date), asset_type (Select), activity (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/downstream_leased_assets_method/downstream_leased_assets_method.json` |
| Downstream Processing of Sold Products Method | Application DocType; see key fields for context. | date (Date), product (Data), processed_qty (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/downstream_processing_of_sold_products_method/downstream_processing_of_sold_products_method.json` |
| Upstream Purchased Goods & Services Method | Scope 3 upstream: Purchased Goods & Services activity inputs. | date (Date), supplier (Data), amount (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/upstream_purchased_goods___services_method/upstream_purchased_goods___services_method.json` |
| Upstream Waste Generated in Operations Method | Scope 3 upstream: Waste generated in operations. | date (Date), waste_type (Select), qty (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/upstream_waste_generated_in_operations_method/upstream_waste_generated_in_operations_method.json` |
| Downstream End-of-Life Treatment Method | Scope 3 downstream: End-of-life treatment of sold products. | date (Date), product (Data), disposal_method (Select), qty (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/downstream_end_of_life_treatment_method/downstream_end_of_life_treatment_method.json` |
| Downstream Use of Sold Products Method | Scope 3 downstream: Use phase of sold products. | date (Date), product (Data), usage (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/downstream_use_of_sold_products_method/downstream_use_of_sold_products_method.json` |
| Downstream Investments Method | Scope 3 downstream: Investments emissions. | date (Date), investment_type (Select), amount (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/downstream_investments_method/downstream_investments_method.json` |
| GHG Reduction Initiative | Application DocType; see key fields for context. | initiative_name (Data), owner (Link), start_date (Date), end_date (Date) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/ghg_reduction_initiative/ghg_reduction_initiative.json` |
| GHG Reduction Line | Application DocType; see key fields for context. | initiative (Data), description (Small Text), reduction_achieved (Float), scope_category_impacted (Data) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/ghg_reduction_line/ghg_reduction_line.json` |
| GHG Report | Aggregate emissions across scopes for reporting. | period (Date), org (Link), totals (Table) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/ghg_report/ghg_report.json` |
| Downstream Fuel Method | Application DocType; see key fields for context. | date (Date), vehicle_no (Data), fuel_selection (Select), fuel_used (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/downstream_fuel_method/downstream_fuel_method.json` |
| Upstream Processing of Sold Products Method | Application DocType; see key fields for context. | date (Date), product (Data), processed_qty (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/upstream_processing_of_sold_products_method/upstream_processing_of_sold_products_method.json` |
| Upstream Downstream T&D Method | Scope 3: Transportation and distribution. | date (Date), transport_mode (Select), distance (Float), weight (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/upstream_downstream_t___d_method/upstream_downstream_t___d_method.json` |
| Upstream End-of-Life Treatment Method | Scope 3 downstream: End-of-life treatment of sold products. | date (Date), product (Data), disposal_method (Select), qty (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/upstream_end_of_life_treatment_method/upstream_end_of_life_treatment_method.json` |
| Purchased Capital Goods Method | Scope 3 upstream: Capital Goods activity inputs. | date (Date), vendor (Data), amount (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/purchased_capital_goods_method/purchased_capital_goods_method.json` |
| Upstream Fuel Method | Application DocType; see key fields for context. | date (Date), fuel_type (Select), fuel_used (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/upstream_fuel_method/upstream_fuel_method.json` |
| Upstream Electricity Use Method | Capture purchased/imported electricity for Scope 2. | date (Date), kwh (Float), grid_factor (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/upstream_electricity_use_method/upstream_electricity_use_method.json` |
| Downstream Electricity Use Method | Capture purchased/imported electricity for Scope 2. | date (Date), kwh (Float), grid_factor (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/downstream_electricity_use_method/downstream_electricity_use_method.json` |
| Upstream Commuting Method | Scope 3 upstream: Employee commuting. | date (Date), mode (Select), distance (Float), employees (Int) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/upstream_commuting_method/upstream_commuting_method.json` |
| Upstream Business Travel Method | Scope 3 upstream: Business travel (passenger-km) inputs. | date (Date), travel_mode (Select), passenger_km (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/upstream_business_travel_method/upstream_business_travel_method.json` |
| Upstream Investments Method | Scope 3 downstream: Investments emissions. | date (Date), investment_type (Select), amount (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/upstream_investments_method/upstream_investments_method.json` |
| Downstream Business Travel Method | Scope 3 upstream: Business travel (passenger-km) inputs. | date (Date), travel_mode (Select), passenger_km (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/downstream_business_travel_method/downstream_business_travel_method.json` |
| Upstream Purchased Capital Goods Method | Scope 3 upstream: Capital Goods activity inputs. | date (Date), vendor (Data), amount (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/upstream_purchased_capital_goods_method/upstream_purchased_capital_goods_method.json` |
| Downstream Commuting Method | Scope 3 upstream: Employee commuting. | date (Date), mode (Select), distance (Float), employees (Int) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/downstream_commuting_method/downstream_commuting_method.json` |
| Upstream Waste Method | Scope 3 upstream: Waste generated in operations. | date (Date), waste_type (Select), qty (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/upstream_waste_method/upstream_waste_method.json` |
| Upstream Processing Method | Application DocType; see key fields for context. | date (Date), process_name (Data), qty (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/upstream_processing_method/upstream_processing_method.json` |
| Downstream Purchased Goods & Services Method | Scope 3 upstream: Purchased Goods & Services activity inputs. | date (Date), supplier (Data), amount (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/downstream_purchased_goods___services_method/downstream_purchased_goods___services_method.json` |
| Upstream Electricity Use T&D Method | Scope 3: Transportation and distribution. | date (Date), electricity_purchased (Float), grid_factor (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/upstream_electricity_use_t___d_method/upstream_electricity_use_t___d_method.json` |
| Use of Sold Products - Value Chain Method | Scope 3 downstream: Use phase of sold products. | date (Date), product (Data), usage (Float) | `climoro-onboarding/climoro_onboarding/climoro_onboarding/doctype/use_of_sold_products_-_value_chain_method/use_of_sold_products_-_value_chain_method.json` |

