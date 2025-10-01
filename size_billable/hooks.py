"""
Size Billable App Configuration and Hooks

This file contains the main configuration for the Size Billable app including:
- App metadata and branding
- Custom field definitions for Project and Timesheet Detail DocTypes
- DocType event handlers for validation and automation
- Client-side script inclusions for enhanced UI functionality
- Workspace creation and fixture management
- Report registration and configuration

The hooks system allows the app to integrate seamlessly with ERPNext's core functionality.
"""

from . import __version__

# App metadata and branding configuration
app_name = "size_billable"
app_title = "Size Billable"
app_publisher = "Your Company"
app_description = "Enhanced billing and timesheet management for ERPNext"
app_icon = "octicon octicon-clock"
app_color = "blue"
app_email = "support@yourcompany.com"
app_license = "MIT"

# Custom fields configuration
custom_fields = {
    "Project": [
        {
            "fieldname": "billing_type",
            "fieldtype": "Select",
            "options": "Fixed Cost\nHourly Billing",
            "label": "Billing Type",
            "reqd": 1,
            "default": "Hourly Billing",
            "insert_after": "project_type",
            "description": "Defines how this project will be billed to the customer"
        },
        {
            "fieldname": "total_purchased_hours",
            "fieldtype": "Float",
            "label": "Total Purchased Hours",
            "insert_after": "estimated_costing",
            "description": "Total hours purchased by customer (for Hourly Billing projects)"
        },
        {
            "fieldname": "total_consumed_hours",
            "fieldtype": "Float",
            "label": "Total Consumed Hours",
            "read_only": 1,
            "insert_after": "total_purchased_hours",
            "description": "Auto-calculated total of approved billable hours"
        },
        {
            "fieldname": "project_manager_user",
            "fieldtype": "Link",
            "options": "User",
            "label": "SB Project Manager",
            "reqd": 1,
            "insert_after": "customer",
            "description": "User responsible for managing this project and approving timesheets"
        },
        {
            "fieldname": "hourly_rate",
            "fieldtype": "Currency",
            "label": "Hourly Rate",
            "insert_after": "total_purchased_hours",
            "description": "Rate per hour for billing (for Hourly Billing projects)"
        },
        {
            "fieldname": "billing_section",
            "fieldtype": "Section Break",
            "label": "Billing Configuration",
            "insert_after": "project_manager_user",
            "collapsible": 1
        }
    ],
    "Timesheet Detail": [
        {
            "fieldname": "billable_hours",
            "fieldtype": "Float",
            "label": "Billable Hours",
            "default": 0,
            "insert_after": "hours",
            "description": "Hours that can be billed to customer"
        },
        {
            "fieldname": "non_billable_hours",
            "fieldtype": "Float",
            "label": "Non-Billable Hours",
            "read_only": 1,
            "insert_after": "billable_hours",
            "description": "Hours for internal/unbillable work (auto-calculated)"
        },
        {
            "fieldname": "approval_section",
            "fieldtype": "Section Break",
            "label": "Approval Details",
            "insert_after": "non_billable_hours",
            "collapsible": 1
        },
        {
            "fieldname": "approved_by",
            "fieldtype": "Link",
            "options": "User",
            "label": "Approved By",
            "read_only": 1,
            "insert_after": "approval_section",
            "description": "SB Project Manager who approved this entry"
        },
        {
            "fieldname": "approved_on",
            "fieldtype": "Datetime",
            "label": "Approved On",
            "read_only": 1,
            "insert_after": "approved_by",
            "description": "Timestamp when this entry was approved"
        },
        {
            "fieldname": "approval_status",
            "fieldtype": "Select",
            "options": "Pending\nApproved\nRejected",
            "label": "Approval Status",
            "default": "Pending",
            "read_only": 1,
            "insert_after": "approved_on",
            "description": "Current approval status of this timesheet entry"
        }
    ]
}

# DocType Events
doc_events = {
    "Project": {
        "validate": "size_billable.api.project.validate_project_manager",
        "on_update": "size_billable.api.project.update_project_hours"
    },
    "Timesheet": {
        "validate": "size_billable.api.timesheet.calculate_billable_hours",
        "on_submit": "size_billable.api.timesheet.lock_timesheet_entries",
        "on_cancel": "size_billable.api.timesheet.unlock_timesheet_entries"
    },
    "Timesheet Detail": {
        "validate": "size_billable.api.timesheet_detail.validate_hour_distribution",
        "on_update": "size_billable.api.timesheet_detail.update_approval_status"
    },
    "Task": {
        "validate": "size_billable.api.task.validate_task_creation"
    }
}

# Client Scripts
app_include_js = [
    "size_billable/public/js/project.js",
    "size_billable/public/js/timesheet.js",
    "size_billable/public/js/timesheet_approval_report.js",
    "size_billable/public/js/manager_approval_report.js"
]

# Installation
after_install = "size_billable.setup.create_workspaces.create_workspaces"


# Reports
report_data = [
    {
        "doctype": "Report",
        "name": "Timesheet Approval Report",
        "report_name": "Timesheet Approval Report",
        "module": "Size Billable",
        "is_standard": "No"
    },
    {
        "doctype": "Report", 
        "name": "Project Billing Summary",
        "report_name": "Project Billing Summary",
        "module": "Size Billable",
        "is_standard": "No"
    },
    {
        "doctype": "Report",
        "name": "Manager Approval Report",
        "report_name": "Manager Approval Report",
        "module": "Size Billable",
        "is_standard": "No"
    }
]

# Website pages
website_route_rules = [
    {"from_route": "/customer-portal", "to_route": "customer_portal"},
    {"from_route": "/customer-portal/<path:path>", "to_route": "customer_portal"}
]

# Scheduled tasks
scheduler_events = {
    "daily": [
        "size_billable.api.scheduler.update_project_hours_daily"
    ],
    "weekly": [
        "size_billable.api.scheduler.generate_billing_reports"
    ]
}

# Fixtures
fixtures = [
    {
        "dt": "Custom Field",
        "filters": [
            ["app_name", "=", "size_billable"]
        ]
    },
    {
        "dt": "Report",
        "filters": [
            ["module", "=", "Size Billable"]
        ]
    }
]