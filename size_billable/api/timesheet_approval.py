import frappe
from frappe import _
from frappe.utils import now, get_datetime
from frappe.model.document import Document

@frappe.whitelist()
def approve_entries(entries):
    """Approve selected timesheet entries"""
    user = frappe.session.user
    
    # Check if user has SB Project Manager role
    if "SB Project Manager" not in frappe.get_roles(user):
        frappe.throw(_("Access denied. Only SB Project Managers can approve entries."))
    
    if not entries:
        frappe.throw(_("No entries selected for approval."))
    
    approved_count = 0
    failed_entries = []
    
    for entry_id in entries:
        try:
            # Get timesheet detail
            tsd = frappe.get_doc("Timesheet Detail", entry_id)
            timesheet = frappe.get_doc("Timesheet", tsd.parent)
            
            # Verify user is the project manager for this project
            if not verify_project_manager_access(user, timesheet.project):
                failed_entries.append(f"Entry {entry_id}: Not authorized for project {timesheet.project}")
                continue
            
            # Update approval status
            tsd.approval_status = "Approved"
            tsd.approved_by = user
            tsd.approved_on = now()
            
            # Save timesheet detail
            tsd.save()
            
            # Update timesheet status if all entries are approved
            update_timesheet_status(timesheet)
            
            # Recalculate project hours
            recalculate_project_hours(timesheet.project)
            
            approved_count += 1
            
        except Exception as e:
            failed_entries.append(f"Entry {entry_id}: {str(e)}")
            frappe.log_error(f"Error approving entry {entry_id}: {str(e)}")
    
    # Return result
    result = {
        "approved_count": approved_count,
        "failed_entries": failed_entries
    }
    
    if failed_entries:
        frappe.msgprint(_("Some entries could not be approved. Check the console for details."))
    
    return result

@frappe.whitelist()
def reject_entries(entries):
    """Reject selected timesheet entries"""
    user = frappe.session.user
    
    # Check if user has SB Project Manager role
    if "SB Project Manager" not in frappe.get_roles(user):
        frappe.throw(_("Access denied. Only SB Project Managers can reject entries."))
    
    if not entries:
        frappe.throw(_("No entries selected for rejection."))
    
    rejected_count = 0
    failed_entries = []
    
    for entry_id in entries:
        try:
            # Get timesheet detail
            tsd = frappe.get_doc("Timesheet Detail", entry_id)
            timesheet = frappe.get_doc("Timesheet", tsd.parent)
            
            # Verify user is the project manager for this project
            if not verify_project_manager_access(user, timesheet.project):
                failed_entries.append(f"Entry {entry_id}: Not authorized for project {timesheet.project}")
                continue
            
            # Update approval status
            tsd.approval_status = "Rejected"
            tsd.approved_by = user
            tsd.approved_on = now()
            
            # Save timesheet detail
            tsd.save()
            
            # Update timesheet status
            update_timesheet_status(timesheet)
            
            # Recalculate project hours
            recalculate_project_hours(timesheet.project)
            
            rejected_count += 1
            
        except Exception as e:
            failed_entries.append(f"Entry {entry_id}: {str(e)}")
            frappe.log_error(f"Error rejecting entry {entry_id}: {str(e)}")
    
    # Return result
    result = {
        "rejected_count": rejected_count,
        "failed_entries": failed_entries
    }
    
    if failed_entries:
        frappe.msgprint(_("Some entries could not be rejected. Check the console for details."))
    
    return result

@frappe.whitelist()
def save_hour_changes(entries):
    """Save hour adjustments without approval"""
    user = frappe.session.user
    
    # Check if user has SB Project Manager role
    if "SB Project Manager" not in frappe.get_roles(user):
        frappe.throw(_("Access denied. Only SB Project Managers can modify hours."))
    
    if not entries:
        frappe.throw(_("No changes to save."))
    
    saved_count = 0
    failed_entries = []
    
    for entry_data in entries:
        try:
            entry_id = entry_data.get("timesheet_detail_id")
            billable_hours = flt(entry_data.get("billable_hours", 0))
            non_billable_hours = flt(entry_data.get("non_billable_hours", 0))
            
            # Get timesheet detail
            tsd = frappe.get_doc("Timesheet Detail", entry_id)
            timesheet = frappe.get_doc("Timesheet", tsd.parent)
            
            # Verify user is the project manager for this project
            if not verify_project_manager_access(user, timesheet.project):
                failed_entries.append(f"Entry {entry_id}: Not authorized for project {timesheet.project}")
                continue
            
            # Validate hour totals
            total_hours = billable_hours + non_billable_hours
            if abs(total_hours - tsd.hours) > 0.01:  # Allow small floating point differences
                failed_entries.append(f"Entry {entry_id}: Total hours mismatch. Expected {tsd.hours}, got {total_hours}")
                continue
            
            # Update hours
            tsd.billable_hours = billable_hours
            tsd.non_billable_hours = non_billable_hours
            
            # If not already approved, mark as pending
            if tsd.approval_status not in ["Approved", "Rejected"]:
                tsd.approval_status = "Pending"
            
            # Save timesheet detail
            tsd.save()
            
            # Recalculate project hours
            recalculate_project_hours(timesheet.project)
            
            saved_count += 1
            
        except Exception as e:
            failed_entries.append(f"Entry {entry_id}: {str(e)}")
            frappe.log_error(f"Error saving hour changes for entry {entry_id}: {str(e)}")
    
    # Return result
    result = {
        "saved_count": saved_count,
        "failed_entries": failed_entries
    }
    
    if failed_entries:
        frappe.msgprint(_("Some changes could not be saved. Check the console for details."))
    
    return result

