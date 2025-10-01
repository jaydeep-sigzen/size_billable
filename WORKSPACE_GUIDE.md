# Size Billable Workspace Configuration Guide

This document outlines the workspace configurations for the Size Billable app, designed to provide role-based access and optimized user experiences.

## Workspace Overview

The Size Billable app includes comprehensive workspace configurations for different user roles and DocTypes, ensuring each user has access to relevant tools and information based on their responsibilities.

## Role-Based Workspaces

### 1. Project Manager Workspace (`project_manager.json`)

**Target Users**: Users with SB Project Manager role
**Color**: Green (#2E7D32)
**Icon**: Briefcase

**Features**:
- Project management tools
- Timesheet approval system
- Task creation and management
- Comprehensive reporting
- Bulk operations for timesheet approval

**Shortcuts**:
- Project creation and management
- Timesheet review and approval
- Task creation
- Timesheet Approval Report
- Project Summary Report
- Billing Report

**Charts**:
- Project Summary
- Timesheet Approval Status
- Billable Hours Overview

**Onboarding Steps**:
1. Create your first project
2. Review timesheet entries
3. Create tasks for team members

### 2. Project User Workspace (`project_user.json`)

**Target Users**: Users with Project User role
**Color**: Blue (#1976D2)
**Icon**: Person

**Features**:
- Personal timesheet management
- Task viewing and updates
- Personal reporting
- Time tracking tools

**Shortcuts**:
- Timesheet creation
- Task viewing
- Personal timesheet reports
- Project task status

**Charts**:
- My Timesheet Summary
- Task Progress
- Billable Hours This Month

**Onboarding Steps**:
1. Log your first timesheet
2. View assigned tasks
3. Track billable hours

### 3. Customer Workspace (`customer.json`)

**Target Users**: Users with Customer role
**Color**: Pink (#E91E63)
**Icon**: Globe

**Features**:
- Customer portal access
- Billing information viewing
- Project status monitoring
- Limited reporting access

**Shortcuts**:
- Customer Portal Dashboard
- Billing Reports
- Project Status Reports

**Charts**:
- Project Hours Summary
- Monthly Billing Overview
- Project Progress

**Onboarding Steps**:
1. Access customer portal
2. Review billing details
3. Track project progress

## DocType-Specific Workspaces

### 4. Project Workspace (`project.json`)

**Extends**: Project DocType
**Features**: Project-specific tools and analytics
**Charts**: Project hours breakdown, task progress, billing summary

### 5. Timesheet Workspace (`timesheet.json`)

**Extends**: Timesheet DocType
**Features**: Timesheet management and approval tools
**Charts**: Hours distribution, approval status, monthly summary

### 6. Task Workspace (`task.json`)

**Extends**: Task DocType
**Features**: Task management and progress tracking
**Charts**: Task status distribution, progress by project, completion timeline

## Report-Specific Workspaces

### 7. Timesheet Approval Report Workspace (`timesheet_approval_report.json`)

**Features**: Approval workflow management
**Charts**: Approval status distribution, pending approvals, approval trends

### 8. Billing Report Workspace (`billing_report.json`)

**Features**: Billing analysis and reporting
**Charts**: Billing by project, monthly trends, billable vs non-billable hours

## Main App Workspace

### 9. Size Billable Workspace (`size_billable.json`)

**Default Workspace**: Yes
**Features**: Comprehensive overview of all app functionality
**Charts**: Project overview, timesheet status, billing summary

## Workspace Features

### Charts
Each workspace includes relevant charts that provide visual insights:
- **Half-width charts**: Quick overview metrics
- **Full-width charts**: Detailed analysis and trends

### Shortcuts
Quick access to frequently used DocTypes, Reports, and Pages:
- **DocType shortcuts**: Direct creation and access
- **Report shortcuts**: Quick report access
- **Page shortcuts**: Custom dashboard access

### Links
Navigation links to related pages and dashboards:
- **Dashboard pages**: Custom Vue.js interfaces
- **Report pages**: Specialized report interfaces
- **Portal pages**: Customer-facing interfaces

### Onboarding
Step-by-step guidance for new users:
- **Role-specific steps**: Tailored to user responsibilities
- **Progressive disclosure**: Learn features gradually
- **Action-oriented**: Direct users to take specific actions

## Implementation Notes

### Workspace Registration
All workspaces are registered in `hooks.py`:
```python
workspace = [
    "size_billable.workspace.project_manager",
    "size_billable.workspace.project_user", 
    "size_billable.workspace.customer",
    # ... other workspaces
]
```

### Role Assignment
Workspaces are automatically assigned based on user roles:
- **SB Project Manager**: Gets project_manager workspace
- **Project User**: Gets project_user workspace
- **Customer**: Gets customer workspace

### Customization
Workspaces can be customized by:
- Modifying JSON configuration files
- Adding new shortcuts and links
- Updating charts and onboarding steps
- Creating role-specific customizations

## Security Considerations

- **Role-based access**: Each workspace respects user permissions
- **Data isolation**: Customers only see their own data
- **Approval workflows**: Proper authorization for sensitive operations
- **CSRF protection**: Secure API endpoints

## Best Practices

1. **Keep workspaces focused**: Each workspace should serve a specific user type
2. **Use consistent colors**: Maintain visual consistency across workspaces
3. **Provide clear navigation**: Make it easy to find relevant tools
4. **Include onboarding**: Help new users get started quickly
5. **Regular updates**: Keep workspaces current with app features

## Troubleshooting

### Common Issues
1. **Workspace not appearing**: Check role assignments and permissions
2. **Charts not loading**: Verify chart configurations and data availability
3. **Shortcuts not working**: Check DocType and Report permissions
4. **Onboarding not showing**: Ensure user has appropriate role

### Debug Steps
1. Check user role assignments
2. Verify workspace JSON syntax
3. Test permissions for DocTypes and Reports
4. Check browser console for JavaScript errors
5. Verify API endpoint accessibility
