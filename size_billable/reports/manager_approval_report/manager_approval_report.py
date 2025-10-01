import frappe
from frappe import _
from frappe.utils import flt, getdate, today, add_days

def execute(filters=None):
    """Generate Manager Approval Report for SB Project Managers"""
    
    # Get current user
    user = frappe.session.user
    
    # Check if user has SB Project Manager role
    if "SB Project Manager" not in frappe.get_roles(user):
        frappe.throw(_("Access denied. Only SB Project Managers can access this report."))
    
    # Get projects managed by current user
    managed_projects = get_managed_projects(user)
    if not managed_projects:
        return get_empty_message()
    
    # Build filters
    conditions = get_conditions(filters, managed_projects)
    
    # Get timesheet entries
    data = get_timesheet_entries(conditions, filters)
    
    # Get columns
    columns = get_columns()
    
    return columns, data

def get_managed_projects(user):
    """Get projects managed by current user"""
    projects = frappe.get_all("Project",
        filters={"project_manager_user": user, "status": ["!=", "Cancelled"]},
        pluck="name"
    )
    return projects

def get_conditions(filters, managed_projects):
    """Build SQL conditions based on filters"""
    conditions = []
    
    # Only show projects managed by current user
    if managed_projects:
        project_filter = "', '".join(managed_projects)
        conditions.append(f"ts.project IN ('{project_filter}')")
    
    # Filter by project
    if filters.get("project"):
        conditions.append(f"ts.project = '{filters['project']}'")
    
    # Filter by employee
    if filters.get("employee"):
        conditions.append(f"ts.employee = '{filters['employee']}'")
    
    # Filter by date range
    if filters.get("from_date"):
        conditions.append(f"tsd.from_time >= '{filters['from_date']}'")
    if filters.get("to_date"):
        conditions.append(f"tsd.from_time <= '{filters['to_date']}'")
    
    # Filter by approval status
    if filters.get("approval_status"):
        if filters["approval_status"] == "Pending":
            conditions.append("tsd.approval_status = 'Pending'")
        elif filters["approval_status"] == "Approved":
            conditions.append("tsd.approval_status = 'Approved'")
        elif filters["approval_status"] == "Rejected":
            conditions.append("tsd.approval_status = 'Rejected'")
    
    return " AND ".join(conditions) if conditions else "1=1"

def get_timesheet_entries(conditions, filters):
    """Get timesheet entries based on conditions"""
    
    query = f"""
        SELECT 
            tsd.name as timesheet_detail_id,
            ts.name as timesheet_id,
            ts.employee,
            emp.employee_name,
            ts.project,
            p.project_name,
            tsd.task,
            t.subject as task_name,
            tsd.activity_type,
            tsd.description,
            tsd.hours as total_hours,
            tsd.billable_hours,
            tsd.non_billable_hours,
            tsd.approval_status,
            tsd.approved_by,
            tsd.approved_on,
            tsd.from_time,
            tsd.to_time,
            ts.status as timesheet_status,
            ts.creation as timesheet_created
        FROM `tabTimesheet Detail` tsd
        INNER JOIN `tabTimesheet` ts ON tsd.parent = ts.name
        INNER JOIN `tabEmployee` emp ON ts.employee = emp.name
        INNER JOIN `tabProject` p ON ts.project = p.name
        LEFT JOIN `tabTask` t ON tsd.task = t.name
        WHERE {conditions}
        ORDER BY tsd.from_time DESC, ts.employee, ts.project
    """
    
    data = frappe.db.sql(query, as_dict=True)
    
    # Add additional calculated fields
    for row in data:
        row['can_edit'] = row['approval_status'] in ['Pending', 'Rejected']
        row['is_approved'] = row['approval_status'] == 'Approved'
        row['is_pending'] = row['approval_status'] == 'Pending'
        row['is_rejected'] = row['approval_status'] == 'Rejected'
        
        # Format dates
        if row['from_time']:
            row['date'] = getdate(row['from_time']).strftime('%Y-%m-%d')
        if row['approved_on']:
            row['approved_date'] = getdate(row['approved_on']).strftime('%Y-%m-%d %H:%M')
    
    return data

