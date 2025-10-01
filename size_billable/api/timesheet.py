import frappe
from frappe import _
from frappe.utils import flt, now_datetime

def calculate_billable_hours(doc, method):
    """Calculate and validate billable hours for timesheet entries"""
    total_billable = 0
    total_non_billable = 0
    
    for row in doc.time_logs:
        # Initialize billable hours if not set
        if not row.billable_hours:
            row.billable_hours = 0
        
        # Calculate non-billable hours
        row.non_billable_hours = flt(row.hours) - flt(row.billable_hours)
        
        # Validate hour distribution
        if flt(row.billable_hours) < 0:
            frappe.throw(_("Billable hours cannot be negative"))
        
        if flt(row.non_billable_hours) < 0:
            frappe.throw(_("Non-billable hours cannot be negative"))
        
        total_billable += flt(row.billable_hours)
        total_non_billable += flt(row.non_billable_hours)
    
    # Update totals
    doc.total_billable_hours = total_billable
    doc.total_non_billable_hours = total_non_billable

def lock_timesheet_entries(doc, method):
    """Lock timesheet entries after submission - only manager can modify"""
    for row in doc.time_logs:
        # Reset approval fields for new submission
        row.approved_by = None
        row.approved_on = None
        row.approval_status = "Pending"
        row.save()
    
    # Update project consumed hours
    if doc.parent_project:
        update_project_consumed_hours(doc.parent_project)

def unlock_timesheet_entries(doc, method):
    """Unlock timesheet entries when timesheet is cancelled"""
    for row in doc.time_logs:
        row.approved_by = None
        row.approved_on = None
        row.approval_status = "Pending"
        row.save()
    
    # Recalculate project consumed hours
    if doc.parent_project:
        update_project_consumed_hours(doc.parent_project)

def update_project_consumed_hours(project_name):
    """Update total consumed hours for a project"""
    project = frappe.get_doc("Project", project_name)
    
    if project.billing_type == "Hourly Billing":
        total_consumed = frappe.db.sql("""
            SELECT SUM(tsd.billable_hours)
            FROM `tabTimesheet Detail` tsd
            INNER JOIN `tabTimesheet` ts ON tsd.parent = ts.name
            WHERE tsd.project = %s
            AND tsd.approved_by IS NOT NULL
            AND ts.status = 'Submitted'
        """, project_name)[0][0] or 0
        
        project.total_consumed_hours = flt(total_consumed, 2)
        project.save()

@frappe.whitelist()
def get_timesheet_approval_status(timesheet_name):
    """Get approval status for all entries in a timesheet"""
    timesheet = frappe.get_doc("Timesheet", timesheet_name)
    
    approval_summary = {
        "total_entries": len(timesheet.time_logs),
        "pending_entries": 0,
        "approved_entries": 0,
        "rejected_entries": 0,
        "entries": []
    }
    
    for row in timesheet.time_logs:
        status = {
            "name": row.name,
            "project": row.project,
            "task": row.task,
            "activity_type": row.activity_type,
            "hours": row.hours,
            "billable_hours": row.billable_hours,
            "non_billable_hours": row.non_billable_hours,
            "approval_status": row.approval_status,
            "approved_by": row.approved_by,
            "approved_on": row.approved_on
        }
        
        approval_summary["entries"].append(status)
        
        if row.approval_status == "Pending":
            approval_summary["pending_entries"] += 1
        elif row.approval_status == "Approved":
            approval_summary["approved_entries"] += 1
        elif row.approval_status == "Rejected":
            approval_summary["rejected_entries"] += 1
    
    return approval_summary

@frappe.whitelist()
def get_manager_timesheets(project_name=None, status="Pending"):
    """Get timesheets for manager approval"""
    user = frappe.session.user
    
    # Get projects managed by current user
    managed_projects = frappe.get_all("Project", 
        filters={"project_manager_user": user},
        pluck="name"
    )
    
    if not managed_projects:
        return []
    
    # Filter by specific project if provided
    if project_name and project_name in managed_projects:
        project_filter = project_name
    else:
        project_filter = ["in", managed_projects]
    
    # Get timesheet details
    timesheet_details = frappe.db.sql("""
        SELECT 
            tsd.name,
            tsd.parent as timesheet_name,
            tsd.project,
            tsd.task,
            tsd.activity_type,
            tsd.hours,
            tsd.billable_hours,
            tsd.non_billable_hours,
            tsd.approval_status,
            tsd.approved_by,
            tsd.approved_on,
            ts.employee,
            ts.employee_name,
            ts.start_date,
            ts.end_date,
            p.project_name,
            p.billing_type,
            p.hourly_rate
        FROM `tabTimesheet Detail` tsd
        INNER JOIN `tabTimesheet` ts ON tsd.parent = ts.name
        INNER JOIN `tabProject` p ON tsd.project = p.name
        WHERE tsd.project = %s
        AND ts.status = 'Submitted'
        AND tsd.approval_status = %s
        ORDER BY ts.start_date DESC, ts.employee_name
    """, (project_filter, status), as_dict=True)
    
    return timesheet_details

@frappe.whitelist()
def get_manager_projects():
    """Get projects managed by current user for filtering"""
    user = frappe.session.user
    
    projects = frappe.get_all("Project",
        filters={"project_manager_user": user, "status": ["!=", "Cancelled"]},
        fields=["name", "project_name"],
        order_by="project_name"
    )
    
    return projects