"""
Project Billing Summary Report

This report provides comprehensive billing information for projects, including
hour consumption, billing amounts, and project status for SB Project Managers.

Key Features:
- Project billing overview with hour tracking
- Customer and billing type information
- Hour consumption vs purchased hours comparison
- Billing amount calculations
- Project manager assignment details
- Budget monitoring and alerts

Security:
- Only accessible by users with SB Project Manager role
- Project managers can only see their assigned projects
- All financial data is properly formatted and validated

The report provides essential insights for project managers to monitor
project budgets and billing status in real-time.
"""

import frappe
from frappe import _
from frappe.utils import flt, format_currency

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {
            "fieldname": "project_name", 
            "label": "Project", 
            "fieldtype": "Data", 
            "width": 150
        },
        {
            "fieldname": "customer", 
            "label": "Customer", 
            "fieldtype": "Data", 
            "width": 120
        },
        {
            "fieldname": "billing_type", 
            "label": "Billing Type", 
            "fieldtype": "Data", 
            "width": 100
        },
        {
            "fieldname": "project_manager", 
            "label": "SB Project Manager", 
            "fieldtype": "Data", 
            "width": 120
        },
        {
            "fieldname": "total_purchased_hours", 
            "label": "Purchased Hours", 
            "fieldtype": "Float", 
            "width": 100
        },
        {
            "fieldname": "total_consumed_hours", 
            "label": "Consumed Hours", 
            "fieldtype": "Float", 
            "width": 100
        },
        {
            "fieldname": "remaining_hours", 
            "label": "Remaining Hours", 
            "fieldtype": "Float", 
            "width": 100
        },
        {
            "fieldname": "consumption_percentage", 
            "label": "Consumption %", 
            "fieldtype": "Percent", 
            "width": 80
        },
        {
            "fieldname": "hourly_rate", 
            "label": "Hourly Rate", 
            "fieldtype": "Currency", 
            "width": 100
        },
        {
            "fieldname": "total_billable_amount", 
            "label": "Billable Amount", 
            "fieldtype": "Currency", 
            "width": 120
        },
        {
            "fieldname": "pending_approvals", 
            "label": "Pending Approvals", 
            "fieldtype": "Int", 
            "width": 100
        },
        {
            "fieldname": "status", 
            "label": "Project Status", 
            "fieldtype": "Data", 
            "width": 100
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
    
    # Optimized query with all calculations in SQL to avoid N+1 problem
    query = """
        SELECT 
            p.name,
            p.project_name,
            p.customer,
            p.billing_type,
            p.project_manager_user,
            p.total_purchased_hours,
            p.total_consumed_hours,
            p.hourly_rate,
            p.status,
            u.full_name as project_manager,
            (p.total_purchased_hours - p.total_consumed_hours) as remaining_hours,
            CASE 
                WHEN p.total_purchased_hours > 0 
                THEN (p.total_consumed_hours / p.total_purchased_hours) * 100 
                ELSE 0 
            END as consumption_percentage,
            (p.total_consumed_hours * p.hourly_rate) as total_billable_amount,
            COALESCE(pending_counts.pending_approvals, 0) as pending_approvals
        FROM `tabProject` p
        LEFT JOIN `tabUser` u ON p.project_manager_user = u.name
        LEFT JOIN (
            SELECT 
                tsd.project,
                COUNT(*) as pending_approvals
            FROM `tabTimesheet Detail` tsd
            INNER JOIN `tabTimesheet` ts ON tsd.parent = ts.name
            WHERE ts.status = 'Submitted'
            AND tsd.approval_status = 'Pending'
            GROUP BY tsd.project
        ) pending_counts ON p.name = pending_counts.project
        WHERE p.name IN %(projects)s
    """
    
    query_params = {"projects": managed_projects}
    
    # Apply filters
    if filters.get("project"):
        query += " AND p.name = %(project)s"
        query_params["project"] = filters.get("project")
    
    if filters.get("billing_type"):
        query += " AND p.billing_type = %(billing_type)s"
        query_params["billing_type"] = filters.get("billing_type")
    
    if filters.get("status"):
        query += " AND p.status = %(status)s"
        query_params["status"] = filters.get("status")
    
    query += " ORDER BY p.project_name"
    
    data = frappe.db.sql(query, query_params, as_dict=True)
    
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
            "fieldname": "billing_type",
            "label": "Billing Type",
            "fieldtype": "Select",
            "options": "Fixed Cost\nHourly Billing"
        },
        {
            "fieldname": "status",
            "label": "Project Status",
            "fieldtype": "Select",
            "options": "Open\nCompleted\nCancelled"
        }
    ]