def get_columns():
    """Define report columns"""
    columns = [
        {
            "fieldname": "select",
            "label": _("Select"),
            "fieldtype": "Check",
            "width": 50,
            "sortable": False
        },
        {
            "fieldname": "employee_name",
            "label": _("Employee"),
            "fieldtype": "Data",
            "width": 120,
            "sortable": True
        },
        {
            "fieldname": "project_name",
            "label": _("Project"),
            "fieldtype": "Data",
            "width": 150,
            "sortable": True
        },
        {
            "fieldname": "task_name",
            "label": _("Task"),
            "fieldtype": "Data",
            "width": 150,
            "sortable": True
        },
        {
            "fieldname": "activity_type",
            "label": _("Activity Type"),
            "fieldtype": "Data",
            "width": 120,
            "sortable": True
        },
        {
            "fieldname": "description",
            "label": _("Description"),
            "fieldtype": "Text",
            "width": 200,
            "sortable": False
        },
        {
            "fieldname": "date",
            "label": _("Date"),
            "fieldtype": "Date",
            "width": 100,
            "sortable": True
        },
        {
            "fieldname": "total_hours",
            "label": _("Total Hours"),
            "fieldtype": "Float",
            "width": 100,
            "sortable": True,
            "precision": 2
        },
        {
            "fieldname": "billable_hours",
            "label": _("Billable Hours"),
            "fieldtype": "Float",
            "width": 120,
            "sortable": True,
            "precision": 2,
            "editable": True
        },
        {
            "fieldname": "non_billable_hours",
            "label": _("Non-Billable Hours"),
            "fieldtype": "Float",
            "width": 140,
            "sortable": True,
            "precision": 2,
            "editable": True
        },
        {
            "fieldname": "approval_status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 100,
            "sortable": True
        },
        {
            "fieldname": "approved_by",
            "label": _("Approved By"),
            "fieldtype": "Data",
            "width": 120,
            "sortable": True
        },
        {
            "fieldname": "approved_date",
            "label": _("Approved On"),
            "fieldtype": "Data",
            "width": 150,
            "sortable": True
        }
    ]
    
    return columns

def get_empty_message():
    """Return empty message when no data"""
    columns = get_columns()
    data = [{
        "employee_name": "No timesheet entries found",
        "project_name": "",
        "task_name": "",
        "activity_type": "",
        "description": "You don't have any projects assigned or no timesheet entries match your filters.",
        "total_hours": 0,
        "billable_hours": 0,
        "non_billable_hours": 0,
        "approval_status": "",
        "approved_by": "",
        "approved_date": ""
    }]
    return columns, data

@frappe.whitelist()
def get_managed_projects_for_filter():
    """Get projects for filter dropdown"""
    user = frappe.session.user
    
    if "SB Project Manager" not in frappe.get_roles(user):
        return []
    
    projects = frappe.get_all("Project",
        filters={"project_manager_user": user, "status": ["!=", "Cancelled"]},
        fields=["name", "project_name"],
        order_by="project_name"
    )
    
    return projects

@frappe.whitelist()
def get_employees_for_filter():
    """Get employees for filter dropdown"""
    user = frappe.session.user
    
    if "SB Project Manager" not in frappe.get_roles(user):
        return []
    
    # Get employees from timesheet entries for managed projects
    managed_projects = get_managed_projects(user)
    if not managed_projects:
        return []
    
    project_filter = "', '".join(managed_projects)
    
    employees = frappe.db.sql(f"""
        SELECT DISTINCT ts.employee, emp.employee_name
        FROM `tabTimesheet` ts
        INNER JOIN `tabEmployee` emp ON ts.employee = emp.name
        WHERE ts.project IN ('{project_filter}')
        ORDER BY emp.employee_name
    """, as_dict=True)
    
    return employees
