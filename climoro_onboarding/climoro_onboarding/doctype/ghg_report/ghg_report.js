// GHG Report Custom JavaScript

frappe.ui.form.on('GHG Report', {
    refresh: function(frm) {
        // Only keep Generate PDF
        if (frm.doc.docstatus === 0) {
            frm.add_custom_button(__('Generate PDF'), function() {
                generatePDF(frm);
            }).addClass('btn-success');
        }
    },
});

function generatePDF(frm, autoDownload=false) {
    if (!frm.doc.name) {
        frappe.msgprint(__('Please save the document first before generating PDF.'));
        return;
    }

    frm.dashboard.show_progress('Generating PDF...', 50, __('Please wait...'));

    frappe.call({
        method: 'climoro_onboarding.climoro_onboarding.doctype.ghg_report.ghg_report.generate_ghg_report_pdf',
        args: {
            doctype: frm.doctype,
            name: frm.doc.name
        },
        callback: function(r) {
            frm.dashboard.hide_progress();
            if (r.message && r.message.success) {
                frappe.show_alert({ message: r.message.message, indicator: 'green' });
                frm.refresh();
            } else {
                frappe.show_alert({
                    message: r.message ? r.message.message : __('Error generating PDF'),
                    indicator: 'red'
                });
            }
        },
        error: function(err) {
            frm.dashboard.hide_progress();
            frappe.show_alert({ message: __('Error generating PDF. Please try again.'), indicator: 'red' });
        }
    });
}
