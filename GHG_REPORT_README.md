# GHG Report Doctype - Implementation Guide

## Overview

The GHG Report Doctype is a comprehensive document type designed for creating ISO 14064-1 compliant Greenhouse Gas emissions reports. It provides a structured framework for organizations to document their GHG inventory, boundaries, and management practices.

## Features

- **ISO 14064-1 Compliance**: Structured according to international GHG reporting standards
- **Comprehensive Sections**: Covers all required aspects of GHG reporting
- **Child Doctypes**: Modular design with specialized child tables for different data types
- **Auto-calculation**: Automatic calculation of change percentages and emissions totals
- **Professional Print Format**: ISO-compliant print format with tables and formatting
- **Track Changes**: Full audit trail of all modifications

## Doctype Structure

### Main Doctype: GHG Report

**Key Properties:**
- Not submittable (can be edited after creation)
- Track changes enabled
- Multiple sections with collapsible content
- Professional print format included

**Sections:**

1. **Title Page**
   - Report title (required)
   - Organization name (Company link)
   - Reporting period (required dates)
   - Report metadata (version, prepared by, etc.)

2. **Disclaimer**
   - Legal disclaimers and liability statements

3. **Acknowledgements**
   - Recognition of contributors and stakeholders

4. **Citation Information**
   - How to reference this report

5. **Copyright Notice**
   - Intellectual property statements

6. **Table of Contents**
   - HTML editor for custom TOC

7. **Purpose of This Report**
   - Objectives, intended users, responsibilities
   - Frequency, structure, data scope

8. **Introduction**
   - Report type and compliance statements
   - Verification status and GWP values

9. **Organization Description**
   - Overview and GHG policies/strategies

10. **Organizational Boundaries**
    - Child table: GHG Boundary Line
    - Business units, locations, inclusion criteria

11. **Reporting Boundaries**
    - Significance criteria, emission categories, exclusions

12. **GHG Inventory Results**
    - Base year and changes
    - Quantification approaches and factors
    - Child tables: GHG Inventory Line, GHG Scope2 Dual Line

13. **GHG Reductions and Removals**
    - Child table: GHG Reduction Line
    - Initiatives and achieved reductions

14. **Data Management and Quality**
    - Data sources and quality assurance

15. **Appendices**
    - Supporting documents and references

## Child Doctypes

### 1. GHG Boundary Line
**Purpose**: Define organizational boundaries and inclusion criteria
**Fields**:
- `business_unit` (Data, required)
- `location` (Data)
- `purpose` (Small Text)
- `included` (Check, default: Yes)
- `reason_exclusion` (Small Text, conditional)

### 2. GHG Inventory Line
**Purpose**: Detailed GHG emissions inventory by category and scope
**Fields**:
- `iso_category` (Select: Category 1-6)
- `scope` (Select: 1, 2, 3)
- `direct_or_indirect` (Select: Direct/Indirect)
- `ghg_type` (Select: CO₂, CH₄, N₂O, HFCs, PFCs, SF₆, NF₃, Aggregate)
- `emissions_current` (Float, required)
- `emissions_base` (Float)
- `change_pct` (Percent, read-only, auto-calculated)

### 3. GHG Scope2 Dual Line
**Purpose**: Scope 2 emissions reporting with location-based and market-based methods
**Fields**:
- `method` (Select: Location-Based/Market-Based)
- `category2_emissions` (Float, required)
- `total_gross_emissions` (Float, required)

### 4. GHG Reduction Line
**Purpose**: Document GHG reduction initiatives and achievements
**Fields**:
- `initiative` (Data, required)
- `description` (Small Text)
- `reduction_achieved` (Float, required)
- `scope_category_impacted` (Data)

## Technical Implementation

### Python Controller (`ghg_report.py`)

**Key Methods:**
- `validate()`: Main validation logic
- `validate_dates()`: Ensure period_from < period_to
- `calculate_change_percentages()`: Auto-calculate change percentages
- `get_total_emissions_by_scope()`: Group emissions by scope
- `get_emissions_by_ghg_type()`: Group emissions by GHG type

**Auto-calculation Logic:**
```python
def calculate_change_percentages(self):
    if self.ghg_inventory_line:
        for line in self.ghg_inventory_line:
            if line.emissions_current and line.emissions_base:
                if line.emissions_base != 0:
                    line.change_pct = ((line.emissions_current - line.emissions_base) / line.emissions_base) * 100
                else:
                    line.change_pct = 0
```

