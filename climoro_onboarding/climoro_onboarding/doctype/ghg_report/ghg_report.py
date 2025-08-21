import frappe
from frappe.model.document import Document
from frappe.utils import get_url
import os
from frappe.utils.pdf import get_pdf
from frappe.utils.jinja import render_template
from bs4 import BeautifulSoup
from pypdf import PdfReader, PdfWriter
import io

class GHGReport(Document):
    def validate(self):
        """Validate the GHG Report document"""
        self.validate_dates()
        self.calculate_change_percentages()
        self.generate_table_of_contents()
        # Ensure custom print format is the default for this doctype
        self._ensure_default_print_format("GHG Report (ISO 14064-1)")
    
    def validate_dates(self):
        """Validate that period_from is before period_to"""
        if self.period_from and self.period_to:
            if self.period_from > self.period_to:
                frappe.throw("Period From date must be before Period To date")
    
    def calculate_change_percentages(self):
        """Calculate change percentages for GHG Inventory Lines"""
        if self.ghg_inventory_line:
            for line in self.ghg_inventory_line:
                if line.emissions_current and line.emissions_base:
                    if line.emissions_base != 0:
                        line.change_pct = ((line.emissions_current - line.emissions_base) / line.emissions_base) * 100
                    else:
                        line.change_pct = 0
                else:
                    line.change_pct = 0
    
    def generate_table_of_contents(self):
        """Generate automatic table of contents based on document sections"""
        toc_sections = [
            {"title": "Disclaimer", "level": 1},
            {"title": "Acknowledgements", "level": 1},
            {"title": "Citation Information", "level": 1},
            {"title": "Copyright Notice", "level": 1},
            {"title": "Purpose of This Report", "level": 1},
            {"title": "Introduction", "level": 1},
            {"title": "Organization Description", "level": 2},
            {"title": "Organizational Boundaries", "level": 2},
            {"title": "Reporting Boundaries", "level": 2},
            {"title": "GHG Inventory Results", "level": 1},
            {"title": "Emissions and Removals Summary", "level": 2},
            {"title": "Dual Reporting for Scope 2 (if applicable)", "level": 2},
            {"title": "GHG Reductions and Removals Enhancements", "level": 1},
            {"title": "Data Management and Quality", "level": 1},
            {"title": "Appendices", "level": 1}
        ]
        
        # Generate TOC HTML
        toc_html = '<div class="toc-container">\n'
        toc_html += '<h2>Table of Content</h2>\n'
        toc_html += '<ul class="toc-list">\n'
        
        for section in toc_sections:
            indent = "  " * (section["level"] - 1)
            toc_html += f'{indent}<li class="toc-item level-{section["level"]}">\n'
            toc_html += f'{indent}  <a href="#{section["title"].lower().replace(" ", "-").replace("(", "").replace(")", "")}">{section["title"]}</a>\n'
            toc_html += f'{indent}</li>\n'
        
        toc_html += '</ul>\n'
        toc_html += '</div>'
        
        self.toc_note = toc_html

    def _ensure_default_print_format(self, print_format_name: str) -> None:
        """Make the given print format default for the GHG Report doctype (via Property Setter)."""
        try:
            ps_name = frappe.db.get_value(
                "Property Setter",
                {"doc_type": "GHG Report", "property": "default_print_format"},
                "name",
            )
            if ps_name:
                current = frappe.db.get_value("Property Setter", ps_name, "value")
                if current == print_format_name:
                    return
                ps = frappe.get_doc("Property Setter", ps_name)
                ps.value = print_format_name
                ps.save(ignore_permissions=True)
            else:
                frappe.get_doc({
                    "doctype": "Property Setter",
                    "doctype_or_field": "DocType",
                    "doc_type": "GHG Report",
                    "property": "default_print_format",
                    "value": print_format_name,
                    "property_type": "Data",
                }).insert(ignore_permissions=True)
            frappe.clear_cache(doctype="GHG Report")
        except Exception as e:
            frappe.log_error(f"Failed setting default print format: {e}")
    
    def _sync_print_format_from_files(self, print_format_name: str) -> None:
        """Ensure the Print Format HTML/CSS in DB matches the app files."""
        try:
            app = "climoro_onboarding"
            base_dir = os.path.join(
                frappe.get_app_path(app),
                "climoro_onboarding",
                "doctype",
                "ghg_report",
                "print_formats",
                "ghg_report_iso_14064_1",
            )
            html_path = os.path.join(base_dir, "ghg_report_iso_14064_1.html")
            css_path = os.path.join(base_dir, "ghg_report_iso_14064_1.css")

            html_content = ""
            css_content = ""
            if os.path.exists(html_path):
                with open(html_path, "r", encoding="utf-8") as f:
                    html_content = f.read()
                frappe.logger().info(f"HTML file read: {len(html_content)} characters")
            if os.path.exists(css_path):
                with open(css_path, "r", encoding="utf-8") as f:
                    css_content = f.read()
                frappe.logger().info(f"CSS file read: {len(css_content)} characters")

            if not frappe.db.exists("Print Format", print_format_name):
                frappe.logger().info(f"Creating new print format: {print_format_name}")
                pf = frappe.get_doc({
                    "doctype": "Print Format",
                    "name": print_format_name,
                    "doc_type": "GHG Report",
                    "print_format_type": "Jinja",
                })
            else:
                frappe.logger().info(f"Updating existing print format: {print_format_name}")
                pf = frappe.get_doc("Print Format", print_format_name)

            # Force update with file contents
            pf.print_format_type = "Jinja"
            pf.doc_type = "GHG Report"
            pf.html = html_content
            pf.css = css_content
            pf.disabled = 0
            
            # Force save and clear cache
            pf.save(ignore_permissions=True)
            frappe.clear_cache(doctype="Print Format")
            frappe.db.commit()
            
            frappe.logger().info(f"Print format '{print_format_name}' synced successfully")
            
        except Exception as e:
            frappe.log_error(f"Failed syncing print format '{print_format_name}': {e}")
            frappe.logger().error(f"Failed syncing print format '{print_format_name}': {e}")

    @frappe.whitelist()
    def generate_pdf(self):
        """Generate PDF using the print format (no header/footer)"""
        try:
            frappe.logger().info(f"Starting PDF generation for GHG Report {self.name}")
            
            # Ensure print format exists and is default
            print_format_name = "GHG Report (ISO 14064-1)"
            self._sync_print_format_from_files(print_format_name)
            self._ensure_default_print_format(print_format_name)
            
            # Required fields check
            if not self.report_title:
                return {"success": False, "message": "Report Title is required to generate PDF."}

            # Render HTML without letterhead (prevents default header/footer)
            html = frappe.get_print(
                doctype=self.doctype,
                name=self.name,
                print_format=print_format_name,
                as_pdf=False,
                no_letterhead=True
            )
            # Generate PDF directly without injecting header/footer
            pdf = get_pdf(html, options={"print-media-type": None})
            
            if not pdf:
                return {"success": False, "message": "PDF generation failed - no content returned."}
            
            file_name = f"GHG_Report_{self.name}_{frappe.utils.nowdate()}.pdf"
            file_doc = frappe.get_doc({
                "doctype": "File",
                "file_name": file_name,
                "file_type": "pdf",
                "attached_to_doctype": self.doctype,
                "attached_to_name": self.name,
                "content": pdf
            })
            file_doc.insert()
            
            return {
                "success": True,
                "message": f"PDF generated successfully: {file_name}",
                "file_url": file_doc.file_url,
                "file_name": file_name
            }
            
        except Exception as e:
            error_msg = f"Error generating PDF for GHG Report {self.name}: {str(e)}"
            frappe.log_error(error_msg)
            frappe.logger().error(error_msg)
            return {"success": False, "message": f"Error generating PDF: {str(e)}"}

    @frappe.whitelist()
    def force_reset_print_format(self):
        """Force a complete reset and sync of the print format"""
        try:
            frappe.logger().info(f"Force resetting print format for GHG Report {self.name}")
            
            # Clear all caches
            frappe.clear_cache()
            frappe.clear_cache(doctype="Print Format")
            
            # Force sync print format
            print_format_name = "GHG Report (ISO 14064-1)"
            self._sync_print_format_from_files(print_format_name)
            
            # Ensure it's set as default
            self._ensure_default_print_format(print_format_name)
            
            # Clear cache again
            frappe.clear_cache(doctype="GHG Report")
            frappe.db.commit()
            
            frappe.logger().info(f"Print format force reset completed for {self.name}")
            return {"success": True, "message": "Print format has been force reset and synced"}
            
        except Exception as e:
            error_msg = f"Error force resetting print format for GHG Report {self.name}: {str(e)}"
            frappe.log_error(error_msg)
            frappe.logger().error(error_msg)
            return {"success": False, "message": f"Error force resetting print format: {str(e)}"}

    @frappe.whitelist()
    def generate_pdf_using_template(self):
        """Generate PDF by rendering the HTML/CSS template files directly (bypasses DB print format).
        This guarantees the custom layout is used even if DB print formats are stale.
        """
        try:
            app = "climoro_onboarding"
            base_dir = os.path.join(
                frappe.get_app_path(app),
                "climoro_onboarding",
                "doctype",
                "ghg_report",
                "print_formats",
                "ghg_report_iso_14064_1",
            )
            html_path = os.path.join(base_dir, "ghg_report_iso_14064_1.html")
            css_path = os.path.join(base_dir, "ghg_report_iso_14064_1.css")

            if not os.path.exists(html_path):
                return {"success": False, "message": "HTML template file not found."}

            with open(html_path, "r", encoding="utf-8") as f:
                html_template = f.read()

            css_content = ""
            if os.path.exists(css_path):
                with open(css_path, "r", encoding="utf-8") as f:
                    css_content = f.read()

            # Inject CSS from file if not already present in template
            if css_content and "ghg_report_iso_14064_1.css" not in html_template:
                if "</head>" in html_template:
                    html_template = html_template.replace("</head>", f"<style>{css_content}</style></head>")
                else:
                    html_template = f"<style>{css_content}</style>" + html_template

            # Render template with Jinja
            rendered_html = render_template(html_template, {"doc": self, "frappe": frappe})

            # Generate PDF without letterhead/header/footer
            pdf = get_pdf(rendered_html, options={"print-media-type": None})
            if not pdf:
                return {"success": False, "message": "PDF generation failed - no content returned."}

            file_name = f"GHG_Report_{self.name}_{frappe.utils.nowdate()}.pdf"
            file_doc = frappe.get_doc({
                "doctype": "File",
                "file_name": file_name,
                "file_type": "pdf",
                "attached_to_doctype": self.doctype,
                "attached_to_name": self.name,
                "content": pdf,
            })
            file_doc.insert()

            return {
                "success": True,
                "message": f"PDF generated successfully: {file_name}",
                "file_url": file_doc.file_url,
                "file_name": file_name,
            }
        except Exception as e:
            error_msg = f"Error generating PDF (template) for GHG Report {self.name}: {str(e)}"
            frappe.log_error(error_msg)
            frappe.logger().error(error_msg)
            return {"success": False, "message": f"Error generating PDF: {str(e)}"}

    def _build_html_wrapper(self, inner: str, css: str, page_offset: int = 0) -> str:
        """Wrap provided inner HTML with a minimal printable HTML document and inline CSS."""
        watermark_css = (
            ".footer-bar{width:100%;display:flex;justify-content:space-between;align-items:center;"
            "padding:0 12mm 6mm 12mm;box-sizing:border-box;font-size:10pt;color:#666;}"
            ".footer-watermark img{opacity:1;height:28px;}"
            ".footer-page{min-width:80px;text-align:right;}"
        )

        def footer_html() -> str:
            # Use optional field if present on DocType (URL or Data URL). Fallbacks: public files path, then inline SVG.
            img_src = getattr(self, "watermark_image_url", None)
            if not img_src:
                # Prefer the provided public file path
                try:
                    img_src = get_url("/files/Climoro.png")
                except Exception:
                    img_src = None
            if not img_src:
                import base64
                svg = (
                    "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 512 512\">"
                    "<path fill=\"#08a045\" d=\"M470 66c-95 9-165 37-212 85-33 34-54 78-63 133-41-36-95-49-137-43-28 4-49 17-63 40 22 69 64 106 126 110 48 3 98-19 137-65 8 73 3 139-16 197h34c30-55 48-116 55-183 3-34 5-72 6-114 40-23 72-55 93-97 13-27 22-47 25-63Z\"/>"
                    "</svg>"
                )
                b64 = base64.b64encode(svg.encode("utf-8")).decode("ascii")
                img_src = f"data:image/svg+xml;base64,{b64}"
            # Include page numbering using wkhtmltopdf placeholders. We shift numbering in JS by
            # subtracting 'page_offset' (title pages + TOC pages). Hide page numbers <= 0 (title/TOC).
            return (
                "<div id=\"footer-html\">"
                "<div class=\"footer-bar\">"
                f"<div class=\"footer-watermark\"><img src=\"{img_src}\" alt=\"watermark\"/></div>"
                f"<div class=\"footer-page\" data-offset=\"{page_offset}\"><span class=\"page\"></span></div>"
                "<script>(function(){function upd(){try{var el=document.querySelector('.footer-page');if(!el)return;var off=parseInt(el.getAttribute('data-offset')||'0',10);var pg=document.getElementsByClassName('page')[0];var n=parseInt((pg&&pg.textContent)||'0',10);if(!n){setTimeout(upd,0);return;}var v=n-off;el.textContent=(v>0?String(v):''); }catch(e){}} if(document.readyState==='complete'){upd();} else {window.addEventListener('load',upd);} })();</script>"
                "</div></div>"
            )

        return (
            "<!DOCTYPE html><html><head><meta charset='utf-8'>"
            + (f"<style>{css}</style>" if css else "")
            + f"<style>{watermark_css}</style>"
            + "</head><body>"
            + footer_html()
            + "<div class='document-container'>"
            + inner
            + "</div></body></html>"
        )

    def _pdf_pages(self, pdf_bytes: bytes) -> int:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        return len(reader.pages)

    @frappe.whitelist()
    def generate_pdf_with_toc(self):
        """Generate a PDF with a computed Table of Contents including page numbers.

        Strategy:
        - Render the full HTML template
        - Extract title page and each `.section` block
        - Generate PDFs per block to compute page counts
        - Build a TOC page with page numbers (accounting for title + TOC pages)
        - Merge: title → TOC → sections, attach file
        """
        try:
            app = "climoro_onboarding"
            base_dir = os.path.join(
                frappe.get_app_path(app),
                "climoro_onboarding",
                "doctype",
                "ghg_report",
                "print_formats",
                "ghg_report_iso_14064_1",
            )
            html_path = os.path.join(base_dir, "ghg_report_iso_14064_1.html")
            css_path = os.path.join(base_dir, "ghg_report_iso_14064_1.css")

            if not os.path.exists(html_path):
                return {"success": False, "message": "HTML template file not found."}

            with open(html_path, "r", encoding="utf-8") as f:
                html_template = f.read()
            css_content = ""
            if os.path.exists(css_path):
                with open(css_path, "r", encoding="utf-8") as f:
                    css_content = f.read()

            # Render template
            rendered_html = render_template(html_template, {"doc": self, "frappe": frappe})
            soup = BeautifulSoup(rendered_html, "html.parser")

            # Extract title page
            title_div = soup.find(id="title-page")
            title_inner = str(title_div) if title_div else ""
            title_pdf = get_pdf(self._build_html_wrapper(title_inner, css_content), options={"print-media-type": None})
            title_pages = self._pdf_pages(title_pdf) if title_pdf else 1

            # Extract sections
            sections = []
            for sect in soup.select("div.section"):
                # Title from h1.section-header if present
                header = sect.find("h1", {"class": "section-header"}) or sect.find("div", {"class": "section-header"})
                title = header.get_text(strip=True) if header else sect.get("id", "Section")
                marker = f"__PM__{sect.get('id', title.lower().replace(' ', '-'))}__"
                # Use 1px white text so it is invisible but still extractable from PDF text layer
                marker_html = f"<div style=\"font-size:1px;color:#ffffff;line-height:1px;margin:0;padding:0\">{marker}</div>"
                sections.append({
                    "id": sect.get("id", title.lower().replace(" ", "-")),
                    "title": title,
                    "html": str(sect),
                    "marker": marker,
                    "marker_html": marker_html,
                })

            # First pass: render title + all sections (no TOC) with hidden markers to detect start pages
            first_pass_inner = (str(title_div) if title_div else "") + "".join(
                ["<div class='page-break'></div>" + s["marker_html"] + s["html"] for s in sections]
            )
            first_pass_html = self._build_html_wrapper(
                first_pass_inner,
                css_content + ".page-break{page-break-before:always;}",
            )
            first_pass_pdf = get_pdf(first_pass_html, options={"print-media-type": None})
            reader_fp = PdfReader(io.BytesIO(first_pass_pdf))
            pages_text = [p.extract_text() or "" for p in reader_fp.pages]
            # Map section id to its first physical page index (1-based)
            for s in sections:
                pg = 1
                found = None
                for idx, txt in enumerate(pages_text, start=1):
                    if s["marker"] in txt:
                        found = idx
                        break
                s["start_page_physical"] = found or pg
            # Use the actual Disclaimer section as baseline if present
            disclaimer_section = next((s for s in sections if "disclaimer" in s["title"].lower()), sections[0] if sections else None)
            disclaimer_physical = disclaimer_section["start_page_physical"] if disclaimer_section else (title_pages + 1)
            # Compute displayed page numbers relative to Disclaimer
            for s in sections:
                s["display_page"] = max(1, (s["start_page_physical"] - disclaimer_physical + 1))

            # Build TOC with iterative page offset
            def build_toc_inner(start_page: int, offset: int) -> str:
                # TOC using table layout for wkhtmltopdf compatibility (inner only)
                items = [(s["title"], s["display_page"]) for s in sections]
                toc_rows_html = "".join(
                    f"<tr><td class='toc-title'>{title}</td><td class='toc-page'>{page}</td></tr>"
                    for title, page in items
                )
                toc_inner = (
                    "<div class='toc-container'>"
                    "<h1>Table of Content</h1>"
                    + "<table class='toc-table'>" + toc_rows_html + "</table>"
                    "</div>"
                )
                return toc_inner

            toc_css = (
                ".toc-table{width:100%;border-collapse:collapse;}"
                ".toc-table td{border-bottom:1px solid #e6e6e6;padding:8px;}"
                ".toc-title{text-align:left;padding-left:20px;}"
                ".toc-page{text-align:center;width:3em;}"
            )

            toc_pages = 1
            for _ in range(5):
                offset = title_pages + toc_pages
                toc_inner_try = build_toc_inner(start_page=0, offset=offset)
                toc_pdf_try = get_pdf(
                    self._build_html_wrapper(toc_inner_try, css_content + toc_css),
                    options={"print-media-type": None},
                )
                measured = self._pdf_pages(toc_pdf_try)
                if measured == toc_pages:
                    break
                toc_pages = measured
            final_toc_inner = toc_inner_try

            # Build one combined HTML (single wkhtmltopdf run → continuous page numbers)
            combined_inner = "".join([
                (str(title_div) if title_div else ""),
                # Ensure TOC starts on a new page
                "<div class='page-break'></div>" + final_toc_inner,
            ] + ["<div class='page-break'></div>" + s["html"] for s in sections])

            combined_html = self._build_html_wrapper(
                combined_inner,
                css_content + toc_css + "\n.page-break{page-break-before:always;}",
                page_offset=(disclaimer_physical ),
            )
            merged_pdf = get_pdf(combined_html, options={"print-media-type": None})

            file_name = f"GHG_Report_{self.name}_{frappe.utils.nowdate()}.pdf"
            file_doc = frappe.get_doc({
                "doctype": "File",
                "file_name": file_name,
                "file_type": "pdf",
                "attached_to_doctype": self.doctype,
                "attached_to_name": self.name,
                "content": merged_pdf,
            })
            file_doc.insert()

            return {
                "success": True,
                "message": f"PDF (with TOC) generated successfully: {file_name}",
                "file_url": file_doc.file_url,
                "file_name": file_name,
            }
        except Exception as e:
            error_msg = f"Error generating PDF with TOC for GHG Report {self.name}: {str(e)}"
            frappe.log_error(error_msg)
            frappe.logger().error(error_msg)
            return {"success": False, "message": f"Error generating PDF: {str(e)}"}

