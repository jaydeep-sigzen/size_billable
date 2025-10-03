"""
Customer Portal API Endpoints

This module provides API endpoints for the customer portal functionality, allowing customers
to view their project information, billing details, and reports through a secure web interface.

Key Features:
- Project listing and details for customers
- Billing summary and detailed billing data
- Dashboard data aggregation
- Security validation for customer access
- Month-wise billing breakdown

All endpoints include proper security checks to ensure customers can only access their own data.
"""

import frappe
from frappe import _
from frappe.utils import flt, getdate, add_months, format_datetime
from datetime import datetime, timedelta
import calendar

@frappe.whitelist()
def get_customer_projects(customer_name=None):
    """
    Get projects for the current customer user
    
    Security Rules:
    - Only users with "Customer" role can access
    - Customers can only see their own projects
    - Only approved billable hours are visible (approved_by field is not null)
    - September 2025 view: Shows only data approved through August 2025
    """
    user = frappe.session.user
    
    # Validate customer role
    if "Customer" not in frappe.get_roles(user):
        frappe.throw(_("Access denied. Only customers can access this portal."))
    
    # Get customer from user
    if not customer_name:
        customer_name = frappe.get_value("User", user, "customer")
        if not customer_name:
            frappe.throw(_("No customer associated with this user"))
    
    # Get projects for this customer
    projects = frappe.get_all("Project", 
        filters={"customer": customer_name, "status": ["!=", "Cancelled"]},
        fields=["name", "project_name", "billing_type", "total_purchased_hours", 
                "total_consumed_hours", "hourly_rate", "status", "project_manager_user"]
    )
    
    return projects

@frappe.whitelist()
def get_project_summary(project_name):
    """
    Get summary cards data for a project
    
    Returns data in the format required for summary cards:
    [Project Name]                    [Billing Type Badge]
    Total Purchased Hours:            1000
    Total Consumed Hours:             750
    Total Billable Hours (Approved):  600
    Remaining Hours:                  250
    """
    user = frappe.session.user
    
    # Validate customer role
    if "Customer" not in frappe.get_roles(user):
        frappe.throw(_("Access denied. Only customers can access this portal."))
    
    # Validate access to project
    project = frappe.get_doc("Project", project_name)
    customer_name = frappe.get_value("User", user, "customer")
    
    if project.customer != customer_name:
        frappe.throw(_("You don't have permission to access this project"))
    
    # Calculate summary data
    remaining_hours = (project.total_purchased_hours or 0) - (project.total_consumed_hours or 0)
    consumption_percentage = 0
    if project.total_purchased_hours > 0:
        consumption_percentage = (project.total_consumed_hours / project.total_purchased_hours) * 100
    
    # Get approved billable hours (only approved entries are visible to customers)
    # September 2025 view: Shows only data approved through August 2025
    approved_billable_hours = frappe.db.sql("""
        SELECT COALESCE(SUM(tsd.billable_hours), 0)
        FROM `tabTimesheet Detail` tsd
        INNER JOIN `tabTimesheet` ts ON tsd.parent = ts.name
        WHERE tsd.project = %s
        AND tsd.approved_by IS NOT NULL
        AND ts.status = 'Submitted'
        AND tsd.approved_on <= '2025-08-31 23:59:59'
    """, project_name, as_list=True)[0][0]
    
    return {
        "project_name": project.project_name,
        "billing_type": project.billing_type,
        "total_purchased_hours": project.total_purchased_hours,
        "total_consumed_hours": project.total_consumed_hours,
        "approved_billable_hours": approved_billable_hours,
        "remaining_hours": remaining_hours,
        "consumption_percentage": consumption_percentage,
        "hourly_rate": project.hourly_rate,
        "total_billable_amount": approved_billable_hours * (project.hourly_rate or 0),
        "status": project.status
    }