def verify_project_manager_access(user, project_name):
    """Verify that user is the project manager for the given project"""
    project_manager = frappe.get_value("Project", project_name, "project_manager_user")
    return project_manager == user

def update_timesheet_status(timesheet):
    """Update timesheet status based on approval status of all entries"""
    # Get all timesheet details
    timesheet_details = frappe.get_all("Timesheet Detail",
        filters={"parent": timesheet.name},
        fields=["approval_status"]
    )
    
    if not timesheet_details:
        return
    
    # Check if all entries are approved
    all_approved = all(detail.approval_status == "Approved" for detail in timesheet_details)
    
    # Check if any entries are rejected
    any_rejected = any(detail.approval_status == "Rejected" for detail in timesheet_details)
    
    # Update timesheet status
    if all_approved:
        timesheet.status = "Approved"
    elif any_rejected:
        timesheet.status = "Rejected"
    else:
        timesheet.status = "Pending"
    
    timesheet.save()

def recalculate_project_hours(project_name):
    """Recalculate project's total consumed hours"""
    try:
        # Get all approved timesheet entries for this project
        approved_hours = frappe.db.sql("""
            SELECT SUM(tsd.billable_hours) as total_billable_hours
            FROM `tabTimesheet Detail` tsd
            INNER JOIN `tabTimesheet` ts ON tsd.parent = ts.name
            WHERE ts.project = %s AND tsd.approval_status = 'Approved'
        """, (project_name,), as_dict=True)
        
        total_billable_hours = flt(approved_hours[0].total_billable_hours) if approved_hours else 0
        
        # Update project's total consumed hours
        frappe.db.set_value("Project", project_name, "total_consumed_hours", total_billable_hours)
        
        # Commit the changes
        frappe.db.commit()
        
    except Exception as e:
        frappe.log_error(f"Error recalculating project hours for {project_name}: {str(e)}")

@frappe.whitelist()
def get_project_summary(project_name):
    """Get project summary for the approval report"""
    user = frappe.session.user
    
    # Check if user has SB Project Manager role
    if "SB Project Manager" not in frappe.get_roles(user):
        frappe.throw(_("Access denied. Only SB Project Managers can access this data."))
    
    # Verify user is the project manager for this project
    if not verify_project_manager_access(user, project_name):
        frappe.throw(_("Access denied. You are not the project manager for this project."))
    
    # Get project details
    project = frappe.get_doc("Project", project_name)
    
    # Get timesheet summary
    timesheet_summary = frappe.db.sql("""
        SELECT 
            COUNT(*) as total_entries,
            SUM(CASE WHEN tsd.approval_status = 'Pending' THEN 1 ELSE 0 END) as pending_entries,
            SUM(CASE WHEN tsd.approval_status = 'Approved' THEN 1 ELSE 0 END) as approved_entries,
            SUM(CASE WHEN tsd.approval_status = 'Rejected' THEN 1 ELSE 0 END) as rejected_entries,
            SUM(tsd.hours) as total_hours,
            SUM(tsd.billable_hours) as total_billable_hours,
            SUM(tsd.non_billable_hours) as total_non_billable_hours
        FROM `tabTimesheet Detail` tsd
        INNER JOIN `tabTimesheet` ts ON tsd.parent = ts.name
        WHERE ts.project = %s
    """, (project_name,), as_dict=True)
    
    summary = timesheet_summary[0] if timesheet_summary else {}
    
    return {
        "project_name": project.project_name,
        "billing_type": project.billing_type,
        "total_purchased_hours": project.total_purchased_hours,
        "total_consumed_hours": project.total_consumed_hours,
        "remaining_hours": flt(project.total_purchased_hours) - flt(project.total_consumed_hours),
        "timesheet_summary": summary
    }