@frappe.whitelist()
def generate_ghg_report_pdf(doctype, name):
    """Server-side method to generate PDF"""
    try:
        frappe.logger().info(f"generate_ghg_report_pdf called for {doctype} {name}")
        
        if not frappe.db.exists(doctype, name):
            return {"success": False, "message": f"Document {doctype} {name} not found"}
        
        doc = frappe.get_doc(doctype, name)
        result = doc.generate_pdf_with_toc()
        
        frappe.logger().info(f"PDF generation result: {result}")
        return result
        
    except Exception as e:
        error_msg = f"Error in generate_ghg_report_pdf: {str(e)}"
        frappe.log_error(error_msg)
        frappe.logger().error(error_msg)
        return {"success": False, "message": str(e)}

# -------------------- helpers to auto-fill tables from other doctypes --------------------
def _is_admin() -> bool:
    """Return True if current user is System Manager (admin-like)."""
    try:
        return "System Manager" in frappe.get_roles(frappe.session.user)
    except Exception:
        return False


def _year_window(year: int):
    start = frappe.utils.getdate(f"{year}-01-01")
    end = frappe.utils.getdate(f"{year}-12-31")
    return start, end


# --- GHG Reductions and Removals Enhancements ---
# Change this to your actual source doctype that users fill for reductions
REDUCTION_SRC_DOCTYPE = "GHG Reduction Entry"