### Print Format

**Template**: `ghg_report_iso_14064_1.html`
**Features**:
- Professional styling with CSS
- Responsive tables for all child data
- Executive summary box
- Page break optimization
- Print and screen media queries

**Key Jinja Features**:
- Conditional rendering of optional sections
- Loop through child table data
- Formatting for numbers and percentages
- Dynamic content based on document fields

## Usage Instructions

### 1. Creating a New GHG Report

1. Navigate to **Climoro Onboarding > GHG Report**
2. Click **New**
3. Fill in required fields:
   - Report Title
   - Organization Name
   - Period From/To dates
4. Complete optional sections as needed
5. Add child table entries for boundaries, inventory, and reductions
6. Save the document

### 2. Adding Child Table Data

**GHG Boundary Line:**
- Add business units and locations
- Mark inclusion/exclusion status
- Provide reasons for exclusions

**GHG Inventory Line:**
- Select appropriate ISO category and scope
- Enter current and base year emissions
- Change percentage auto-calculates

**GHG Scope2 Dual Line:**
- Enter both location-based and market-based data
- Ensure totals are accurate

**GHG Reduction Line:**
- Document reduction initiatives
- Quantify achieved reductions
- Link to impacted scopes/categories

### 3. Generating Reports

1. Open the GHG Report document
2. Click **Print** button
3. Select **"GHG Report (ISO 14064-1)"** format
4. Choose output format (PDF, Print, etc.)

## Validation Rules

### Date Validation
- `period_from` must be before `period_to`
- Error message: "Period From date must be before Period To date"

### Auto-calculation
- `change_pct` automatically calculates when both emissions values are present
- Handles division by zero gracefully
- Updates on every save/validate

### Required Fields
- Report Title
- Period From
- Period To
- Business Unit (in boundary lines)
- ISO Category, Scope, Direct/Indirect, GHG Type (in inventory lines)
- Current emissions (in inventory lines)
- Initiative name and reduction achieved (in reduction lines)

## Customization Options

### Field Modifications
- Add new fields to any section
- Modify field types and options
- Add custom validation rules

### Print Format Customization
- Modify HTML template for different layouts
- Adjust CSS for branding requirements
- Add custom sections or tables

### Child Doctype Extensions
- Add new fields to child Doctypes
- Create additional child Doctypes for specialized data
- Modify validation logic

## Best Practices

### Data Entry
1. **Start with boundaries**: Define organizational scope first
2. **Complete inventory**: Enter all emission sources systematically
3. **Document reductions**: Track all GHG reduction initiatives
4. **Quality assurance**: Review data before finalizing

### Report Structure
1. **Follow ISO standards**: Maintain compliance with 14064-1
2. **Clear documentation**: Provide detailed explanations for exclusions
3. **Consistent methodology**: Use same approaches across reporting periods
4. **Regular updates**: Maintain current data and methodologies

### Technical Maintenance
1. **Regular validation**: Test Doctype functionality after updates
2. **Backup data**: Export important reports before major changes
3. **Version control**: Track changes to Doctype structure
4. **User training**: Ensure users understand the reporting process

## Troubleshooting

### Common Issues

**Validation Errors:**
- Check date formats and logic
- Ensure required fields are filled
- Verify child table data integrity

**Print Format Issues:**
- Check HTML template syntax
- Verify CSS file paths
- Test with different browsers

**Performance Issues:**
- Limit child table entries for large reports
- Optimize queries for complex calculations
- Consider pagination for very long reports

### Support

For technical support or customization requests:
1. Check this documentation first
2. Review Frappe/ERPNext documentation
3. Contact the development team
4. Submit issue reports with detailed descriptions

## Future Enhancements

### Planned Features
- **Dashboard integration**: Visual charts and graphs
- **Automated calculations**: More complex emission factor calculations
- **Template library**: Pre-built report templates
- **Export options**: Additional output formats (Excel, XML)
- **API integration**: Connect to external GHG calculation tools

### Extension Points
- **Custom fields**: Add organization-specific data points
- **Workflow integration**: Approval processes and notifications
- **Audit trails**: Enhanced change tracking
- **Multi-language support**: Internationalization features

---

**Version**: 1.0  
**Last Updated**: January 2024  
**Compatibility**: Frappe Framework, ERPNext  
**Author**: Climoro Development Team
