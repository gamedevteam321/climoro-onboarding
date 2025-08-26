# Report: Climoro Onboarding + GHG Accounting Forms

## 1. Tech Stack Overview
- **Framework:** Frappe (Python, MariaDB/MySQL, Redis, Node.js/Webpack)
- **Backend:** Python (DocType controllers, hooks, workflows, Carbon Dioxide Equivalent (CO₂e) calculations)
- **Frontend:** HTML/CSS + JavaScript for dynamic forms, validations, UX (User Experience) helpers
- **Database:** MariaDB/MySQL via Frappe ORM (Object Relational Mapping)
- **Background Jobs:** Redis queue (reports, validations)
- **Reference Data:** IPCC (Intergovernmental Panel on Climate Change) GWP (Global Warming Potential) factors (CSV - Comma Separated Values)
- **CI/CD:** pre-commit (ruff, eslint, prettier, pyupgrade), Semgrep, pip-audit
- **Licensing:** Onboarding → MIT License; GHG Forms → License not stated (needs confirmation)

---

## 2. Climoro Onboarding App

### Purpose
- Standardizes user/company onboarding
- Restricts module access until requirements are completed
- Collects KYC (Know Your Customer), company profile, geolocation
- Provides improved UX (User Experience) on Desk UI (User Interface)

### Key Components
- **Custom Signup Form:** Creates `Applicant` DocType with `Applicant` role
- **Workspace Visibility & Module Blocking:** Restricts access to only Onboarding workspace
- **UX Enhancements:** Loading popup, enhanced child tables
- **Google Maps Integration:** Collects facility/site coordinates

### Workflow
1. User registers → Applicant record created
2. Only Onboarding workspace visible
3. Company/KYC details captured + optional geolocation
4. Admin validates entries
5. Access upgraded → general roles (e.g., Climoro User) assigned
6. Additional workspaces (GHG forms) unlocked

---

## 3. GHG Accounting Forms App

### Purpose
Implements GHG (Greenhouse Gas) Protocol accounting for Scopes 1, 2, and 3. Converts activity data × emission factors into tCO₂e (tonnes of Carbon Dioxide Equivalent) using IPCC (Intergovernmental Panel on Climate Change) GWP (Global Warming Potential) values.

### Key Components
- **Scope 1 (Direct):** Stationary combustion, mobile combustion, fugitive emissions
- **Scope 2 (Indirect Energy):** Purchased/imported electricity
- **Scope 3 (Value Chain):** Upstream (purchased goods, capital goods, waste, travel, commuting, leased assets) and Downstream (use of products, end-of-life, franchises, investments)
- **Reports:** Aggregates and exports consolidated emissions

### Workflow
1. **Setup:** System Manager configures Emission Factor Master
2. **Data Entry:** Users input Scope 1, 2, and 3 activity data via forms
3. **Validation:** JS (JavaScript) validation + backend checks
4. **Conversion:** Activity × EF (Emission Factor) (+ GWP) → tCO₂e per record
5. **Aggregation:** Consolidated by scope/category
6. **Reporting:** Emissions summarized and exportable

---

## 4. Role & Permission Reality

### Current Roles in Code
- **System Manager:** Full permissions on all DocTypes
- **All:** Broad read/write/create permissions in some DocTypes (too permissive)
- **Other Generic Roles (Onboarding app):** Climoro User, Unit Manager, Data Analyst, Super Admin, Guest

### Observations
- No GHG-specific roles are defined in code
- Permissions are governed by generic Frappe roles (System Manager/All)
- Needs hardening: remove “All” from sensitive DocTypes, introduce minimal Climoro-specific roles if needed

### Recommendations
1. Restrict create/write from “All” on critical DocTypes
2. Add dedicated roles (e.g., Climoro GHG Data Entry, Climoro Reviewer)
3. Define submit/approve workflows for auditability
4. Publish a documented role model and permission matrix

---