def _fetch_reduction_entries(company: str, year: int):
    start, end = _year_window(year)
    filters = {"company": company, "date": ["between", [start, end]]}
    if not _is_admin():
        filters["owner"] = frappe.session.user

    if not frappe.db.exists("DocType", REDUCTION_SRC_DOCTYPE):
        return []

    return frappe.get_all(
        REDUCTION_SRC_DOCTYPE,
        filters=filters,
        fields=[
            "project_name",
            "reduction_type",
            "amount_tco2e",
            "date",
            "status",
            "description",
            "scope_category_impacted",
        ],
        order_by="date asc",
    )


def _append_reductions(doc, company: str, year: int) -> None:
    """Append rows to `ghg_reduction_line` from the reduction source doctype.

    Uses current child schema: initiative, description, reduction_achieved, scope_category_impacted.
    """
    entries = _fetch_reduction_entries(company, year)
    if not entries:
        return

    # Optional: clear existing rows so auto-generate is idempotent
    if getattr(doc, "ghg_reduction_line", None):
        doc.set("ghg_reduction_line", [])

    for r in entries:
        doc.append(
            "ghg_reduction_line",
            {
                "initiative": r.get("project_name") or r.get("description"),
                "description": r.get("description"),
                "reduction_achieved": r.get("amount_tco2e") or 0,
                "scope_category_impacted": r.get("scope_category_impacted") or r.get("reduction_type"),
            },
        )


