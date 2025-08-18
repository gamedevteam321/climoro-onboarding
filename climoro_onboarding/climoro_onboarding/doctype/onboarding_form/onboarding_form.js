// Client-side script for Onboarding Form doctype
// Copyright (c) 2024, Climoro Onboarding and contributors
// For license information, please see license.txt

// Google Maps Variables
// let map;
// let selectedMarker;
// let selectedCoordinates = null;
// let searchBox;
// let currentMapField = null;

console.log('🔧 Onboarding Form JS loaded');

frappe.ui.form.on('Onboarding Form', {
	refresh: function(frm) {
		console.log('=== DEBUG: Form refresh triggered ===');
		console.log('Form name:', frm.doc.name);
		console.log('Form status:', frm.doc.status);
		
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
		// frm.add_custom_button('Update Sub-Industry', function() {
		// 	console.log('🔧 Manual trigger button clicked');
		// 	updateSubIndustryOptions(frm);
		// });
		

		
		// Initialize GHG Accounting dynamic behavior
		updateStep5Visibility(frm);
		
		// Temporarily disable map functionality to avoid errors
		// const gpsField = frm.get_field('gps_coordinates');
		// if (gpsField && gpsField.$wrapper) {
		// 	addMapToField(frm, 'gps_coordinates');
		// }
		
		// Add map functionality to company units
		// if (frm.doc.units && frm.doc.units.length > 0) {
		// 	frm.doc.units.forEach((unit, index) => {
		// 		addMapToChildTableField(frm, 'units', index, 'gps_coordinates');
		// 	});
		// }

		// --- Approve/Reject logic for admin ---
		console.log('=== DEBUG: Checking Approve/Reject conditions ===');
		console.log('Status:', frm.doc.status);
		console.log('Current user:', frappe.session.user);
		console.log('frappe.user_roles exists:', !!frappe.user_roles);
		console.log('User roles:', frappe.user_roles);
		console.log('Is System Manager:', frappe.user_roles && frappe.user_roles.includes('System Manager'));
		console.log('Is Administrator:', frappe.user_roles && frappe.user_roles.includes('Administrator'));
		
		// Check if user has any admin-like roles
		const adminRoles = ['System Manager', 'Administrator', 'Super Admin'];
		const hasAdminRole = frappe.user_roles && frappe.user_roles.some(role => adminRoles.includes(role));
		console.log('Has any admin role:', hasAdminRole);
		console.log('Status check:', frm.doc.status === 'Submitted');
		console.log('Admin role check:', hasAdminRole);
		console.log('Both conditions met:', frm.doc.status === 'Submitted' && hasAdminRole);
		
		if (
			frm.doc.status === 'Submitted' &&
			hasAdminRole
		) {
			console.log('=== DEBUG: Adding Approve/Reject buttons ===');
			
			// Add Approve button
			frm.add_custom_button(__('Approve'), function() {
				console.log('=== DEBUG: Approve button clicked ===');
				
				// Show loading popup using helper function
				const processingPopup = showProcessingPopup(
					'Processing Onboarding Approval',
					'Creating company and user accounts...',
					'#007bff'
				);
				
				frappe.call({
					method: 'climoro_onboarding.climoro_onboarding.doctype.onboarding_form.onboarding_form.approve_application',
					args: { docname: frm.doc.name },
					callback: function(r) {
						console.log('=== DEBUG: Approve callback response ===', r);
						console.log('=== DEBUG: Response message ===', r.message);
						console.log('=== DEBUG: Response success ===', r.message && r.message.success);
						console.log('=== DEBUG: Response exc ===', r.exc);
						
						// Hide loading popup and spinner
						processingPopup.hide();
						
						if (!r.exc && r.message && r.message.success) {
							frappe.show_alert({ 
								message: __('🎉 Application Approved Successfully! Company and users have been created.'), 
								indicator: 'green' 
							});
							// Force reload the document to show updated status
							frm.reload_doc();
						} else {
							console.error('=== DEBUG: Approve failed ===', r.exc || (r.message && r.message.message));
							frappe.show_alert({ 
								message: __('❌ Approval failed: ' + (r.exc || (r.message && r.message.message))), 
								indicator: 'red' 
							});
						}
					},
					error: function(xhr, status, error) {
						console.error('=== DEBUG: Approve error ===', {xhr, status, error});
						
						// Hide loading popup and spinner
						processingPopup.hide();
						
						frappe.show_alert({ 
							message: __('❌ Approval failed: ' + error), 
							indicator: 'red' 
						});
					}
				});
			}, __('Actions'));

			// Add Reject button
			frm.add_custom_button(__('Reject'), function() {
				console.log('=== DEBUG: Reject button clicked ===');
				frappe.prompt([
					{
						fieldtype: 'Small Text',
						label: 'Reason for Rejection',
						fieldname: 'reason',
						reqd: 1
					}
				], function(values) {
					console.log('=== DEBUG: Reject reason provided ===', values);
					
					// Show loading popup using helper function
					const processingPopup = showProcessingPopup(
						'Processing Application Rejection',
						'Sending rejection notification...',
						'#dc3545'
					);
					
					frappe.call({
						method: 'climoro_onboarding.climoro_onboarding.doctype.onboarding_form.onboarding_form.reject_application',
						args: { docname: frm.doc.name, reason: values.reason },
						callback: function(r) {
							console.log('=== DEBUG: Reject callback response ===', r);
							
							// Hide loading popup and spinner
							processingPopup.hide();
							
							if (!r.exc) {
								frappe.show_alert({ 
									message: __('❌ Application Rejected Successfully! Rejection email has been sent.'), 
									indicator: 'red' 
								});
								frm.reload_doc();
							} else {
								frappe.show_alert({ 
									message: __('❌ Rejection failed: ' + (r.exc || 'Unknown error')), 
									indicator: 'red' 
								});
							}
						},
						error: function(xhr, status, error) {
							console.error('=== DEBUG: Reject error ===', {xhr, status, error});
							
							// Hide loading popup and spinner
							processingPopup.hide();
							
							frappe.show_alert({ 
								message: __('❌ Rejection failed: ' + error), 
								indicator: 'red' 
							});
						}
					});
				});
			}, __('Actions'));
			
			console.log('=== DEBUG: Approve/Reject buttons added successfully ===');
		} else {
			console.log('=== DEBUG: Conditions not met for Approve/Reject buttons ===');
			console.log('Status check failed:', frm.doc.status !== 'Submitted');
			console.log('Admin role check failed:', !hasAdminRole);
		}
		
		// Enhance table display with delay to ensure tables are loaded
		setTimeout(() => enhanceTableDisplay(frm), 500);
	},
	
	industry_type: function(frm) {
		console.log('🏭 Industry type changed to:', frm.doc.industry_type);
		// Update sub-industry options when industry type changes
		updateSubIndustryOptions(frm);
	},
	
	sub_industry_type: function(frm) {
		console.log('🏭 Sub-industry type changed to:', frm.doc.sub_industry_type);
		console.log('🏭 Sub-industry type doc value:', frm.doc.sub_industry_type);
	},
	
	units_add: function(frm, cdt, cdn) {
		// Temporarily disable map functionality
		// const row = locals[cdt][cdn];
		// if (row) {
		// 	setTimeout(() => {
		// 		const index = frm.doc.units.findIndex(unit => unit.name === row.name);
		// 		if (index !== -1) {
		// 			addMapToChildTableField(frm, 'units', index, 'gps_coordinates');
		// 		}
		// 	}, 100);
		// }
		
		// Re-enhance table when new unit is added
		setTimeout(() => enhanceTableDisplay(frm), 100);
	},
	
	assigned_users_add: function(frm, cdt, cdn) {
		// Temporarily disable map functionality
		// const row = locals[cdt][cdn];
		// if (row) {
		// 	setTimeout(() => {
		// 		const index = frm.doc.assigned_users.findIndex(user => user.name === row.name);
		// 		if (index !== -1) {
		// 			addMapToChildTableField(frm, 'assigned_users', index, 'gps_coordinates');
		// 		}
		// 	}, 100);
		// }
		
		// Re-enhance table when new user is added
		setTimeout(() => enhanceTableDisplay(frm), 100);
	},
	
	// GHG Accounting Dynamic Behavior
	scopes_to_report_scope1: function(frm) {
		console.log('🌱 Scope 1 changed:', frm.doc.scopes_to_report_scope1);
		updateStep5Visibility(frm);
	},
	
	scopes_to_report_scope2: function(frm) {
		console.log('🌱 Scope 2 changed:', frm.doc.scopes_to_report_scope2);
		updateStep5Visibility(frm);
	},
	
	scopes_to_report_scope3: function(frm) {
		console.log('🌱 Scope 3 changed:', frm.doc.scopes_to_report_scope3);
		updateStep5Visibility(frm);
	},
	
	scopes_to_report_reductions: function(frm) {
		console.log('🌱 Reductions changed:', frm.doc.scopes_to_report_reductions);
		updateStep5Visibility(frm);
	},
	
	gases_to_report_co2: function(frm) {
		console.log('🌱 CO2 gas changed:', frm.doc.gases_to_report_co2);
	},
	
	gases_to_report_ch4: function(frm) {
		console.log('🌱 CH4 gas changed:', frm.doc.gases_to_report_ch4);
	},
	
	gases_to_report_n2o: function(frm) {
		console.log('🌱 N2O gas changed:', frm.doc.gases_to_report_n2o);
	},
	
	gases_to_report_hfcs: function(frm) {
		console.log('🌱 HFCs gas changed:', frm.doc.gases_to_report_hfcs);
	},
	
	gases_to_report_pfcs: function(frm) {
		console.log('🌱 PFCs gas changed:', frm.doc.gases_to_report_pfcs);
	},
	
	gases_to_report_sf6: function(frm) {
		console.log('🌱 SF6 gas changed:', frm.doc.gases_to_report_sf6);
	},
	
	gases_to_report_nf3: function(frm) {
		console.log('🌱 NF3 gas changed:', frm.doc.gases_to_report_nf3);
		// Handle NF3 visibility for semiconductor industry
		let industry_type = frm.doc.industry_type;
		
		// Check if industry is semiconductor-related
		if (industry_type && industry_type.toLowerCase().includes('semiconductor')) {
			// NF3 is available for semiconductor industry
			console.log('🌱 Semiconductor industry detected, NF3 available');
		} else {
			// Remove NF3 if not semiconductor industry
			if (selected_gases.includes('NF3')) {
				selected_gases = selected_gases.filter(gas => gas !== 'NF3');
				frm.set_value('gases_to_report', selected_gases);
				console.log('🌱 NF3 removed - not semiconductor industry');
			}
		}
	},
	
	// Step 5 Dynamic Field Handlers
	scope_1_intensity_reduction: function(frm) {
		if (!frm.doc.scope_1_intensity_reduction) {
			frm.set_value('scope_1_reduction_percentage', '');
			frm.set_value('scope_1_target_year', '');
		}
	},
	
	scope_2_intensity_reduction: function(frm) {
		if (!frm.doc.scope_2_intensity_reduction) {
			frm.set_value('scope_2_reduction_percentage', '');
			frm.set_value('scope_2_target_year', '');
		}
	},
	
	scope_3_intensity_reduction: function(frm) {
		if (!frm.doc.scope_3_intensity_reduction) {
			frm.set_value('scope_3_reduction_percentage', '');
			frm.set_value('scope_3_target_year', '');
		}
	},
	
	ghg_tracking_tools_excel: function(frm) {
		console.log('🌱 Excel tracking tool changed:', frm.doc.ghg_tracking_tools_excel);
	},
	
	ghg_tracking_tools_software: function(frm) {
		console.log('🌱 Software tracking tool changed:', frm.doc.ghg_tracking_tools_software);
		if (!frm.doc.ghg_tracking_tools_software) {
			frm.set_value('ghg_tracking_tools_software_name', '');
		}
	},
	
	ghg_tracking_tools_web_platform: function(frm) {
		console.log('🌱 Web platform tracking tool changed:', frm.doc.ghg_tracking_tools_web_platform);
	},
	
	monitoring_frequency: function(frm) {
		console.log('🌱 Monitoring frequency changed:', frm.doc.monitoring_frequency);
		if (frm.doc.monitoring_frequency !== 'Other') {
			frm.set_value('monitoring_frequency_other_text', '');
		}
	},
	

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

function addMapToField(frm, fieldname) {
	const field = frm.get_field(fieldname);
	if (!field || !field.$wrapper) return;
	
	// Create map button
	const mapButton = $(`
		<button type="button" class="btn btn-sm btn-default" style="margin-left: 5px;">
			<i class="fa fa-map-marker"></i> Select Location
		</button>
	`);
	
	// Add button next to the field
	field.$wrapper.append(mapButton);
	
	// Add click handler
	mapButton.on('click', function() {
		openMapModal(fieldname, field);
	});
}

function addMapToChildTableField(frm, childTable, rowIndex, fieldname) {
	const grid = frm.get_field(childTable).grid;
	if (!grid) return;
	
	const row = grid.grid_rows[rowIndex];
	if (!row) return;
	
	const field = row.get_field(fieldname);
	if (!field || !field.$wrapper) return;
	
	// Remove existing map button if any
	field.$wrapper.find('.map-select-btn').remove();
	
	// Create map button
	const mapButton = $(`
		<button type="button" class="btn btn-xs btn-default map-select-btn" style="margin-left: 5px;">
			<i class="fa fa-map-marker"></i> Map
		</button>
	`);
	
	// Add button next to the field
	field.$wrapper.append(mapButton);
	
	// Add click handler
	mapButton.on('click', function() {
		openMapModal(fieldname, field, childTable, rowIndex);
	});
}

function openMapModal(fieldname, field, childTable = null, rowIndex = null) {
	currentMapField = { fieldname, field, childTable, rowIndex };
	
	// Create modal if it doesn't exist
	if (!document.getElementById('mapModal')) {
		createMapModal();
	}
	
	const modal = document.getElementById('mapModal');
	modal.style.display = 'block';
	
	// Load Google Maps
	loadGoogleMaps()
		.then(() => {
			console.log('Google Maps loaded successfully, initializing map...');
			initMap();
		})
		.catch((error) => {
			console.error('Failed to load Google Maps:', error);
			showMapError(error.message);
		});
}

function createMapModal() {
	const modalHTML = `
		<div id="mapModal" class="modal" style="display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; overflow: auto; background-color: rgba(0,0,0,0.4);">
			<div class="map-modal-content" style="background-color: #fefefe; margin: 5% auto; padding: 20px; border: 1px solid #888; width: 80%; max-width: 800px; border-radius: 8px; position: relative;">
				<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
					<h3 style="margin: 0; color: #333;">📍 Select Location</h3>
					<span class="close" onclick="closeMapModal()" style="color: #aaa; font-size: 28px; font-weight: bold; cursor: pointer;">&times;</span>
				</div>
				
				<div style="margin-bottom: 15px;">
					<input type="text" id="mapSearchInput" placeholder="Search for a location..." 
						   style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px;">
				</div>
				
				<div id="map" style="width: 100%; height: 400px; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 15px;"></div>
				
				<div id="coordinatesDisplay" style="background: #f8f9fa; padding: 10px; border-radius: 4px; margin-bottom: 15px; font-family: monospace; font-size: 14px;">
					No location selected. Click on the map or search for a location.
				</div>
				
				<div style="display: flex; justify-content: space-between; align-items: center;">
					<button type="button" onclick="enableManualEntry()" class="btn btn-default">
						<i class="fa fa-edit"></i> Manual Entry
					</button>
					<div>
						<button type="button" onclick="closeMapModal()" class="btn btn-secondary" style="margin-right: 10px;">
							Cancel
						</button>
						<button type="button" onclick="confirmLocation()" class="btn btn-primary">
							<i class="fa fa-check"></i> Confirm Location
						</button>
					</div>
				</div>
			</div>
		</div>
	`;
	
	document.body.insertAdjacentHTML('beforeend', modalHTML);
}

function loadGoogleMaps() {
	return new Promise((resolve, reject) => {
		// Check if Google Maps is already loaded
		if (typeof google !== 'undefined' && google.maps) {
			console.log('Google Maps already available');
			resolve();
			return;
		}
		
		// Get API key from server
		frappe.call({
			method: 'climoro_onboarding.climoro_onboarding.doctype.onboarding_form.onboarding_form.get_google_maps_api_key',
			callback: function(response) {
				if (response.message && response.message.success) {
					const apiKey = response.message.api_key;
					console.log('API key retrieved for direct loading');
					
					// Check if script already exists
					const existingScript = document.querySelector('script[src*="maps.googleapis.com"]');
					if (existingScript) {
						console.log('Google Maps script already exists, waiting for load...');
						// Wait for existing script to load
						const checkGoogleMaps = setInterval(() => {
							if (typeof google !== 'undefined' && google.maps) {
								clearInterval(checkGoogleMaps);
								resolve();
							}
						}, 100);
						
						setTimeout(() => {
							clearInterval(checkGoogleMaps);
							reject(new Error('Google Maps loading timeout'));
						}, 10000);
						return;
					}
					
					// Create callback function
					window.mapCallback = function() {
						console.log('Google Maps callback triggered');
						resolve();
					};
					
					// Create and load script
					const script = document.createElement('script');
					script.async = true;
					script.defer = true;
					script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places&callback=mapCallback`;
					script.onerror = () => reject(new Error('Failed to load Google Maps script'));
					
					document.head.appendChild(script);
					
				} else {
					reject(new Error('Failed to get API key: ' + (response.message?.message || 'Unknown error')));
				}
			},
			error: function(error) {
				reject(new Error('Error fetching API key: ' + error.message));
			}
		});
	});
}

function initMap() {
	console.log('initMap called');
	
	try {
		// Check if Google Maps is loaded
		if (typeof google === 'undefined' || !google.maps) {
			console.error('Google Maps API not loaded');
			return;
		}
		
		console.log('Google Maps API loaded successfully');
		
		// Initialize map centered on India
		const mapElement = document.getElementById('map');
		if (!mapElement) {
			console.error('Map element not found');
			return;
		}
		
		map = new google.maps.Map(mapElement, {
			center: { lat: 20.5937, lng: 78.9629 }, // India center
			zoom: 5,
			mapTypeControl: true,
			streetViewControl: true,
			fullscreenControl: true
		});
		
		console.log('Map initialized successfully');
		
		// Initialize Places search
		const searchInput = document.getElementById('mapSearchInput');
		if (searchInput && google.maps.places) {
			searchBox = new google.maps.places.SearchBox(searchInput);
			
			// Bias search results to current map viewport
			map.addListener('bounds_changed', () => {
				searchBox.setBounds(map.getBounds());
			});
			
			// Listen for place search results
			searchBox.addListener('places_changed', () => {
				const places = searchBox.getPlaces();
				if (places.length === 0) return;
				
				const place = places[0];
				if (!place.geometry || !place.geometry.location) return;
				
				// Center map on selected place
				map.setCenter(place.geometry.location);
				map.setZoom(15);
				
				// Add marker at selected place
				addMarkerAtLocation(place.geometry.location);
			});
			
			console.log('Places search initialized');
		} else {
			console.warn('Places API not available or search input not found');
		}
		
		// Add click listener to map
		map.addListener('click', (event) => {
			console.log('Map clicked at:', event.latLng.toString());
			addMarkerAtLocation(event.latLng);
		});
		
	} catch (error) {
		console.error('Error initializing map:', error);
	}
}

function addMarkerAtLocation(location) {
	// Remove existing marker
	if (selectedMarker) {
		selectedMarker.setMap(null);
	}
	
	// Add new marker
	selectedMarker = new google.maps.Marker({
		position: location,
		map: map,
		title: 'Selected Location'
	});
	
	// Store coordinates
	selectedCoordinates = {
		lat: location.lat(),
		lng: location.lng()
	};
	
	// Update coordinates display
	const coordinatesText = `${selectedCoordinates.lat.toFixed(6)}, ${selectedCoordinates.lng.toFixed(6)}`;
	document.getElementById('coordinatesDisplay').textContent = `Selected: ${coordinatesText}`;
}

function closeMapModal() {
	document.getElementById('mapModal').style.display = 'none';
}

function confirmLocation() {
	if (selectedCoordinates && currentMapField) {
		const coordinatesText = `${selectedCoordinates.lat.toFixed(6)}, ${selectedCoordinates.lng.toFixed(6)}`;
		
		if (currentMapField.childTable) {
			// Update child table field
			const frm = cur_frm;
			const grid = frm.get_field(currentMapField.childTable).grid;
			const row = grid.grid_rows[currentMapField.rowIndex];
			const field = row.get_field(currentMapField.fieldname);
			field.set_value(coordinatesText);
		} else {
			// Update main form field
			currentMapField.field.set_value(coordinatesText);
		}
		
		closeMapModal();
		
		// Show success message
		frappe.show_alert({
			message: 'Location selected successfully!',
			indicator: 'green'
		});
	} else {
		frappe.msgprint({
			title: 'No Location Selected',
			message: 'Please click on the map to select a location first.',
			indicator: 'red'
		});
	}
}

function enableManualEntry() {
	if (!currentMapField) return;
	
	if (currentMapField.childTable) {
		// Enable manual entry for child table field
		const frm = cur_frm;
		const grid = frm.get_field(currentMapField.childTable).grid;
		const row = grid.grid_rows[currentMapField.rowIndex];
		const field = row.get_field(currentMapField.fieldname);
		field.$input.removeAttr('readonly');
		field.$input.focus();
		field.$input.attr('placeholder', 'Enter coordinates manually (e.g., 28.6139, 77.2090)');
	} else {
		// Enable manual entry for main form field
		currentMapField.field.$input.removeAttr('readonly');
		currentMapField.field.$input.focus();
		currentMapField.field.$input.attr('placeholder', 'Enter coordinates manually (e.g., 28.6139, 77.2090)');
	}
	
	// Show help message
	frappe.show_alert({
		message: 'You can now enter coordinates manually. Format: latitude, longitude',
		indicator: 'blue'
	});
}

function showMapError(message) {
	const mapElement = document.getElementById('map');
	if (mapElement) {
		mapElement.innerHTML = '<div style="padding: 20px; text-align: center; color: #dc3545;">' +
			'<h4>📍 Map Loading Issue</h4>' +
			'<p>' + message + '</p>' +
			'<div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0;">' +
			'<strong>✅ Alternative: Manual Entry</strong><br>' +
			'You can enter coordinates directly in the GPS field below:<br>' +
			'<code style="background: white; padding: 2px 5px;">28.6139, 77.2090</code> (latitude, longitude)<br>' +
			'<small>💡 Get coordinates from Google Maps by right-clicking any location</small>' +
			'</div>' +
			'</div>';
	}
}

// Enhanced Table Display Functions
function enhanceTableDisplay(frm) {
	// Add custom CSS for enhanced table display
	addCustomCSS();
	
	// Enhance Units table
	if (frm.get_field('units')) {
		enhanceUnitsTable(frm);
	}
	
	// Enhance Assigned Users table
	if (frm.get_field('assigned_users')) {
		enhanceAssignedUsersTable(frm);
	}
}

function addCustomCSS() {
	// Add custom CSS if not already added
	if (!document.getElementById('enhanced-table-css')) {
		const css = `
			<style id="enhanced-table-css">
				.enhanced-unit-info {
					background: #f8f9fa;
					border: 1px solid #dee2e6;
					border-radius: 4px;
					padding: 8px;
					margin: 4px 0;
				}
				.enhanced-user-info {
					background: #e3f2fd;
					border: 1px solid #bbdefb;
					border-radius: 4px;
					padding: 8px;
					margin: 4px 0;
				}
				.unit-badge {
					display: inline-block;
					padding: 2px 6px;
					font-size: 10px;
					font-weight: 500;
					border-radius: 3px;
					margin-left: 8px;
				}
				.user-badge {
					display: inline-block;
					padding: 2px 6px;
					font-size: 10px;
					font-weight: 500;
					border-radius: 3px;
					margin-left: 8px;
				}
				.badge-office { background: #007bff; color: white; }
				.badge-warehouse { background: #ffc107; color: #212529; }
				.badge-factory { background: #dc3545; color: white; }
				.badge-franchise { background: #28a745; color: white; }
				.badge-manager { background: #007bff; color: white; }
				.badge-analyst { background: #17a2b8; color: white; }
				.info-icon {
					color: #6c757d;
					margin-right: 4px;
				}
				/* Desk form text visibility fixes (scoped) */
				.form-layout select,
				.form-layout .control-input,
				.form-layout .control-value,
				.form-layout .awesomplete input {
					color: inherit !important;
					opacity: 1 !important;
				}
				.form-layout select option { color: initial !important; }
				/* Dark theme-friendly text color fallback */
				[data-theme="dark"] .form-layout select,
				[data-theme="dark"] .form-layout .control-input,
				[data-theme="dark"] .form-layout .awesomplete input {
					color: #e5e7eb !important; /* tailwind zinc-200 */
				}
				/* Desk-only: neutralize any stray checkbox pseudo from other pages */
				.form-layout input[type="checkbox"]::after { content: none !important; }
				.form-layout input[type="checkbox"] {
					appearance: auto !important;
					-webkit-appearance: checkbox !important;
					-moz-appearance: checkbox !important;
					background-image: none !important;
					box-shadow: none !important;
				}
			</style>
		`;
		document.head.insertAdjacentHTML('beforeend', css);
	}
}

function enhanceUnitsTable(frm) {
	const unitsGrid = frm.get_field('units');
	if (!unitsGrid || !unitsGrid.grid) return;
	
	// Add custom formatter for units table
	unitsGrid.grid.grid_rows.forEach((row, index) => {
		try {
			// Get the row data
			const rowData = row.doc;
			if (!rowData) return;
			
			// Create enhanced display for the row
			const enhancedInfo = createUnitInfoDisplay(rowData);
			
			// Find the first editable field to add the enhanced info
			const firstField = row.get_field('name_of_unit') || row.get_field('type_of_unit');
			if (firstField && firstField.$wrapper) {
				// Add enhanced info below the field
				const infoDiv = document.createElement('div');
				infoDiv.className = 'enhanced-unit-info';
				infoDiv.innerHTML = enhancedInfo;
				firstField.$wrapper.after(infoDiv);
			}
		} catch (error) {
			console.log('Error enhancing unit row:', error);
		}
	});
}

function enhanceAssignedUsersTable(frm) {
	const usersGrid = frm.get_field('assigned_users');
	if (!usersGrid || !usersGrid.grid) return;
	
	// Add custom formatter for assigned users table
	usersGrid.grid.grid_rows.forEach((row, index) => {
		try {
			// Get the row data
			const rowData = row.doc;
			if (!rowData) return;
			
			// Create enhanced display for the row
			const enhancedInfo = createUserInfoDisplay(rowData);
			
			// Find the first editable field to add the enhanced info
			const firstField = row.get_field('first_name') || row.get_field('email');
			if (firstField && firstField.$wrapper) {
				// Add enhanced info below the field
				const infoDiv = document.createElement('div');
				infoDiv.className = 'enhanced-user-info';
				infoDiv.innerHTML = enhancedInfo;
				firstField.$wrapper.after(infoDiv);
			}
		} catch (error) {
			console.log('Error enhancing user row:', error);
		}
	});
}

function createUnitInfoDisplay(unitData) {
	const typeBadge = getUnitTypeBadge(unitData.type_of_unit);
	const sizeInfo = unitData.size_of_unit ? `${parseFloat(unitData.size_of_unit).toLocaleString()} sq ft` : '';
	const locationInfo = unitData.location_name || '';
	const addressInfo = unitData.address || '';
	const phoneInfo = unitData.phone_number || '';
	
	return `
		<div style="font-size: 12px;">
			<div style="margin-bottom: 4px;">
				<strong>${unitData.name_of_unit || 'Unit Name'}</strong>
								${typeBadge}
			</div>
			${sizeInfo ? `<div><i class="fa fa-arrows-alt info-icon"></i>${sizeInfo}</div>` : ''}
			${locationInfo ? `<div><i class="fa fa-map-marker info-icon"></i>${locationInfo}</div>` : ''}
			${addressInfo ? `<div><i class="fa fa-home info-icon"></i>${addressInfo}</div>` : ''}
			${phoneInfo ? `<div><i class="fa fa-phone info-icon"></i>${phoneInfo}</div>` : ''}
		</div>
	`;
}

function createUserInfoDisplay(userData) {
	const roleBadge = getUserRoleBadge(userData.user_role);
	const emailInfo = userData.email || '';
	const unitInfo = userData.assigned_unit || '';
	
	return `
		<div style="font-size: 12px;">
			<div style="margin-bottom: 4px;">
				<strong>${userData.first_name || 'User Name'}</strong>
								${roleBadge}
			</div>
			${emailInfo ? `<div><i class="fa fa-envelope info-icon"></i>${emailInfo}</div>` : ''}
			${unitInfo ? `<div><i class="fa fa-building info-icon"></i>${unitInfo}</div>` : ''}
		</div>
	`;
}

function getUnitTypeBadge(unitType) {
	if (!unitType) return '';
	const badgeClass = getUnitTypeBadgeClass(unitType);
	return `<span class="unit-badge ${badgeClass}">${unitType}</span>`;
}

function getUserRoleBadge(userRole) {
	if (!userRole) return '';
	const badgeClass = getUserRoleBadgeClass(userRole);
	return `<span class="user-badge ${badgeClass}">${userRole}</span>`;
}

function getUnitTypeBadgeClass(unitType) {
	const badgeClasses = {
		'Office': 'badge-office',
		'Warehouse': 'badge-warehouse',
		'Factory': 'badge-factory',
		'Franchise': 'badge-franchise'
	};
	return badgeClasses[unitType] || 'badge-secondary';
}

function getUserRoleBadgeClass(userRole) {
	switch(userRole) {
		case 'Unit Manager':
			return 'badge-primary';
		case 'Data Analyst':
			return 'badge-info';
		case 'Super Admin':
			return 'badge-success';
		default:
			return 'badge-secondary';
	}
}

// Helper function to show loading popup with spinner
function showProcessingPopup(title, subtitle, spinnerColor = '#007bff') {
	// Show loading popup
	const loadingDialog = frappe.show_alert({
		message: subtitle,
		indicator: 'blue'
	}, 0); // 0 means don't auto-hide
	
	// Show spinner overlay
	const spinnerOverlay = $(`
		<div class="processing-overlay" style="
			position: fixed;
			top: 0;
			left: 0;
			width: 100%;
			height: 100%;
			background: rgba(0, 0, 0, 0.5);
			z-index: 9999;
			display: flex;
			justify-content: center;
			align-items: center;
			flex-direction: column;
		">
			<div class="spinner" style="
				width: 50px;
				height: 50px;
				border: 5px solid #f3f3f3;
				border-top: 5px solid ${spinnerColor};
				border-radius: 50%;
				animation: spin 1s linear infinite;
				margin-bottom: 20px;
			"></div>
			<div style="
				color: white;
				font-size: 18px;
				font-weight: bold;
				text-align: center;
				max-width: 400px;
				line-height: 1.4;
			">
				${title}<br>
				<small style="font-size: 14px; opacity: 0.8;">
					${subtitle}<br>
					This may take a few moments.
				</small>
			</div>
		</div>
	`);
	
	// Add CSS animation if not already present
	if (!$('#spinner-css').length) {
		$('head').append(`
			<style id="spinner-css">
				@keyframes spin {
					0% { transform: rotate(0deg); }
					100% { transform: rotate(360deg); }
				}
			</style>
		`);
	}
	
	$('body').append(spinnerOverlay);
	
	// Return object with hide method
	return {
		hide: function() {
			loadingDialog.hide();
			spinnerOverlay.remove();
		}
	};
}

// Function to update Step 5 visibility based on Step 4 selections
function updateStep5Visibility(frm) {
	console.log('🌱 updateStep5Visibility called');
	
	// Get selected scopes from individual scope fields
	let selected_scopes = [];
	if (frm.doc.scopes_to_report_scope1) selected_scopes.push('Scope 1');
	if (frm.doc.scopes_to_report_scope2) selected_scopes.push('Scope 2');
	if (frm.doc.scopes_to_report_scope3) selected_scopes.push('Scope 3');
	if (frm.doc.scopes_to_report_reductions) selected_scopes.push('Reductions');
	
	console.log('🌱 Selected scopes:', selected_scopes);
	
	// Helper to safely toggle fields that may not exist in this site
	function safeToggle(fieldname, should_show, clear_when_hide, is_section=false) {
		const f = frm.get_field(fieldname);
		if (!f) {
			console.log('⚪ Skipping missing field:', fieldname);
			return;
		}
		frm.set_df_property(fieldname, 'hidden', should_show ? 0 : 1);
		if (!should_show && clear_when_hide && !is_section) {
			try { frm.set_value(fieldname, ''); } catch (e) { /* ignore */ }
		}
		console.log(should_show ? '🌱 Showing field:' : '🌱 Hiding field:', fieldname);
	}

	// Scope 1 fields
	const scope1Fields = [
		{ n: 'section_b_scope_1_targets', section: true },
		{ n: 'scope_1_target_type' },
		{ n: 'scope_1_intensity_reduction' },
		{ n: 'scope_1_reduction_percentage' },
		{ n: 'scope_1_target_year' },
		{ n: 'scope_1_mitigation_strategies' }
	];
	const s1 = selected_scopes.includes('Scope 1');
	scope1Fields.forEach(f => safeToggle(f.n, s1, true, !!f.section));
	
	// Scope 2 fields
	const scope2Fields = [
		{ n: 'section_c_scope_2_targets', section: true },
		{ n: 'scope_2_target_type' },
		{ n: 'scope_2_intensity_reduction' },
		{ n: 'scope_2_reduction_percentage' },
		{ n: 'scope_2_target_year' },
		{ n: 'scope_2_mitigation_strategies' }
	];
	const s2 = selected_scopes.includes('Scope 2');
	scope2Fields.forEach(f => safeToggle(f.n, s2, true, !!f.section));
	
	// Scope 3 fields
	const scope3Fields = [
		{ n: 'section_d_scope_3_targets', section: true },
		{ n: 'scope_3_categories_included' },
		{ n: 'scope_3_target_type' },
		{ n: 'scope_3_intensity_reduction' },
		{ n: 'scope_3_reduction_percentage' },
		{ n: 'scope_3_target_year' },
		{ n: 'scope_3_mitigation_strategies' }
	];
	const s3 = selected_scopes.includes('Scope 3');
	scope3Fields.forEach(f => safeToggle(f.n, s3, true, !!f.section));
	
	// Reductions fields
	const reductionFields = [
		{ n: 'section_e_reductions', section: true },
		{ n: 'reduction_target_type' },
		{ n: 'land_sector_removals' },
		{ n: 'residual_emissions_strategy' }
	];
	const sr = selected_scopes.includes('Reductions');
	reductionFields.forEach(f => safeToggle(f.n, sr, true, !!f.section));
	
	console.log('🌱 Step 5 visibility updated based on scopes:', selected_scopes);
}
