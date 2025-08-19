frappe.listview_settings['GHG Report'] = {
    onload(listview) {
        addAutoBtn(listview);
    },
    refresh(listview) {
        addAutoBtn(listview);
    }
};

function addAutoBtn(listview) {
    const $wrap = listview.page.wrapper;
    if ($wrap.find('.btn-auto-download-ghg').length) return;
    listview.page.add_inner_button(__('Auto Download PDF'), () => openAutoDownloadDialog(listview))
        .addClass('btn-auto-download-ghg btn-primary');
}

function openAutoDownloadDialog(listview){
    const d = new frappe.ui.Dialog({
        title: __('Generate GHG Report PDF'),
        fields: [
            { fieldtype: 'Link', fieldname: 'organization_name', label: __('Organization Name'), options: 'Company', reqd: 0 },
            { fieldtype: 'Int', fieldname: 'year', label: __('Year'), reqd: 0, default: (new Date()).getFullYear() }
        ],
        primary_action_label: __('Generate'),
        primary_action: (values) => {
            d.hide();
            frappe.call({
                method: 'climoro_onboarding.climoro_onboarding.doctype.ghg_report.ghg_report.auto_create_and_generate_pdf',
                args: values || {},
                callback: function(r) {
                    if (r.message && r.message.success && r.message.file_url) {
                        const url = r.message.file_url;
                        const link = document.createElement('a');
                        link.href = url; link.download = (url.split('/').pop()) || 'GHG_Report.pdf';
                        document.body.appendChild(link); link.click(); document.body.removeChild(link);
                        frappe.show_alert({message: __('PDF Download started'), indicator: 'green'});
                        listview.refresh();
                    } else {
                        frappe.msgprint({message: (r.message && r.message.message) || __('Failed to generate PDF'), indicator: 'red'});
                    }
                },
                error: function(err){
                    console.error(err);
                    frappe.msgprint(__('Error generating PDF'));
                }
            });
        }
    });
    d.show();
}