@frappe.whitelist()
def get_billing_data(project_name=None, month=None, year=None, employee=None, activity_type=None):
    """
    Get detailed billing data for customer portal with hierarchical structure
    
    Hierarchical Data Structure:
    📅 September 2024
      📁 Project: Website Redesign
        📋 Task: Frontend Development
          - Activity: Development | Employee: John Doe | 8 hours
          - Activity: Testing | Employee: Jane Smith | 4 hours
        📋 Task: Backend API
          - Activity: Development | Employee: Mike Johnson | 6 hours
    
    Security Rules:
    - Only approved billable hours are visible (approved_by field is not null)
    - September 2025 view: Shows only data approved through August 2025
    - No pending/unapproved entries visible to customers
    """
    user = frappe.session.user
    
    # Validate customer role
    if "Customer" not in frappe.get_roles(user):
        frappe.throw(_("Access denied. Only customers can access this portal."))
    
    # Validate customer access
    customer_name = frappe.get_value("User", user, "customer")
    if not customer_name:
        frappe.throw(_("No customer associated with this user"))
    
    # Set default to current month if not provided
    if not month or not year:
        now = datetime.now()
        month = now.month
        year = now.year
    
    # Get projects for this customer
    if project_name:
        # Validate project belongs to customer
        project_customer = frappe.get_value("Project", project_name, "customer")
        if project_customer != customer_name:
            frappe.throw(_("You don't have permission to access this project"))
        project_filter = project_name
    else:
        # Get all customer projects
        projects = frappe.get_all("Project", 
            filters={"customer": customer_name, "status": ["!=", "Cancelled"]},
            pluck="name"
        )
        if not projects:
            return {}
        project_filter = ["in", projects]
    
    # Calculate date range for the month
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1) - timedelta(days=1)
    
    # Build additional filters
    additional_filters = []
    filter_params = [project_filter, start_date, end_date]
    
    if employee:
        additional_filters.append("AND ts.employee_name LIKE %s")
        filter_params.append(f"%{employee}%")
    
    if activity_type:
        additional_filters.append("AND tsd.activity_type LIKE %s")
        filter_params.append(f"%{activity_type}%")
    
    filter_clause = " ".join(additional_filters)
    
    # Get approved timesheet data (only approved entries are visible to customers)
    # September 2025 view: Shows only data approved through August 2025
    billing_data = frappe.db.sql(f"""
        SELECT 
            tsd.name,
            tsd.project,
            tsd.task,
            tsd.activity_type,
            tsd.description,
            tsd.billable_hours,
            tsd.approved_by,
            tsd.approved_on,
            ts.employee,
            ts.employee_name,
            ts.start_date,
            p.project_name,
            p.billing_type,
            p.hourly_rate
        FROM `tabTimesheet Detail` tsd
        INNER JOIN `tabTimesheet` ts ON tsd.parent = ts.name
        INNER JOIN `tabProject` p ON tsd.project = p.name
        WHERE tsd.project = %s
        AND ts.status = 'Submitted'
        AND tsd.approved_by IS NOT NULL
        AND tsd.approved_on <= '2025-08-31 23:59:59'
        AND ts.start_date >= %s
        AND ts.start_date <= %s
        {filter_clause}
        ORDER BY ts.start_date DESC, p.project_name, tsd.task
    """, filter_params, as_dict=True)
    
    # Group data by month and project
    result = {}
    month_name = calendar.month_name[month]
    year_month = f"{year}-{month:02d}"
    
    result[year_month] = {
        "month": f"{month_name} {year}",
        "projects": {}
    }
    
    for entry in billing_data:
        project_name = entry.project_name
        task_name = entry.task or "General"
        
        if project_name not in result[year_month]["projects"]:
            result[year_month]["projects"][project_name] = {
                "project_name": project_name,
                "billing_type": entry.billing_type,
                "hourly_rate": entry.hourly_rate,
                "tasks": {}
            }
        
        if task_name not in result[year_month]["projects"][project_name]["tasks"]:
            result[year_month]["projects"][project_name]["tasks"][task_name] = []
        
        result[year_month]["projects"][project_name]["tasks"][task_name].append({
            "activity_type": entry.activity_type,
            "description": entry.description,
            "employee_name": entry.employee_name,
            "billable_hours": entry.billable_hours,
            "approved_by": entry.approved_by,
            "approved_on": format_datetime(entry.approved_on) if entry.approved_on else None,
            "date": entry.start_date.strftime("%Y-%m-%d")
        })
    
    return result

@frappe.whitelist()
def get_customer_dashboard_data():
    """Get complete dashboard data for customer portal"""
    user = frappe.session.user
    
    # Get customer projects
    projects = get_customer_projects()
    
    # Get current month data
    now = datetime.now()
    current_month_data = get_billing_data(month=now.month, year=now.year)
    
    # Calculate totals across all projects - optimized single query
    customer_name = frappe.get_value("User", user, "customer")
    totals = frappe.db.sql("""
        SELECT 
            COALESCE(SUM(p.total_purchased_hours), 0) as total_purchased,
            COALESCE(SUM(p.total_consumed_hours), 0) as total_consumed,
            COALESCE(SUM(tsd.billable_hours), 0) as total_approved
        FROM `tabProject` p
        LEFT JOIN `tabTimesheet Detail` tsd ON tsd.project = p.name
        LEFT JOIN `tabTimesheet` ts ON tsd.parent = ts.name
        WHERE p.customer = %s
        AND p.status != 'Cancelled'
        AND (tsd.approved_by IS NULL OR (tsd.approved_by IS NOT NULL AND ts.status = 'Submitted' AND tsd.approved_on <= '2025-08-31 23:59:59'))
    """, customer_name, as_dict=True)[0]
    
    return {
        "projects": projects,
        "current_month_data": current_month_data,
        "totals": {
            "total_purchased_hours": totals.total_purchased,
            "total_consumed_hours": totals.total_consumed,
            "total_approved_hours": totals.total_approved,
            "remaining_hours": totals.total_purchased - totals.total_consumed
        }
    }

