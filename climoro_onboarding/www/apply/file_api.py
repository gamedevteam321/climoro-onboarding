import frappe
from frappe import _
import os


@frappe.whitelist(allow_guest=True)
def upload_file():
    """Handle file uploads for onboarding form documents"""
    try:
        # Get uploaded file from request
        uploaded_file = frappe.request.files.get('file')
        field_name = frappe.form_dict.get('field_name')
        
        # Validate required parameters
        if not uploaded_file:
            return {"success": False, "message": "No file uploaded"}
        
        if not field_name:
            return {"success": False, "message": "Field name is required"}
        
        # Validate file size (25MB limit)
        max_size = 25 * 1024 * 1024  # 25MB in bytes
        file_size = len(uploaded_file.read())
        uploaded_file.seek(0)  # Reset file pointer
        
        if file_size > max_size:
            return {"success": False, "message": "File size exceeds 25MB limit"}
        
        # Validate file type
        allowed_extensions = ['.pdf', '.docx', '.doc', '.xlsx', '.xls', '.csv', '.jpg', '.jpeg', '.png', '.gif', '.bmp']
        filename = uploaded_file.filename
        
        if not filename:
            return {"success": False, "message": "Invalid filename"}
        
        file_extension = '.' + filename.split('.')[-1].lower()
        
        if file_extension not in allowed_extensions:
            return {"success": False, "message": f"File type {file_extension} not supported. Allowed types: {', '.join(allowed_extensions)}"}
        
        # Create file document record in database using Frappe's proper file handling
        uploaded_file.seek(0)  # Reset file pointer
        file_content = uploaded_file.read()
        
        # Use Frappe's built-in file creation system
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": filename,
            "is_private": 1,
            "content": file_content
        })
        
        file_doc.insert(ignore_permissions=True)
        frappe.db.commit()
        
        # Use the file document's unique_url property which includes proper fid parameter
        # This ensures proper permission checking by Frappe
        site_url = frappe.utils.get_url()
        file_url = f"{site_url}{file_doc.unique_url}"
        
        return {
            "success": True,
            "message": "File uploaded successfully",
            "file_url": file_url,
            "file_name": filename,
            "file_size": file_size,
            "file_id": file_doc.name
        }
        
    except Exception as e:
        frappe.log_error(f"File upload error: {str(e)}", "Onboarding File Upload")
        return {"success": False, "message": f"Upload failed: {str(e)}"}


@frappe.whitelist(allow_guest=True)
def validate_file_upload(file_data, filename):
    """Validate file before upload"""
    try:
        # Validate filename
        if not filename or not filename.strip():
            return {"success": False, "message": "Filename is required"}
        
        # Validate file extension
        allowed_extensions = ['.pdf', '.docx', '.doc', '.xlsx', '.xls', '.csv', '.jpg', '.jpeg', '.png', '.gif', '.bmp']
        file_extension = '.' + filename.split('.')[-1].lower()
        
        if file_extension not in allowed_extensions:
            return {
                "success": False, 
                "message": f"File type {file_extension} not supported. Allowed types: {', '.join(allowed_extensions)}"
            }
        
        # Validate file size (if file_data is provided)
        if file_data:
            # Estimate file size from base64 data
            import base64
            try:
                # Remove data URL prefix if present
                if ',' in file_data:
                    file_data = file_data.split(',')[1]
                
                file_content = base64.b64decode(file_data)
                file_size = len(file_content)
                
                max_size = 25 * 1024 * 1024  # 25MB
                if file_size > max_size:
                    return {"success": False, "message": "File size exceeds 25MB limit"}
                
            except Exception as e:
                return {"success": False, "message": "Invalid file data format"}
        
        return {
            "success": True,
            "message": "File validation passed",
            "file_extension": file_extension,
            "file_size": file_size if 'file_size' in locals() else None
        }
        
    except Exception as e:
        frappe.log_error(f"File validation error: {str(e)}", "Onboarding File Validation")
        return {"success": False, "message": f"Validation failed: {str(e)}"}


@frappe.whitelist(allow_guest=True)
def delete_uploaded_file(file_id):
    """Delete uploaded file"""
    try:
        if not file_id:
            return {"success": False, "message": "File ID is required"}
        
        # Check if file exists
        if not frappe.db.exists("File", file_id):
            return {"success": False, "message": "File not found"}
        
        # Delete the file
        frappe.delete_doc("File", file_id, ignore_permissions=True)
        frappe.db.commit()
        
        return {
            "success": True,
            "message": "File deleted successfully"
        }
        
    except Exception as e:
        frappe.log_error(f"File deletion error: {str(e)}", "Onboarding File Deletion")
        return {"success": False, "message": f"Deletion failed: {str(e)}"}


@frappe.whitelist(allow_guest=True)
def get_file_info(file_id):
    """Get information about uploaded file"""
    try:
        if not file_id:
            return {"success": False, "message": "File ID is required"}
        
        # Check if file exists
        if not frappe.db.exists("File", file_id):
            return {"success": False, "message": "File not found"}
        
        file_doc = frappe.get_doc("File", file_id)
        
        return {
            "success": True,
            "file_info": {
                "name": file_doc.name,
                "file_name": file_doc.file_name,
                "file_url": file_doc.file_url,
                "file_size": file_doc.file_size,
                "creation": str(file_doc.creation),
                "modified": str(file_doc.modified)
            }
        }
        
    except Exception as e:
        frappe.log_error(f"File info error: {str(e)}", "Onboarding File Info")
        return {"success": False, "message": f"Failed to get file info: {str(e)}"} 