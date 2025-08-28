// Unit Users DocType client script
frappe.ui.form.on('Unit Users', {
    refresh: function(frm) {
        // Set up unit filtering based on company
        frm.set_query('assigned_unit', function() {
            return {
                query: 'climoro_onboarding.climoro_onboarding.doctype.unit_users.unit_users.get_filtered_units'
            };
        });
        
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
        
        // Add buttons for user management
        if (frm.doc.user_created && frm.doc.frappe_user_id) {
            frm.add_custom_button(__('View User'), function() {
                frappe.set_route('Form', 'User', frm.doc.frappe_user_id);
            });
            
            frm.add_custom_button(__('Reset Password'), function() {
                frappe.prompt([
                    {
                        fieldtype: 'Password',
                        label: 'New Password',
                        fieldname: 'new_password',
                        reqd: 1
                    }
                ], function(values) {
                    frappe.call({
                        method: 'frappe.core.doctype.user.user.reset_password',
                        args: {
                            user: frm.doc.frappe_user_id,
                            password: values.new_password
                        },
                        callback: function(r) {
                            if (!r.exc) {
                                frappe.show_alert({
                                    message: 'Password reset successfully',
                                    indicator: 'green'
                                });
                            }
                        }
                    });
                }, 'Reset Password');
            });
        }
        
        // Add generate password button
        if (frm.doc.create_user_account && !frm.doc.user_created) {
            frm.add_custom_button(__('Generate Password'), function() {
                frm.trigger('generate_password');
            });
        }
    },
    
    assigned_unit: function(frm) {
        // Auto-set company from selected unit
        if (frm.doc.assigned_unit) {
            frappe.db.get_value('Units', frm.doc.assigned_unit, 'company')
                .then(r => {
                    if (r.message && r.message.company) {
                        frm.set_value('company', r.message.company);
                    }
                });
        }
    },
    
    first_name: function(frm) {
        // Auto-generate username when first name changes
        if (frm.doc.first_name && frm.doc.email && frm.doc.create_user_account) {
            frm.trigger('generate_username');
        }
    },
    
    email: function(frm) {
        // Auto-generate username when email changes
        if (frm.doc.first_name && frm.doc.email && frm.doc.create_user_account) {
            frm.trigger('generate_username');
        }
    },
    
    create_user_account: function(frm) {
        if (frm.doc.create_user_account) {
            // Generate username and password
            frm.trigger('generate_username');
            frm.trigger('generate_password');
        } else {
            // Clear user creation fields
            frm.set_value('username', '');
            frm.set_value('password', '');
            frm.set_value('confirm_password', '');
        }
    },
    
    generate_username: function(frm) {
        if (frm.doc.first_name && frm.doc.email) {
            frappe.call({
                method: 'climoro_onboarding.climoro_onboarding.doctype.unit_users.unit_users.generate_username',
                args: {
                    first_name: frm.doc.first_name,
                    email: frm.doc.email
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value('username', r.message);
                    }
                }
            });
        }
    },
    
    generate_password: function(frm) {
        frappe.call({
            method: 'climoro_onboarding.climoro_onboarding.doctype.unit_users.unit_users.generate_secure_password',
            callback: function(r) {
                if (r.message) {
                    frm.set_value('password', r.message);
                    frm.set_value('confirm_password', r.message);
                }
            }
        });
    }
});
