// Client-side script for Onboarding Form doctype
console.log('🔧 Onboarding Form JS loaded');

frappe.ui.form.on('Onboarding Form', {
    refresh: function(frm) {
        console.log('🔄 Form refreshed');
        // Initialize sub-industry options when form loads
        if (frm.doc.industry_type) {
            console.log('🏭 Industry type found on refresh:', frm.doc.industry_type);
            updateSubIndustryOptions(frm);
        }
        
        // Set up watchers for industry_type changes
        frm.set_df_property('industry_type', 'onchange', function() {
            console.log('🏭 Industry type onchange triggered');
            updateSubIndustryOptions(frm);
        });
        
        // Also listen for field changes
        frm.fields_dict.industry_type.$input.on('change', function() {
            console.log('🏭 Industry type field change detected');
            setTimeout(() => updateSubIndustryOptions(frm), 100);
        });
        
        // Add a manual trigger button for testing
        frm.add_custom_button('Update Sub-Industry', function() {
            console.log('🔧 Manual trigger button clicked');
            updateSubIndustryOptions(frm);
        });
    },
    
    industry_type: function(frm) {
        console.log('🏭 Industry type changed to:', frm.doc.industry_type);
        // Update sub-industry options when industry type changes
        updateSubIndustryOptions(frm);
    },
    
    sub_industry_type: function(frm) {
        console.log('🏭 Sub-industry type changed to:', frm.doc.sub_industry_type);
        console.log('🏭 Sub-industry type doc value:', frm.doc.sub_industry_type);
    }
});

function updateSubIndustryOptions(frm) {
    console.log('🔄 updateSubIndustryOptions called');
    
    const industryType = frm.doc.industry_type;
    const subIndustryField = frm.get_field('sub_industry_type');
    
    console.log('🏭 Industry type:', industryType);
    console.log('📋 Sub-industry field:', subIndustryField);
    console.log('📋 Sub-industry field type:', typeof subIndustryField);
    console.log('📋 Sub-industry field properties:', Object.keys(subIndustryField || {}));
    
    if (!industryType) {
        console.log('❌ No industry type selected, clearing options');
        // Clear options if no industry selected
        subIndustryField.set_options('');
        frm.set_value('sub_industry_type', '');
        return;
    }
    
    console.log('📞 Calling backend function...');
    
    // Call the backend function to get sub-industry options
    frappe.call({
        method: 'climoro_onboarding.climoro_onboarding.doctype.onboarding_form.onboarding_form.get_sub_industry_options',
        args: {
            industry_type: industryType
        },
        callback: function(r) {
            console.log('📥 Backend response:', r);
            if (r.message) {
                console.log('✅ Got options:', r.message);
                
                // Get the select element directly
                const selectElement = subIndustryField.$input || subIndustryField.$wrapper.find('select');
                console.log('🔍 Select element:', selectElement);
                
                if (selectElement && selectElement.length > 0) {
                    console.log('🔍 Found select element, clearing and adding options');
                    
                    // Store current selection before clearing
                    const currentSelection = frm.doc.sub_industry_type;
                    console.log('🔍 Current selection before clearing:', currentSelection);
                    
                    // Clear existing options
                    selectElement.empty();
                    
                    // Add default option
                    selectElement.append('<option value="">Select Sub-Industry Type</option>');
                    
                    // Add new options
                    r.message.forEach(option => {
                        const isSelected = option === currentSelection ? 'selected' : '';
                        selectElement.append(`<option value="${option}" ${isSelected}>${option}</option>`);
                    });
                    
                    // Restore selection if it exists in new options
                    if (currentSelection && r.message.includes(currentSelection)) {
                        console.log('🔍 Restoring selection:', currentSelection);
                        selectElement.val(currentSelection);
                    }
                    
                    console.log('✅ Options added to select element');
                    console.log('🔍 Current select element HTML:', selectElement.html());
                    
                    // Add change event listener to capture selection
                    selectElement.off('change.subIndustry').on('change.subIndustry', function() {
                        const selectedValue = $(this).val();
                        console.log('🎯 Sub-industry option selected:', selectedValue);
                        console.log('🎯 Select element value:', $(this).val());
                        console.log('🎯 Form doc value before update:', frm.doc.sub_industry_type);
                        
                        // Update the form's document model
                        frm.set_value('sub_industry_type', selectedValue);
                        
                        console.log('🎯 Form doc value after update:', frm.doc.sub_industry_type);
                        console.log('🎯 Field value after update:', frm.get_field('sub_industry_type').value);
                    });
                } else {
                    console.log('❌ Select element not found, trying alternative method');
                    
                    // Alternative method: use Frappe's set_options
                    const options = r.message.join('\n');
                    console.log('🔍 Setting options using set_options:', options);
                    subIndustryField.set_options(options);
                    
                    // Force refresh
                    frm.refresh_field('sub_industry_type');
                    console.log('✅ Field refreshed after set_options');
                }
                
                // Clear the current value if it's not in the new options
                const currentValue = frm.doc.sub_industry_type;
                if (currentValue && !r.message.includes(currentValue)) {
                    frm.set_value('sub_industry_type', '');
                }
                
                console.log('✅ Options set successfully');
                
            } else {
                console.log('❌ No options returned from backend');
                // Clear options if no data returned
                const selectElement = subIndustryField.$input || subIndustryField.$wrapper.find('select');
                if (selectElement && selectElement.length > 0) {
                    selectElement.empty();
                    selectElement.append('<option value="">Select Industry Type First</option>');
                }
                frm.set_value('sub_industry_type', '');
            }
        },
        error: function(err) {
            console.error('❌ Error fetching sub-industry options:', err);
            subIndustryField.set_options('');
            frm.set_value('sub_industry_type', '');
        }
    });
} 