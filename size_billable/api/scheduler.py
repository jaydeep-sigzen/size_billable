"""
Scheduler and Background Tasks API

This module handles scheduled tasks and background operations for the Size Billable app,
including automated hour calculations, billing report generation, and system health monitoring.

Key Features:
- Daily project hour consumption updates
- Weekly billing report generation
- System health monitoring and metrics
- Automated project budget tracking
- Background data synchronization

Scheduled Tasks:
- Daily: Update project consumed hours from approved timesheets
- Weekly: Generate customer billing reports
- On-demand: System health checks and metrics

The module ensures data consistency and provides automated maintenance
for the Size Billable system without manual intervention.
"""

import frappe
from frappe.utils import now_datetime, add_days
from frappe import _

def update_project_hours_daily():
    """Daily task to update project consumed hours"""
    frappe.logger().info("Starting daily project hours update")
    
    # Get all hourly billing projects
    projects = frappe.get_all("Project", 
        filters={"billing_type": "Hourly Billing", "status": "Open"},
        fields=["name"]
    )
    
    updated_count = 0
    for project in projects:
        try:
            update_project_consumed_hours(project.name)
            updated_count += 1
        except Exception as e:
            frappe.logger().error(f"Error updating project {project.name}: {str(e)}")
    
    frappe.logger().info(f"Updated {updated_count} projects")

def generate_billing_reports():
    """Weekly task to generate billing reports"""
    frappe.logger().info("Starting weekly billing report generation")
    
    # Generate reports for all customers
    customers = frappe.get_all("Customer", 
        filters={"disabled": 0},
        fields=["name"]
    )
    
    for customer in customers:
        try:
            generate_customer_billing_report(customer.name)
        except Exception as e:
            frappe.logger().error(f"Error generating report for customer {customer.name}: {str(e)}")

def update_project_consumed_hours(project_name):
    """Update consumed hours for a specific project"""
    # Check billing type first to avoid unnecessary queries
    billing_type = frappe.get_value("Project", project_name, "billing_type")
    
    if billing_type == "Hourly Billing":
        total_consumed = frappe.db.sql("""
            SELECT COALESCE(SUM(tsd.billable_hours), 0)
            FROM `tabTimesheet Detail` tsd
            INNER JOIN `tabTimesheet` ts ON tsd.parent = ts.name
            WHERE tsd.project = %s
            AND tsd.approved_by IS NOT NULL
            AND ts.status = 'Submitted'
        """, project_name, as_list=True)[0][0]
        
        # Use direct SQL update for better performance
        frappe.db.set_value("Project", project_name, "total_consumed_hours", total_consumed)

def generate_customer_billing_report(customer_name):
    """Generate billing report for a customer"""
    # This could generate PDF reports, send emails, etc.
    pass

@frappe.whitelist()
def get_system_health():
    """Get system health metrics for Size Billable"""
    # Get all metrics in a single optimized query
    health_data = frappe.db.sql("""
        SELECT 
            (SELECT COUNT(*) FROM `tabTimesheet Detail` tsd
             INNER JOIN `tabTimesheet` ts ON tsd.parent = ts.name
             WHERE tsd.approved_by IS NULL AND ts.status = 'Submitted') as pending_approvals,
            (SELECT COUNT(*) FROM `tabProject` p
             WHERE p.billing_type = 'Hourly Billing' 
             AND p.total_consumed_hours > p.total_purchased_hours
             AND p.status = 'Open') as over_budget_projects,
            (SELECT COALESCE(SUM(p.total_consumed_hours * p.hourly_rate), 0) 
             FROM `tabProject` p
             WHERE p.billing_type = 'Hourly Billing' AND p.status = 'Open') as total_billable_amount
    """, as_dict=True)[0]
    
    return {
        "pending_approvals": health_data.pending_approvals,
        "over_budget_projects": health_data.over_budget_projects,
        "total_billable_amount": health_data.total_billable_amount,
        "timestamp": now_datetime()
    }