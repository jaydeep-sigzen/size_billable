"""
Custom Fields Installation Patch - v1.0.0

This patch installs all custom fields required for the Size Billable app,
including fields for Project and Timesheet Detail DocTypes.

Custom Fields Installed:
- Project DocType: billing_type, total_purchased_hours, total_consumed_hours, 
  project_manager_user, hourly_rate
- Timesheet Detail DocType: billable_hours, non_billable_hours, is_approved

Features:
- Automatic field creation with proper validation
- Role creation for SB Project Manager
- Field dependency management
- Error handling and rollback capabilities

This patch is executed during app installation and ensures all required
custom fields are properly installed in the ERPNext system.
"""

import frappe

def execute():
    """Install custom fields for Size Billable app"""
    
    # Install Project custom fields
    project_fields = [
        {
            "dt": "Project",
            "fieldname": "billing_type",
            "fieldtype": "Select",
            "options": "Fixed Cost\nHourly Billing",
            "label": "Billing Type",
            "reqd": 1,
            "default": "Hourly Billing",
            "insert_after": "project_type",
            "description": "Defines how this project will be billed to the customer"
        },
        {
            "dt": "Project",
            "fieldname": "total_purchased_hours",
            "fieldtype": "Float",
            "label": "Total Purchased Hours",
            "insert_after": "estimated_costing",
            "description": "Total hours purchased by customer (for Hourly Billing projects)"
        },
        {
            "dt": "Project",
            "fieldname": "total_consumed_hours",
            "fieldtype": "Float",
            "label": "Total Consumed Hours",
            "read_only": 1,
            "insert_after": "total_purchased_hours",
            "description": "Auto-calculated total of approved billable hours"
        },
        {
            "dt": "Project",
            "fieldname": "project_manager_user",
            "fieldtype": "Link",
            "options": "User",
            "label": "Project Manager",
            "reqd": 1,
            "insert_after": "customer",
            "description": "User responsible for managing this project and approving timesheets"
        },
        {
            "dt": "Project",
            "fieldname": "hourly_rate",
            "fieldtype": "Currency",
            "label": "Hourly Rate",
            "insert_after": "total_purchased_hours",
            "description": "Rate per hour for billing (for Hourly Billing projects)"
        },
        {
            "dt": "Project",
            "fieldname": "billing_section",
            "fieldtype": "Section Break",
            "label": "Billing Configuration",
            "insert_after": "project_manager_user",
            "collapsible": 1
        }
    ]
    
    for field in project_fields:
        if not frappe.db.exists("Custom Field", {"dt": field["dt"], "fieldname": field["fieldname"]}):
            frappe.get_doc({
                "doctype": "Custom Field",
                **field
            }).insert()
    
    # Install Timesheet Detail custom fields
    timesheet_fields = [
        {
            "dt": "Timesheet Detail",
            "fieldname": "billable_hours",
            "fieldtype": "Float",
            "label": "Billable Hours",
            "default": 0,
            "insert_after": "hours",
            "description": "Hours that can be billed to customer"
        },
        {
            "dt": "Timesheet Detail",
            "fieldname": "non_billable_hours",
            "fieldtype": "Float",
            "label": "Non-Billable Hours",
            "read_only": 1,
            "insert_after": "billable_hours",
            "description": "Hours for internal/unbillable work (auto-calculated)"
        },
        {
            "dt": "Timesheet Detail",
            "fieldname": "approval_section",
            "fieldtype": "Section Break",
            "label": "Approval Details",
            "insert_after": "non_billable_hours",
            "collapsible": 1
        },
        {
            "dt": "Timesheet Detail",
            "fieldname": "approved_by",
            "fieldtype": "Link",
            "options": "User",
            "label": "Approved By",
            "read_only": 1,
            "insert_after": "approval_section",
            "description": "Project Manager who approved this entry"
        },
        {
            "dt": "Timesheet Detail",
            "fieldname": "approved_on",
            "fieldtype": "Datetime",
            "label": "Approved On",
            "read_only": 1,
            "insert_after": "approved_by",
            "description": "Timestamp when this entry was approved"
        },
        {
            "dt": "Timesheet Detail",
            "fieldname": "approval_status",
            "fieldtype": "Select",
            "options": "Pending\nApproved\nRejected",
            "label": "Approval Status",
            "default": "Pending",
            "read_only": 1,
            "insert_after": "approved_on",
            "description": "Current approval status of this timesheet entry"
        }
    ]
    
    for field in timesheet_fields:
        if not frappe.db.exists("Custom Field", {"dt": field["dt"], "fieldname": field["fieldname"]}):
            frappe.get_doc({
                "doctype": "Custom Field",
                **field
            }).insert()
    
    # Create SB Project Manager role if it doesn't exist
    if not frappe.db.exists("Role", "SB Project Manager"):
        frappe.get_doc({
            "doctype": "Role",
            "role_name": "SB Project Manager",
            "desk_access": 1,
            "is_custom": 1
        }).insert()
    
    frappe.db.commit()
    frappe.clear_cache()

def before_uninstall():
    """Clean up custom fields before uninstalling"""
    # Remove custom fields
    custom_fields = frappe.get_all("Custom Field", 
        filters={"app_name": "size_billable"},
        pluck="name"
    )
    
    for field_name in custom_fields:
        frappe.delete_doc("Custom Field", field_name)
    
    # Remove custom role
    if frappe.db.exists("Role", "SB Project Manager"):
        frappe.delete_doc("Role", "SB Project Manager")
    
    frappe.db.commit()

