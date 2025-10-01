"""
Customer Portal Page Handler

This module handles the customer portal web page, providing authentication,
authorization, and context data for the customer-facing dashboard.

Key Features:
- User authentication and session validation
- Customer role verification
- Customer data context preparation
- Security checks for customer access
- Page context setup for Vue.js frontend

Security:
- Only authenticated users can access the portal
- Customer role required for access
- Customer-specific data isolation
- Session-based authentication

The module serves as the entry point for the customer portal,
ensuring proper security and data context for the frontend application.
"""

import frappe
from frappe import _

def get_context(context):
    """Get context for customer portal page"""
    context.title = _("Customer Portal")
    context.no_cache = 1
    
    # Check if user is logged in
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login to access the customer portal"), frappe.PermissionError)
    
    # Check if user has customer role
    if not frappe.has_permission("Customer", "read"):
        frappe.throw(_("You don't have permission to access the customer portal"), frappe.PermissionError)
    
    # Get customer information
    customer_name = frappe.get_value("User", frappe.session.user, "customer")
    if not customer_name:
        frappe.throw(_("No customer associated with this user"), frappe.PermissionError)
    
    context.customer_name = customer_name
    context.user = frappe.session.user
    
    return context
