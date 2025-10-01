"""
Desktop Configuration for Size Billable App

This module configures the desktop shortcuts and navigation items for the Size Billable app,
providing easy access to key reports and pages for different user roles.

Desktop Items:
- Timesheet Approval Report: Primary tool for SB Project Managers
- Project Billing Summary: Billing overview and monitoring
- Customer Portal: Customer-facing dashboard

Features:
- Role-based visibility (handled by Frappe's permission system)
- Onboarding integration for new users
- Icon and description configuration
- Organized under Size Billable section

The configuration ensures that users have quick access to the most
important features of the Size Billable system from the desktop.
"""

from frappe import _

def get_data():
    return [
        {
            "label": _("Size Billable"),
            "icon": "octicon octicon-clock",
            "items": [
                {
                    "type": "report",
                    "name": "Timesheet Approval Report",
                    "label": _("Timesheet Approval Report"),
                    "description": _("Manage timesheet approvals for your projects"),
                    "onboard": 1,
                },
                {
                    "type": "report",
                    "name": "Project Billing Summary", 
                    "label": _("Project Billing Summary"),
                    "description": _("Overview of project billing and hour consumption"),
                    "onboard": 1,
                },
                {
                    "type": "page",
                    "name": "customer-portal",
                    "label": _("Customer Portal"),
                    "description": _("Customer billing dashboard"),
                    "onboard": 1,
                }
            ]
        }
    ]