# --- Organizational Boundaries ---
# Primary source; set to a doctype that lists business units/sites for each company
BOUNDARY_SRC_DOCTYPE = "Company Unit"


def _fetch_boundaries(company: str):
    """Fetch organizational boundary rows from Onboarding Form Units (Company Unit child).

    We use the latest Onboarding Form for the given company (prefer submitted),
    then read its child table `units` (doctype: Company Unit) and map to boundary rows.
    """
    # Find latest submitted onboarding form for this company_name; fallback to latest any
    ob = frappe.get_all(
        "Onboarding Form",
        filters={"company_name": company, "docstatus": 1},
        fields=["name"],
        order_by="modified desc",
        limit=1,
    )
    if not ob:
        ob = frappe.get_all(
            "Onboarding Form",
            filters={"company_name": company},
            fields=["name"],
            order_by="modified desc",
            limit=1,
        )
    if not ob:
        return []

    units = frappe.get_all(
        "Company Unit",
        filters={"parenttype": "Onboarding Form", "parent": ob[0].name},
        fields=["name_of_unit", "location_name", "address", "type_of_unit"],
        order_by="idx asc",
    )

    rows = []
    for u in units:
        rows.append({
            "business_unit": u.get("name_of_unit"),
            "location": u.get("location_name") or u.get("address"),
            "purpose": u.get("type_of_unit"),
            "included": 1,
            "reason_exclusion": "",
        })
    return rows


