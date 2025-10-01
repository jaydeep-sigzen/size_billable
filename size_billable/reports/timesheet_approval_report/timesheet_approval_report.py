import frappe
from frappe import _
from frappe.utils import flt, format_datetime

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {
            "fieldname": "checkbox", 
            "label": "", 
            "fieldtype": "Check", 
            "width": 50,
            "editable": True
        },
        {
            "fieldname": "employee_name", 
            "label": "Employee", 
            "fieldtype": "Data", 
            "width": 120
        },
        {
            "fieldname": "project_name", 
            "label": "Project", 
            "fieldtype": "Data", 
            "width": 150
        },
        {
            "fieldname": "task", 
            "label": "Task", 
            "fieldtype": "Data", 
            "width": 120
        },
        {
            "fieldname": "activity_type", 
            "label": "Activity", 
            "fieldtype": "Data", 
            "width": 100
        },
        {
            "fieldname": "hours", 
            "label": "Total Hours", 
            "fieldtype": "Float", 
            "width": 80
        },
        {
            "fieldname": "billable_hours", 
            "label": "Billable Hours", 
            "fieldtype": "Float", 
            "width": 100,
            "editable": True
        },
        {
            "fieldname": "non_billable_hours", 
            "label": "Non-Billable Hours", 
            "fieldtype": "Float", 
            "width": 120
        },
        {
            "fieldname": "start_date", 
            "label": "Date", 
            "fieldtype": "Date", 
            "width": 100
        },
        {
            "fieldname": "approval_status", 
            "label": "Status", 
            "fieldtype": "Data", 
            "width": 80
        },
        {
            "fieldname": "approved_by", 
            "label": "Approved By", 
            "fieldtype": "Data", 
            "width": 120
        },
        {
            "fieldname": "approved_on", 
            "label": "Approved On", 
            "fieldtype": "Datetime", 
            "width": 120
        }
    ]

def get_data(filters):
    user = frappe.session.user
    
    # Get projects managed by current user
    managed_projects = frappe.get_all("Project", 
        filters={"project_manager_user": user},
        pluck="name"
    )
    
    if not managed_projects:
        return []
    
    # Build query
    query = """
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
        WHERE tsd.project IN %(projects)s
        AND ts.status = 'Submitted'
    """
    
    query_params = {"projects": managed_projects}
    
    # Apply filters
    if filters.get("project"):
        query += " AND tsd.project = %(project)s"
        query_params["project"] = filters.get("project")
    
    if filters.get("employee"):
        query += " AND ts.employee = %(employee)s"
        query_params["employee"] = filters.get("employee")
    
    if filters.get("status"):
        query += " AND tsd.approval_status = %(status)s"
        query_params["status"] = filters.get("status")
    
    if filters.get("from_date"):
        query += " AND ts.start_date >= %(from_date)s"
        query_params["from_date"] = filters.get("from_date")
    
    if filters.get("to_date"):
        query += " AND ts.start_date <= %(to_date)s"
        query_params["to_date"] = filters.get("to_date")
    
    query += " ORDER BY ts.start_date DESC, ts.employee_name"
    
    data = frappe.db.sql(query, query_params, as_dict=True)
    
    # Format data
    for row in data:
        row["checkbox"] = 0
        if row["approved_on"]:
            row["approved_on"] = format_datetime(row["approved_on"])
    
    return data

def get_filters():
    return [
        {
            "fieldname": "project",
            "label": "Project",
            "fieldtype": "Link",
            "options": "Project",
            "get_query": "size_billable.api.timesheet.get_manager_projects"
        },
        {
            "fieldname": "employee",
            "label": "Employee",
            "fieldtype": "Link",
            "options": "Employee"
        },
        {
            "fieldname": "status",
            "label": "Status",
            "fieldtype": "Select",
            "options": "Pending\nApproved\nRejected"
        },
        {
            "fieldname": "from_date",
            "label": "From Date",
            "fieldtype": "Date"
        },
        {
            "fieldname": "to_date",
            "label": "To Date",
            "fieldtype": "Date"
        }
    ]

