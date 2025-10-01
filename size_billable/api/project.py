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
        total_consumed = frappe.db.sql("""
            SELECT SUM(tsd.billable_hours)
            FROM `tabTimesheet Detail` tsd
            INNER JOIN `tabTimesheet` ts ON tsd.parent = ts.name
            WHERE tsd.project = %s
            AND tsd.approved_by IS NOT NULL
            AND ts.status = 'Submitted'
        """, doc.name)[0][0] or 0
        
        doc.total_consumed_hours = flt(total_consumed, 2)
        
        # Check if project is over budget
        if doc.total_consumed_hours > doc.total_purchased_hours:
            frappe.msgprint(_("Warning: Project has consumed more hours than purchased!"), 
                          alert=True, indicator="red")

@frappe.whitelist()
def get_project_billing_summary(project_name):
    """Get comprehensive billing summary for a project"""
    project = frappe.get_doc("Project", project_name)
    
    # Get timesheet statistics
    timesheet_stats = frappe.db.sql("""
        SELECT 
            COUNT(*) as total_entries,
            SUM(CASE WHEN approved_by IS NOT NULL THEN 1 ELSE 0 END) as approved_entries,
            SUM(CASE WHEN approved_by IS NULL THEN 1 ELSE 0 END) as pending_entries,
            SUM(billable_hours) as total_billable_hours,
            SUM(non_billable_hours) as total_non_billable_hours
        FROM `tabTimesheet Detail` tsd
        INNER JOIN `tabTimesheet` ts ON tsd.parent = ts.name
        WHERE tsd.project = %s
        AND ts.status = 'Submitted'
    """, project_name, as_dict=True)[0]
    
    # Calculate remaining hours
    remaining_hours = (project.total_purchased_hours or 0) - (project.total_consumed_hours or 0)
    consumption_percentage = 0
    if project.total_purchased_hours > 0:
        consumption_percentage = (project.total_consumed_hours / project.total_purchased_hours) * 100
    
    return {
        "project_name": project.project_name,
        "billing_type": project.billing_type,
        "total_purchased_hours": project.total_purchased_hours,
        "total_consumed_hours": project.total_consumed_hours,
        "remaining_hours": remaining_hours,
        "consumption_percentage": consumption_percentage,
        "hourly_rate": project.hourly_rate,
        "total_billable_amount": project.total_consumed_hours * (project.hourly_rate or 0),
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
    
    # Validate project manager
    project = frappe.get_doc("Project", project_name)
    if project.project_manager_user != user:
        frappe.throw(_("You can only approve entries for your managed projects"))
    
    approved_count = 0
    for detail_name in timesheet_details:
        try:
            detail = frappe.get_doc("Timesheet Detail", detail_name)
            
            if action == "approve":
                detail.approved_by = user
                detail.approved_on = now_datetime()
                detail.approval_status = "Approved"
                approved_count += 1
            elif action == "reject":
                detail.approval_status = "Rejected"
            
            detail.save()
            
        except Exception as e:
            frappe.log_error(f"Error processing timesheet detail {detail_name}: {str(e)}")
    
    # Update project hours after approval
    if action == "approve" and approved_count > 0:
        update_project_hours(project, "on_update")
    
    return {
        "message": f"Successfully {action}d {approved_count} timesheet entries",
        "approved_count": approved_count
    }

