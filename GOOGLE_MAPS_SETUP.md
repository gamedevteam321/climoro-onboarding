# Google Maps Integration Setup Guide

This guide will help you set up Google Maps integration for the Climoro Onboarding app.

## 🚀 Features Added

1. **GPS Coordinates Field**: Added to Onboarding Form (Company Details section)
2. **Map Selection**: Interactive map modal for selecting locations
3. **Search Functionality**: Search for locations using Google Places API
4. **Manual Entry**: Option to enter coordinates manually
5. **Child Table Support**: Map selection for Company Units

## 📋 Prerequisites

1. Google Cloud Console account
2. Frappe/ERPNext installation
3. Internet connectivity for Google Maps API

## 🔧 Setup Instructions

### Step 1: Google Cloud Console Setup

1. **Go to Google Cloud Console**
   - Visit [https://console.cloud.google.com/](https://console.cloud.google.com/)
   - Sign in with your Google account

2. **Create or Select Project**
   - Create a new project or select an existing one
   - Note down your Project ID

3. **Enable Required APIs**
   - Go to "APIs & Services" > "Library"
   - Search and enable the following APIs:
     - **Maps JavaScript API**
     - **Places API**
     - **Geocoding API**

4. **Create API Key**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "API Key"
   - Copy the generated API key

5. **Restrict API Key (Recommended)**
   - Click on the created API key
   - Under "Application restrictions", select "HTTP referrers"
   - Add your domain(s) to the allowed referrers
   - Under "API restrictions", select "Restrict key"
   - Select the three APIs you enabled above

### Step 2: Configure API Key in Frappe

1. **Set API Key in Site Config**
   ```bash
   bench --site your-site.com set-config google_maps_api_key "YOUR_API_KEY_HERE"
   ```

2. **Verify Configuration**
   ```bash
   bench --site your-site.com get-config google_maps_api_key
   ```

### Step 3: Test the Integration

1. **Create/Edit Onboarding Form**
   - Go to the Onboarding Form doctype
   - You should see a "Select Location" button next to the GPS Coordinates field

2. **Test Map Functionality**
   - Click the "Select Location" button
   - The map modal should open
   - Try searching for a location
   - Click on the map to select coordinates
   - Confirm the selection

## 🎯 Usage Guide

### For Onboarding Form

1. **Company Details Section**
   - Fill in the company address
   - Click "Select Location" next to GPS Coordinates
   - Use the map to select the exact location
   - Or search for the address using the search box
   - Click "Confirm Location" to save coordinates

### For Company Units

1. **Adding Units**
   - In the Units & Users tab, add a new unit
   - Fill in the unit address
   - Click the "Map" button next to GPS Coordinates
   - Select location using the map
   - Confirm the selection

### Manual Entry

If you prefer to enter coordinates manually:
1. Click "Manual Entry" in the map modal
2. Enter coordinates in format: `latitude, longitude`
   - Example: `28.6139, 77.2090`
3. The field will be unlocked for manual input

## 🔍 Troubleshooting

### Map Not Loading

1. **Check API Key**
   ```bash
   bench --site your-site.com get-config google_maps_api_key
   ```

2. **Check Browser Console**
   - Open browser developer tools (F12)
   - Check for JavaScript errors
   - Look for Google Maps API errors

3. **Verify API Quotas**
   - Check Google Cloud Console for API usage
   - Ensure you haven't exceeded free tier limits

### Search Not Working

1. **Verify Places API**
   - Ensure Places API is enabled in Google Cloud Console
   - Check if API key has Places API access

### Coordinates Not Saving

1. **Check Field Permissions**
   - Ensure user has write permissions to the doctype
   - Check if the field is not read-only

## 📊 API Usage & Costs

### Free Tier Limits (Google Maps Platform)
- **Maps JavaScript API**: 28,500 map loads per month
- **Places API**: 1,000 requests per month
- **Geocoding API**: 2,500 requests per month

### Monitoring Usage
1. Go to Google Cloud Console
2. Navigate to "APIs & Services" > "Dashboard"
3. Monitor usage for each enabled API

## 🔒 Security Considerations

1. **API Key Restrictions**
   - Always restrict API keys to your domain
   - Use HTTP referrer restrictions
   - Enable API restrictions

2. **Rate Limiting**
   - Monitor API usage
   - Implement client-side caching if needed

3. **Error Handling**
   - The app includes fallback for manual entry
   - Graceful error handling for API failures

## 🆘 Support

If you encounter issues:

1. **Check Logs**
   ```bash
   bench --site your-site.com tail-logs
   ```

2. **Test Configuration**
   - Use the test function in the setup script
   - Check browser console for errors

3. **Common Issues**
   - API key not configured
   - APIs not enabled
   - Domain restrictions too strict
   - Network connectivity issues

## 📝 Additional Notes

- The map is centered on India by default
- Coordinates are stored in decimal degrees format
- The integration works with both main form and child table fields
- Manual entry is always available as a fallback
- The map modal is responsive and works on mobile devices

## 🔄 Updates

To update the Google Maps integration:

1. **Pull Latest Changes**
   ```bash
   bench --site your-site.com migrate
   ```

2. **Clear Cache**
   ```bash
   bench --site your-site.com clear-cache
   ```

3. **Restart Services**
   ```bash
   bench restart
   ```

---

**Note**: This integration requires an active internet connection to load Google Maps. For offline environments, consider using alternative mapping solutions or implementing local map tiles. 