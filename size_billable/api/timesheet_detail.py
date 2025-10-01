import frappe
from frappe import _
from frappe.utils import flt

def validate_hour_distribution(doc, method):
    """Validate that billable + non-billable = total hours"""
    if doc.billable_hours is not None and doc.non_billable_hours is not None:
        total = flt(doc.billable_hours) + flt(doc.non_billable_hours)
        if abs(total - flt(doc.hours)) > 0.01:  # Allow small floating point differences
            frappe.throw(_("Billable Hours + Non-Billable Hours must equal Total Hours"))
    
    # Ensure non-billable hours are calculated correctly
    if doc.billable_hours is not None:
        doc.non_billable_hours = flt(doc.hours) - flt(doc.billable_hours)

def update_approval_status(doc, method):
    """Update approval status based on approval fields"""
    if doc.approved_by:
        doc.approval_status = "Approved"
    elif doc.approval_status == "Pending":
        # Keep as pending if not explicitly set
        pass
    else:
        doc.approval_status = "Pending"

@frappe.whitelist()
def update_timesheet_hours(timesheet_detail, billable_hours, non_billable_hours):
    """Update hours for a timesheet detail entry"""
    user = frappe.session.user
    doc = frappe.get_doc("Timesheet Detail", timesheet_detail)
    
    # Validate project manager
    project = frappe.get_doc("Project", doc.project)
    if project.project_manager_user != user:
        frappe.throw(_("You can only modify entries for your managed projects"))
    
    # Validate hour distribution
    total = flt(billable_hours) + flt(non_billable_hours)
    if abs(total - flt(doc.hours)) > 0.01:
        frappe.throw(_("Billable Hours + Non-Billable Hours must equal Total Hours"))
    
    doc.billable_hours = flt(billable_hours)
    doc.non_billable_hours = flt(non_billable_hours)
    doc.save()
    
    return "Hours updated successfully"

@frappe.whitelist()
def bulk_update_hours(timesheet_details, billable_hours_dict):
    """Bulk update hours for multiple timesheet details"""
    user = frappe.session.user
    updated_count = 0
    
    for detail_name, hours_data in billable_hours_dict.items():
        try:
            doc = frappe.get_doc("Timesheet Detail", detail_name)
            
            # Validate project manager
            project = frappe.get_doc("Project", doc.project)
            if project.project_manager_user != user:
                continue
            
            # Validate hour distribution
            total = flt(hours_data.get("billable_hours", 0)) + flt(hours_data.get("non_billable_hours", 0))
            if abs(total - flt(doc.hours)) > 0.01:
                continue
            
            doc.billable_hours = flt(hours_data.get("billable_hours", 0))
            doc.non_billable_hours = flt(hours_data.get("non_billable_hours", 0))
            doc.save()
            
            updated_count += 1
            
        except Exception as e:
            frappe.log_error(f"Error updating timesheet detail {detail_name}: {str(e)}")
    
    return {
        "message": f"Successfully updated {updated_count} timesheet entries",
        "updated_count": updated_count
    }