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

function showLoading(message){
    const msg = message || __('Generating report...');
    if (!window.__ghg_loading_dialog) {
        window.__ghg_loading_dialog = new frappe.ui.Dialog({ title: __('Please wait'), fields: [{ fieldtype: 'HTML', fieldname: 'content' }] });
    }
    window.__ghg_loading_dialog.set_value('content', `<div style="display:flex;gap:12px;align-items:center;"><span class="spinner-border" role="status" aria-hidden="true"></span><div>${frappe.utils.escape_html(msg)}</div></div>`);
    window.__ghg_loading_dialog.show();
}

function hideLoading(){ if (window.__ghg_loading_dialog) window.__ghg_loading_dialog.hide(); }

function openAutoDownloadDialog(listview){
    const d = new frappe.ui.Dialog({
        title: __('Generate GHG Report PDF'),
        fields: [
            { 
                fieldtype: 'Link', 
                fieldname: 'organization_name', 
                label: __('Organization Name'), 
                options: 'Company', 
                reqd: 0,
                description: __('Leave empty to use your default company (non-admin users)')
            },
            { 
                fieldtype: 'Int', 
                fieldname: 'year', 
                label: __('Year'), 
                reqd: 0, 
                default: (new Date()).getFullYear(),
                description: __('Used if start/end dates are not specified')
            },
            { 
                fieldtype: 'Date', 
                fieldname: 'start_date', 
                label: __('Start Date'), 
                reqd: 0,
                description: __('Leave empty to use full year from Year field')
            },
            { 
                fieldtype: 'Date', 
                fieldname: 'end_date', 
                label: __('End Date'), 
                reqd: 0,
                description: __('Leave empty to use full year from Year field')
            }
        ],
        primary_action_label: __('Generate'),
        primary_action: (values) => {
            // Validate date inputs
            if (values.start_date && values.end_date) {
                const start = new Date(values.start_date);
                const end = new Date(values.end_date);
                if (start > end) {
                    frappe.msgprint(__('Start Date must be before End Date'));
                    return;
                }
            }
            
            d.hide();
            showLoading(__('Generating report...'));
            
            // Prepare arguments for the backend function
            const args = {
                organization_name: values.organization_name || null,
                year: values.year || null,
                start_date: values.start_date || null,
                end_date: values.end_date || null
            };
            
            frappe.call({
                method: 'climoro_onboarding.climoro_onboarding.doctype.ghg_report.ghg_report.auto_create_and_generate_pdf',
                args: args,
                callback: function(r) {
                    hideLoading();
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
                    hideLoading();
                    console.error(err);
                    frappe.msgprint(__('Error generating PDF'));
                }
            });
        }
    });
    d.show();
}