## 5. Combined End-to-End Flow
1. Signup → Applicant role created; only Onboarding workspace visible
2. Company/KYC data captured + optional geotags
3. Access elevated → Climoro User or equivalent role
4. EF setup by System Manager
5. Data entry for Scopes 1–3 via DocTypes
6. Validation and conversion to tCO₂e
7. Consolidation and reporting
8. Export for audits and stakeholders

---

## 6. Strengths
- End-to-end onboarding → emissions reporting workflow
- Covers Scopes 1–3 fully
- Uses IPCC GWP conversions for accuracy
- Role-based access (though requires tightening)
- Modular DocTypes support customization

## 7. Gaps & Risks
- Permissions too broad (use of “All”)
- GHG repo missing README/license
- No formal release/version matrix
- Limited test coverage
- Factor update governance undocumented

---

## 8. Key Questions to Expect (with Suggested Answers)

**Q1. Which ERPNext (Enterprise Resource Planning - Next) versions are supported?**  
*A1.* Built on Frappe v14+; expected compatible with ERPNext 14. Forward-compatible with ERPNext 15 with minor adjustments. Formal testing and release tags recommended.

**Q2. How will emission factors be governed and updated?**  
*A2.* EF (Emission Factor) Master exists, but governance is undocumented. Best practice: source annually from IPCC (Intergovernmental Panel on Climate Change)/DEFRA (Department for Environment, Food & Rural Affairs)/IEA (International Energy Agency), version factors, and publish update logs.

**Q3. Are permissions hardened (avoiding broad “All”)?**  
*A3.* No; currently permissive. Should be hardened by removing write/create from “All”, defining minimal roles, and enabling audit logs.

**Q4. Does the system align with GHG (Greenhouse Gas) Protocol & ISO (International Organization for Standardization) 14064?**  
*A4.* Yes for structure: covers Scopes 1–3, uses GWP factors. For ISO 14064, workflows and boundary documentation should be added for certification readiness.

**Q5. How customizable are the DocTypes and reports?**  
*A5.* Fully customizable; standard Frappe JSON (JavaScript Object Notation) definitions. Reports extendable through ERPNext’s Report Builder, custom scripts, or dashboards.

**Q6. What is the roadmap (dashboards, dMRV)?**  
*A6.* Future roadmap should include dashboards, dMRV (Digital Monitoring, Reporting & Verification) integrations (IoT - Internet of Things/satellite), and alignment with Article 6 compliance.

**Q7. AI Agents for Enhanced Accounting and Automation (AI/Carbon GPT)**  
*A7.* AI agents are being developed to automate accounting tasks such as invoice processing and data population. These agents can quickly process large volumes of files for audits, significantly reducing the time required compared to manual processes. They enhance human work by providing interoperability and scalability, and can be integrated with various compliance reporting tools.

**Q8. Cybersecurity Measures and Data Protection**  
*A8.* Cybersecurity is a key concern, and measures are being implemented to protect sensitive data. The system is designed to be highly secure, making it difficult to hack, with features like 2-state verification. The server is hosted on AWS (Amazon Web Services), which is considered a secure and industry-trusted platform.

**Q9. OCR (Optical Character Recognition) Technology and its Applications**  
*A9.* OCR technology is utilized for accounting purposes, including data detection. OCR is efficient and has various applications across industries. OCR libraries are connected with year-end accounting, enabling automation in document scanning, invoice recognition, and data entry tasks.

---

## 9. Appendix — All DocTypes with Usage (from code)
> Comprehensive list of DocTypes identified in repositories, separated by Onboarding and GHG Accounting modules.

### Onboarding DocTypes
| Doctype | Usage | Key Fields (sample) | Path |
|---|---|---|---|
| Applicant | Onboarding record created at signup. | first_name (Data), email (Data), status (Select) | `climoro-onboarding/.../applicant.json` |
| Site Facility | Facility/site record with Maps coordinates. | site_name (Data), latitude (Float), longitude (Float) | `climoro-onboarding/.../site_facility.json` |
| Workspace Visibility Rule | Controls which workspaces are visible to which roles. | role (Link), workspace (Link), enabled (Check) | `climoro-onboarding/.../workspace_visibility_rule.json` |