@frappe.whitelist()
def get_available_months():
    """Get list of available months with approved data for customer"""
    user = frappe.session.user
    
    # Validate customer role
    if "Customer" not in frappe.get_roles(user):
        frappe.throw(_("Access denied. Only customers can access this portal."))
    
    customer_name = frappe.get_value("User", user, "customer")
    if not customer_name:
        return []
    
    # Get months with approved timesheet data
    # September 2025 view: Shows only data approved through August 2025
    months = frappe.db.sql("""
        SELECT DISTINCT 
            YEAR(ts.start_date) as year,
            MONTH(ts.start_date) as month
        FROM `tabTimesheet Detail` tsd
        INNER JOIN `tabTimesheet` ts ON tsd.parent = ts.name
        INNER JOIN `tabProject` p ON tsd.project = p.name
        WHERE p.customer = %s
        AND ts.status = 'Submitted'
        AND tsd.approved_by IS NOT NULL
        AND tsd.approved_on <= '2025-08-31 23:59:59'
        ORDER BY year DESC, month DESC
    """, customer_name, as_dict=True)
    
    result = []
    for month_data in months:
        month_name = calendar.month_name[month_data.month]
        result.append({
            "year": month_data.year,
            "month": month_data.month,
            "label": f"{month_name} {month_data.year}",
            "value": f"{month_data.year}-{month_data.month:02d}"
        })
    
    return result

@frappe.whitelist()
def get_available_employees():
    """Get list of employees who have worked on customer projects"""
    user = frappe.session.user
    
    # Validate customer role
    if "Customer" not in frappe.get_roles(user):
        frappe.throw(_("Access denied. Only customers can access this portal."))
    
    customer_name = frappe.get_value("User", user, "customer")
    if not customer_name:
        return []
    
    # Get employees with approved timesheet data
    employees = frappe.db.sql("""
        SELECT DISTINCT ts.employee_name
        FROM `tabTimesheet Detail` tsd
        INNER JOIN `tabTimesheet` ts ON tsd.parent = ts.name
        INNER JOIN `tabProject` p ON tsd.project = p.name
        WHERE p.customer = %s
        AND ts.status = 'Submitted'
        AND tsd.approved_by IS NOT NULL
        AND tsd.approved_on <= '2025-08-31 23:59:59'
        ORDER BY ts.employee_name
    """, customer_name, as_dict=True)
    
    return [emp.employee_name for emp in employees if emp.employee_name]

@frappe.whitelist()
def get_available_activity_types():
    """Get list of activity types used in customer projects"""
    user = frappe.session.user
    
    # Validate customer role
    if "Customer" not in frappe.get_roles(user):
        frappe.throw(_("Access denied. Only customers can access this portal."))
    
    customer_name = frappe.get_value("User", user, "customer")
    if not customer_name:
        return []
    
    # Get activity types with approved timesheet data
    activity_types = frappe.db.sql("""
        SELECT DISTINCT tsd.activity_type
        FROM `tabTimesheet Detail` tsd
        INNER JOIN `tabTimesheet` ts ON tsd.parent = ts.name
        INNER JOIN `tabProject` p ON tsd.project = p.name
        WHERE p.customer = %s
        AND ts.status = 'Submitted'
        AND tsd.approved_by IS NOT NULL
        AND tsd.approved_on <= '2025-08-31 23:59:59'
        ORDER BY tsd.activity_type
    """, customer_name, as_dict=True)
    
    return [act.activity_type for act in activity_types if act.activity_type]

@frappe.whitelist()
def get_customer_projects_for_filter():
    """Get customer projects for filter dropdown"""
    user = frappe.session.user
    
    # Validate customer role
    if "Customer" not in frappe.get_roles(user):
        frappe.throw(_("Access denied. Only customers can access this portal."))
    
    customer_name = frappe.get_value("User", user, "customer")
    if not customer_name:
        return []
    
    # Get projects for this customer
    projects = frappe.get_all("Project", 
        filters={"customer": customer_name, "status": ["!=", "Cancelled"]},
        fields=["name", "project_name"]
    )
    
    return [{"name": p.name, "project_name": p.project_name} for p in projects]
