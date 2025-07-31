frappe.listview_settings['Onboarding Form'] = {
    add_fields: ["status"],
    get_indicator: function(doc) {
        if (doc.status === "Submitted") return [__("Submitted"), "orange", "status,=,Submitted"];
        if (doc.status === "Approved") return [__("Approved"), "green", "status,=,Approved"];
        if (doc.status === "Rejected") return [__("Rejected"), "red", "status,=,Rejected"];
        return [__("Draft"), "gray", "status,=,Draft"];
    }
}; 