### GHG Accounting DocTypes
| Doctype | Usage | Key Fields (sample) | Path |
|---|---|---|---|
| Emission Factor Master | Master list of fuel/activity emission factors used in calculations. | fuel_type (Select), fuel_name (Data), efco2 (Float), efch4 (Float), efn20 (Float) | `climoro-onboarding/.../emission_factor_master.json` |
| GWP Reference | Stores IPCC (Intergovernmental Panel on Climate Change) GWP values for gases. | chemical_name (Data), chemical_formula (Data), gwp_ar5_100yr (Float) | `climoro-onboarding/.../gwp_reference.json` |
| Stationary Emissions | Records Scope 1 stationary combustion activity. | fuel_type (Select), quantity (Float), efco2 (Float) | `climoro-onboarding/.../stationary_emissions.json` |
| Mobile Combustion Transportation Method | Records Scope 1 mobile combustion (vehicle/equipment). | date (Date), transportation_type (Select), distance_traveled (Float) | `climoro-onboarding/.../mobile_combustion_transportation_method.json` |
| Fugitive Emissions | Captures refrigerant/gas fugitive emissions with GWP conversion. | date (Date), refrigerant_type (Select), quantity (Float) | `climoro-onboarding/.../fugitive_emissions.json` |
| Electricity | Captures purchased/imported electricity for Scope 2. | date (Date), kwh (Float), grid_factor (Float) | `climoro-onboarding/.../electricity.json` |
| Business Travel Method | Records Scope 3 upstream business travel. | travel_mode (Select), passenger_km (Float) | `climoro-onboarding/.../business_travel_method.json` |
| Employee Commuting Method | Records Scope 3 upstream employee commuting. | mode (Select), distance (Float), employees (Int) | `climoro-onboarding/.../employee_commuting_method.json` |
| Purchased Goods & Services Method | Records Scope 3 purchased goods/services. | supplier (Data), amount (Float), unit (Data) | `climoro-onboarding/.../purchased_goods___services_method.json` |
| Capital Goods Method | Records Scope 3 capital goods purchases. | vendor (Data), amount (Float), category (Select) | `climoro-onboarding/.../capital_goods_method.json` |
| Waste Generated in Operations Method | Records Scope 3 waste in operations. | waste_type (Select), qty (Float) | `climoro-onboarding/.../upstream_waste_generated_in_operations_method.json` |
| Transportation & Distribution Methods | Records upstream/downstream T&D. | transport_mode (Select), distance (Float), weight (Float) | `climoro-onboarding/.../transportation_distribution_method.json` |
| End-of-Life Treatment Method | Records Scope 3 end-of-life treatment of sold products. | product (Data), disposal_method (Select), qty (Float) | `climoro-onboarding/.../end_of_life_treatment_method.json` |
| Use of Sold Products Method | Records downstream use of sold products. | product (Data), usage (Float), unit (Data) | `climoro-onboarding/.../use_of_sold_products_method.json` |
| Franchises Method | Records Scope 3 downstream franchise data. | franchise_name (Data), activity (Data/Float) | `climoro-onboarding/.../franchises_method.json` |
| Investments Method | Records Scope 3 downstream investments emissions. | investment_type (Select), amount (Float) | `climoro-onboarding/.../investments_method.json` |
| GHG Report | Consolidates Scope 1–3 data for reporting. | period (Date), totals (Table) | `climoro-onboarding/.../ghg_report.json` |

---

**Conclusion:**  
The combined system provides a robust onboarding → emissions reporting pipeline. To be production-ready, permissions must be hardened, factor update governance established, and documentation/licensing completed. Additionally, AI (Artificial Intelligence) Agents, Cybersecurity measures, and OCR (Optical Character Recognition) applications provide a future roadmap for scalability and automation. These improvements will ensure compliance, security, and customer confidence.