def _append_boundaries(doc, company: str) -> None:
    rows = _fetch_boundaries(company)
    if not rows:
        return

    # Optional: clear existing boundary rows before appending
    if getattr(doc, "ghg_boundary_line", None):
        doc.set("ghg_boundary_line", [])

    for b in rows:
        doc.append(
            "ghg_boundary_line",
            {
                "business_unit": b.get("business_unit"),
                "location": b.get("location"),
                "purpose": b.get("purpose"),
                "included": 1 if b.get("included") in (1, True, "Yes") else 0,
                "reason_exclusion": b.get("reason_exclusion"),
            },
        )

# --- Emissions and Removals Summary (GHG Inventory Line) ---
def _safe_sum(values):
	total = 0.0
	for v in values:
		try:
			total += float(v or 0)
		except Exception:
			continue
	return total


def _sum_records(doctype: str, company: str, start, end, gas_fields, total_field: str | None = None):
	"""Sum rows for a source doctype within date window and optional company filter.

	- gas_fields: per-gas numeric fieldnames to sum (e.g., ["eco2","ech4","en20"]).
	- total_field: overall tCO2e field to sum when per-gas is not available.
	"""
	if not frappe.db.exists("DocType", doctype):
		return {"per_gas": {}, "total": 0.0}

	meta = frappe.get_meta(doctype)
	filters = {"date": ["between", [start, end]]}
	# Apply company filter only if field exists
	if meta.has_field("company") and company:
		filters["company"] = company
	# Apply owner filter for non-admin users if there is no company field
	if not _is_admin() and not meta.has_field("company"):
		filters["owner"] = frappe.session.user

	# Select only present fields
	selected_fields = ["name", "date"]
	present_gas = [f for f in gas_fields if meta.has_field(f)]
	selected_fields.extend(present_gas)
	if total_field and meta.has_field(total_field):
		selected_fields.append(total_field)

	rows = frappe.get_all(doctype, filters=filters, fields=selected_fields, order_by="date asc")

	per_gas_sum = {f: 0.0 for f in present_gas}
	total_sum = 0.0
	for r in rows:
		for f in present_gas:
			per_gas_sum[f] += float(r.get(f) or 0)
		if total_field and total_field in r:
			total_sum += float(r.get(total_field) or 0)

	return {"per_gas": per_gas_sum, "total": total_sum}


