import frappe
from frappe import _

def validate_task_creation(doc, method):
    """Validate that only project managers can create tasks for their projects"""
    if not doc.project:
        return
    
    # Get project manager for this project
    project_manager = frappe.get_value("Project", doc.project, "project_manager_user")
    
    if not project_manager:
        frappe.throw(_("Project Manager not assigned to this project. Please contact administrator."))
    
    # Check if current user is the project manager
    if frappe.session.user != project_manager:
        frappe.throw(_("Only the assigned Project Manager can create tasks for this project. "
                      "Please contact the Project Manager: {0}").format(project_manager))

@frappe.whitelist()
def get_project_manager_tasks(project_name):
    """Get tasks for a project (only accessible by project manager)"""
    user = frappe.session.user
    
    # Validate project manager
    project_manager = frappe.get_value("Project", project_name, "project_manager_user")
    if project_manager != user:
        frappe.throw(_("You can only view tasks for projects you manage"))
    
    # Get tasks for this project
    tasks = frappe.get_all("Task",
        filters={"project": project_name},
        fields=["name", "subject", "status", "priority", "exp_start_date", "exp_end_date", "progress"],
        order_by="creation desc"
    )
    
    return tasks

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
