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
        
        project.total_consumed_hours = total_consumed
        project.save()

def generate_customer_billing_report(customer_name):
    """Generate billing report for a customer"""
    # This could generate PDF reports, send emails, etc.
    pass

@frappe.whitelist()
def get_system_health():
    """Get system health metrics for Size Billable"""
    # Get pending approvals count
    pending_approvals = frappe.db.sql("""
        SELECT COUNT(*)
        FROM `tabTimesheet Detail` tsd
        INNER JOIN `tabTimesheet` ts ON tsd.parent = ts.name
        WHERE tsd.approved_by IS NULL
        AND ts.status = 'Submitted'
    """)[0][0]
    
    # Get over-budget projects
    over_budget_projects = frappe.db.sql("""
        SELECT COUNT(*)
        FROM `tabProject`
        WHERE billing_type = 'Hourly Billing'
        AND total_consumed_hours > total_purchased_hours
        AND status = 'Open'
    """)[0][0]
    
    # Get total billable amount
    total_billable = frappe.db.sql("""
        SELECT SUM(p.total_consumed_hours * p.hourly_rate)
        FROM `tabProject` p
        WHERE p.billing_type = 'Hourly Billing'
        AND p.status = 'Open'
    """)[0][0] or 0
    
    return {
        "pending_approvals": pending_approvals,
        "over_budget_projects": over_budget_projects,
        "total_billable_amount": total_billable,
        "timestamp": now_datetime()
    }