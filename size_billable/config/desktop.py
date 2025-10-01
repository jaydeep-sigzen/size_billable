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

