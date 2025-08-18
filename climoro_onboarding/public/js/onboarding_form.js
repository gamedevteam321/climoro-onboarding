// Onboarding Form JavaScript for Frappe Desk
frappe.ui.form.on('Onboarding Form', {
    refresh: function(frm) {
        // Add custom buttons or functionality
        if (frm.doc.status === 'Draft') {
            frm.add_custom_button(__('Submit Application'), function() {
                frm.set_value('status', 'Submitted');
                frm.save();
            });
        }
    },
    
    validate: function(frm) {
        // Custom validation
        if (frm.doc.email && !frappe.utils.validate_email(frm.doc.email)) {
            frappe.throw(__('Please enter a valid email address'));
        }
        
        if (frm.doc.phone_number && frm.doc.phone_number.length < 10) {
            frappe.throw(__('Phone number must be at least 10 digits'));
        }
    }
});

// Company Unit child table
frappe.ui.form.on('Company Unit', {
    refresh: function(frm, cdt, cdn) {
        // Add custom functionality for units
    },
    
    validate: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        
        if (row.name_of_unit && row.name_of_unit.length < 2) {
            frappe.throw(__('Unit name must be at least 2 characters long'));
        }
        
        if (row.size_of_unit && row.size_of_unit <= 0) {
            frappe.throw(__('Unit size must be greater than 0'));
        }
    }
});

// Assigned User child table
frappe.ui.form.on('Assigned User', {
    refresh: function(frm, cdt, cdn) {
        // Add custom functionality for users
    },
    
    validate: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        
        if (row.email && !frappe.utils.validate_email(row.email)) {
            frappe.throw(__('Please enter a valid email address'));
        }
        
        if (row.first_name && row.first_name.length < 2) {
            frappe.throw(__('First name must be at least 2 characters long'));
        }
    }
});