def _append_inventory_lines(doc, company: str, year: int) -> None:
	"""Populate `ghg_inventory_line` by aggregating Scope 1/2 sources.

	Sources detected:
	  - Stationary Emissions → Scope 1, Category 1, Direct (CO₂/CH₄/N₂O if available)
	  - Fugitive Simple → Scope 1, Category 1, Direct (Aggregate)
	  - Electricity Purchased → Scope 2, Category 2, Indirect (Aggregate)

	Base-year window: uses doc.base_year if set, else (year - 1).
	"""
	start_current, end_current = _year_window(year)
	base_year = int(doc.base_year) if getattr(doc, "base_year", None) else (year - 1)
	start_base, end_base = _year_window(base_year)

	# Clear old rows for idempotency
	if getattr(doc, "ghg_inventory_line", None):
		doc.set("ghg_inventory_line", [])

	# Scope 1 - Category 1: Stationary Emissions (per gas if available)
	st_cur = _sum_records("Stationary Emissions", company, start_current, end_current, ["eco2", "ech4", "en20"], total_field="etco2eq")
	st_base = _sum_records("Stationary Emissions", company, start_base, end_base, ["eco2", "ech4", "en20"], total_field="etco2eq")

	gas_map = {
		"eco2": "CO₂",
		"ech4": "CH₄",
		"en20": "N₂O",
	}
	# If per-gas values exist, append lines per gas
	if any(v > 0 for v in st_cur["per_gas"].values()) or any(v > 0 for v in st_base["per_gas"].values()):
		for fieldname, gas in gas_map.items():
			cur_v = float(st_cur["per_gas"].get(fieldname) or 0)
			base_v = float(st_base["per_gas"].get(fieldname) or 0)
			if cur_v == 0 and base_v == 0:
				continue
			doc.append(
				"ghg_inventory_line",
				{
					"iso_category": "Category 1",
					"scope": "1",
					"direct_or_indirect": "Direct",
					"ghg_type": gas,
					"emissions_current": cur_v,
					"emissions_base": base_v,
				},
			)
	else:
		# Fallback to aggregate if no per-gas breakdown
		if st_cur["total"] > 0 or st_base["total"] > 0:
			doc.append(
				"ghg_inventory_line",
				{
					"iso_category": "Category 1",
					"scope": "1",
					"direct_or_indirect": "Direct",
					"ghg_type": "Aggregate",
					"emissions_current": float(st_cur["total"]),
					"emissions_base": float(st_base["total"]),
				},
			)

	# Scope 1 - Category 1: Fugitive Simple (aggregate)
	fg_cur = _sum_records("Fugitive Simple", company, start_current, end_current, [], total_field="etco2eq")
	fg_base = _sum_records("Fugitive Simple", company, start_base, end_base, [], total_field="etco2eq")
	if fg_cur["total"] > 0 or fg_base["total"] > 0:
		doc.append(
			"ghg_inventory_line",
			{
				"iso_category": "Category 1",
				"scope": "1",
				"direct_or_indirect": "Direct",
				"ghg_type": "Aggregate",
				"emissions_current": float(fg_cur["total"]),
				"emissions_base": float(fg_base["total"]),
			},
		)

	# Scope 2 - Category 2: Electricity Purchased (aggregate)
	el_cur = _sum_records("Electricity Purchased", company, start_current, end_current, [], total_field="etco2eq")
	el_base = _sum_records("Electricity Purchased", company, start_base, end_base, [], total_field="etco2eq")
	if el_cur["total"] > 0 or el_base["total"] > 0:
		doc.append(
			"ghg_inventory_line",
			{
				"iso_category": "Category 2",
				"scope": "2",
				"direct_or_indirect": "Indirect",
				"ghg_type": "Aggregate",
				"emissions_current": float(el_cur["total"]),
				"emissions_base": float(el_base["total"]),
			},
		)

	# Future: Scope 3 mappings → append under Category 3..6 as Aggregate

