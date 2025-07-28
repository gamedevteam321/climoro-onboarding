// Copyright (c) 2024, Climoro Onboarding and contributors
// For license information, please see license.txt

// Google Maps Variables
let map;
let selectedMarker;
let selectedCoordinates = null;
let searchBox;
let currentMapField = null;

frappe.ui.form.on('Onboarding Form', {
	refresh: function(frm) {
		// Add map functionality to GPS coordinates field
		addMapToField(frm, 'gps_coordinates');
		
		// Add map functionality to company units
		if (frm.doc.units && frm.doc.units.length > 0) {
			frm.doc.units.forEach((unit, index) => {
				addMapToChildTableField(frm, 'units', index, 'gps_coordinates');
			});
		}
	},
	
	units_add: function(frm, cdt, cdn) {
		// Add map functionality when new unit is added
		const row = locals[cdt][cdn];
		if (row) {
			setTimeout(() => {
				const index = frm.doc.units.findIndex(unit => unit.name === row.name);
				if (index !== -1) {
					addMapToChildTableField(frm, 'units', index, 'gps_coordinates');
				}
			}, 100);
		}
	}
});

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