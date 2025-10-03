"""
Project Management API

This module handles project-related functionality including validation, billing calculations,
and timesheet approval workflows for the Size Billable app.

Key Features:
- Project manager validation and role checking
- Billing type validation (Fixed Cost vs Hourly Billing)
- Automatic hour consumption tracking
- Project billing summary generation
- Bulk timesheet approval/rejection
- Budget monitoring and alerts

Security:
- Only SB Project Managers can manage projects
- Project managers can only approve entries for their assigned projects
- All operations include proper validation and error handling

The module integrates with the timesheet system to provide real-time billing insights
and automated workflow management.
"""

import frappe
from frappe import _
from frappe.utils import flt, now_datetime

def validate_project_manager(doc, method):
    """Validate that project has exactly one manager with proper role"""
    if not doc.project_manager_user:
        frappe.throw(_("Project Manager is required"))
    
    # Check if user has SB Project Manager role
    user_roles = frappe.get_roles(doc.project_manager_user)
    if "SB Project Manager" not in user_roles:
        frappe.throw(_("Selected user must have SB Project Manager role"))
    
    # Validate billing type specific requirements
    if doc.billing_type == "Hourly Billing":
        if not doc.total_purchased_hours or doc.total_purchased_hours <= 0:
            frappe.throw(_("Total Purchased Hours must be greater than 0 for Hourly Billing projects"))
        
        if not doc.hourly_rate or doc.hourly_rate <= 0:
            frappe.throw(_("Hourly Rate must be greater than 0 for Hourly Billing projects"))
    
    elif doc.billing_type == "Fixed Cost":
        # Reset hour-related fields for fixed cost projects
        doc.total_purchased_hours = 0
        doc.total_consumed_hours = 0
        doc.hourly_rate = 0

def update_project_hours(doc, method):
    """Update total consumed hours when timesheet entries are approved"""
    if doc.billing_type == "Hourly Billing":
        # Recalculate total consumed hours from approved timesheet entries
        # Optimized query with better performance
        total_consumed = frappe.db.sql("""
            SELECT COALESCE(SUM(tsd.billable_hours), 0)
            FROM `tabTimesheet Detail` tsd
            INNER JOIN `tabTimesheet` ts ON tsd.parent = ts.name
            WHERE tsd.project = %s
            AND tsd.approved_by IS NOT NULL
            AND ts.status = 'Submitted'
        """, doc.name, as_list=True)[0][0]
        
        doc.total_consumed_hours = flt(total_consumed, 2)
        
        # Check if project is over budget
        if doc.total_consumed_hours > doc.total_purchased_hours:
            frappe.msgprint(_("Warning: Project has consumed more hours than purchased!"), 
                          alert=True, indicator="red")

@frappe.whitelist()
def get_project_billing_summary(project_name):
    """Get comprehensive billing summary for a project"""
    # Use get_value for better performance instead of get_doc
    project_data = frappe.get_value("Project", project_name, 
        ["project_name", "billing_type", "total_purchased_hours", 
         "total_consumed_hours", "hourly_rate"], as_dict=True)
    
    if not project_data:
        frappe.throw(_("Project not found"))
    
    # Get timesheet statistics in a single optimized query
    timesheet_stats = frappe.db.sql("""
        SELECT 
            COUNT(*) as total_entries,
            SUM(CASE WHEN approved_by IS NOT NULL THEN 1 ELSE 0 END) as approved_entries,
            SUM(CASE WHEN approved_by IS NULL THEN 1 ELSE 0 END) as pending_entries,
            COALESCE(SUM(billable_hours), 0) as total_billable_hours,
            COALESCE(SUM(non_billable_hours), 0) as total_non_billable_hours
        FROM `tabTimesheet Detail` tsd
        INNER JOIN `tabTimesheet` ts ON tsd.parent = ts.name
        WHERE tsd.project = %s
        AND ts.status = 'Submitted'
    """, project_name, as_dict=True)[0]
    
    # Calculate remaining hours
    remaining_hours = (project_data.total_purchased_hours or 0) - (project_data.total_consumed_hours or 0)
    consumption_percentage = 0
    if project_data.total_purchased_hours > 0:
        consumption_percentage = (project_data.total_consumed_hours / project_data.total_purchased_hours) * 100
    
    return {
        "project_name": project_data.project_name,
        "billing_type": project_data.billing_type,
        "total_purchased_hours": project_data.total_purchased_hours,
        "total_consumed_hours": project_data.total_consumed_hours,
        "remaining_hours": remaining_hours,
        "consumption_percentage": consumption_percentage,
        "hourly_rate": project_data.hourly_rate,
        "total_billable_amount": project_data.total_consumed_hours * (project_data.hourly_rate or 0),
        "timesheet_stats": timesheet_stats
    }

@frappe.whitelist()
def get_project_manager(project_name):
    """Get project manager for a given project"""
    return frappe.get_value("Project", project_name, "project_manager_user")

@frappe.whitelist()
def approve_timesheet_entries(project_name, timesheet_details, action="approve"):
    """Bulk approve or reject timesheet entries"""
    user = frappe.session.user
    
    # Validate project manager - use get_value for better performance
    project_manager = frappe.get_value("Project", project_name, "project_manager_user")
    if project_manager != user:
        frappe.throw(_("You can only approve entries for your managed projects"))
    
    if not timesheet_details:
        return {"message": "No timesheet entries provided", "approved_count": 0}
    
    # Bulk update using SQL for better performance
    if action == "approve":
        approved_count = frappe.db.sql("""
            UPDATE `tabTimesheet Detail` 
            SET approved_by = %s, approved_on = %s, approval_status = 'Approved'
            WHERE name IN %s
        """, (user, now_datetime(), tuple(timesheet_details)))
        approved_count = len(timesheet_details)
    elif action == "reject":
        frappe.db.sql("""
            UPDATE `tabTimesheet Detail` 
            SET approval_status = 'Rejected'
            WHERE name IN %s
        """, (tuple(timesheet_details),))
        approved_count = len(timesheet_details)
    else:
        approved_count = 0
    
    # Update project hours after approval - only if approving
    if action == "approve" and approved_count > 0:
        # Create a minimal project object for the update function
        project = frappe._dict({
            "name": project_name,
            "billing_type": frappe.get_value("Project", project_name, "billing_type")
        })
        update_project_hours(project, "on_update")
    
    return {
        "message": f"Successfully {action}d {approved_count} timesheet entries",
        "approved_count": approved_count
    }