@frappe.whitelist()
def auto_create_and_generate_pdf(organization_name: str | None = None, year: int | None = None):
    """Create a GHG Report with sensible defaults, generate PDF, and return file_url.
    Used by the listview primary action (Download Report).
    """
    try:
        # Defaults
        today = frappe.utils.getdate()
        if not year:
            year = today.year
        start = frappe.utils.getdate(f"{year}-01-01")
        end = frappe.utils.getdate(f"{year}-12-31")
        if not organization_name:
            organization_name = frappe.defaults.get_user_default("company") or ""

        title = f"Annual GHG Emissions and Reductions Report for {organization_name or 'Organization'}"

        doc = frappe.get_doc({
            "doctype": "GHG Report",
            "organization_name": organization_name,
            "report_title": title,
            "period_from": start,
            "period_to": end,
            "date_of_report": today,
            "version": "1.0",
            "prepared_by": "Climoro",
            "frequency": "Annual",
            "report_type": "Annual GHG emissions and reductions report"
        })
        doc.insert(ignore_permissions=True)
        # Auto-load organizational boundaries and reduction initiatives
        try:
            if organization_name:
                _append_boundaries(doc, company=organization_name)
            if organization_name and year:
                _append_reductions(doc, company=organization_name, year=year)
                _append_inventory_lines(doc, company=organization_name, year=year)
            doc.save(ignore_permissions=True)
        except Exception as _e:
            frappe.log_error(f"auto_create_and_generate_pdf: population error: {_e}")
        # Always use the HTML/CSS template layout with TOC
        result = doc.generate_pdf_with_toc()
        result["name"] = doc.name
        return result
    except Exception as e:
        frappe.log_error(f"auto_create_and_generate_pdf error: {e}")
        return {"success": False, "message": str(e)}
