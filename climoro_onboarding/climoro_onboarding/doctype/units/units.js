// Units DocType client script
frappe.ui.form.on('Units', {
    refresh: function(frm) {
        // Add company filter for non-super admin users
        if (!frappe.user_roles.includes('System Manager') && 
            !frappe.user_roles.includes('Administrator')) {
            
            frappe.call({
                method: 'climoro_onboarding.climoro_onboarding.doctype.units.units.get_user_company_filter',
                callback: function(r) {
                    if (r.message && r.message.company) {
                        frm.set_value('company', r.message.company);
                        frm.set_df_property('company', 'read_only', 1);
                    }
                }
            });
        }
    },
    
    company: function(frm) {
        // Filter any related fields based on company if needed
        frm.refresh_field('company');
    }
});
