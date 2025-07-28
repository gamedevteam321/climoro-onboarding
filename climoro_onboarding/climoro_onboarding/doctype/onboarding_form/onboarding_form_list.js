frappe.listview_settings['Onboarding Form'] = {
    add_fields: ["total_units", "total_users", "units_summary", "status"],
    get_indicator: function(doc) {
        if (doc.status === "Submitted") return [__("Submitted"), "orange", "status,=,Submitted"];
        if (doc.status === "Approved") return [__("Approved"), "green", "status,=,Approved"];
        if (doc.status === "Rejected") return [__("Rejected"), "red", "status,=,Rejected"];
        return [__("Draft"), "gray", "status,=,Draft"];
    },
    onload: function(listview) {
        // Add custom styling for summary fields
        listview.page.add_inner_button(__("Refresh Summaries"), function() {
            frappe.call({
                method: "climoro_onboarding.climoro_onboarding.doctype.onboarding_form.onboarding_form.refresh_all_summaries",
                callback: function(r) {
                    if (r.message) {
                        frappe.msgprint(__("Summaries refreshed successfully!"));
                        listview.refresh();
                    }
                }
            });
        });
    },
    formatters: {
        total_units: function(value, doc, cdf, cdt) {
            return `<span class="badge badge-primary">${value || 0}</span>`;
        },
        total_users: function(value, doc, cdf, cdt) {
            return `<span class="badge badge-info">${value || 0}</span>`;
        },
        units_summary: function(value, doc, cdf, cdt) {
            if (!value || value === "No units added") {
                return `<span class="text-muted">No units</span>`;
            }
            return `<span class="text-primary">${value}</span>`;
        }
    }
}; 