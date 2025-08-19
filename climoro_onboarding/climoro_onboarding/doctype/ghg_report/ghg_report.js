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

function showLoading(message) {
    const msg = message || __('Generating report...');
    if (!window.__ghg_loading_dialog) {
        window.__ghg_loading_dialog = new frappe.ui.Dialog({ title: __('Please wait'), fields: [{ fieldtype: 'HTML', fieldname: 'content' }] });
    }
    window.__ghg_loading_dialog.set_value('content', `<div style="display:flex;gap:12px;align-items:center;"><span class="spinner-border" role="status" aria-hidden="true"></span><div>${frappe.utils.escape_html(msg)}</div></div>`);
    window.__ghg_loading_dialog.show();
}

function hideLoading() {
    if (window.__ghg_loading_dialog) window.__ghg_loading_dialog.hide();
}

function generatePDF(frm) {
    if (!frm.doc.name) {
        frappe.msgprint(__('Please save the document first before generating PDF.'));
        return;
    }

    showLoading(__('Generating report...'));

    frappe.call({
        method: 'climoro_onboarding.climoro_onboarding.doctype.ghg_report.ghg_report.generate_ghg_report_pdf',
        args: {
            doctype: frm.doctype,
            name: frm.doc.name
        },
        callback: function(r) {
            hideLoading();
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
            hideLoading();
            frappe.show_alert({ message: __('Error generating PDF. Please try again.'), indicator: 'red' });
        }
    });
}
