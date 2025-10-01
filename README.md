# Size Billable

Enhanced billing and timesheet management for ERPNext with advanced project management features.

## Features

### Project Management
- **Fixed Cost vs Hourly Billing**: Support for both billing types with automatic hour tracking
- **SB Project Manager Restrictions**: Only assigned SB project managers can create tasks for their projects
- **Hour Distribution**: Automatic calculation of billable vs non-billable hours
- **Project Summary**: Real-time tracking of purchased, consumed, and remaining hours

### Timesheet Management
- **Enhanced Timesheet Detail**: Child table with approval workflow and hour distribution
- **Manager Approval System**: Project managers can approve/reject timesheet entries
- **Bulk Operations**: Approve or reject multiple timesheet entries at once
- **Hour Adjustment**: Managers can adjust billable hours with automatic non-billable calculation

### Customer Portal
- **Vue.js Dashboard**: Modern, responsive customer portal interface
- **Project Overview**: Summary cards showing purchased, consumed, and remaining hours
- **Detailed Billing**: Month-by-month breakdown of approved billable hours
- **Filtering Options**: Filter by project and month for detailed analysis
- **Real-time Data**: Live updates from approved timesheet entries

### Reporting
- **Manager Approval Report**: Interactive report for project managers
- **Customer Reports**: Vue.js-based reports for customer consumption
- **Billing Analytics**: Comprehensive billing data analysis
- **Export Capabilities**: Export reports in multiple formats

### Security & Access Control
- **Role-based Access**: Different access levels for managers and customers
- **Customer Data Isolation**: Customers can only see their own project data
- **CSRF Protection**: Secure API endpoints with proper authentication
- **Approval Workflow**: Multi-level approval system for timesheet entries

## Installation

```bash
# Clone the app
git clone <repository-url> apps/size_billable

# Install in development mode
pip install -e apps/size_billable

# Install on site
bench --site [site-name] install-app size_billable
```

## Configuration

1. **Project Setup**: Configure projects with billing type (Fixed Cost or Hourly)
2. **User Roles**: Assign project manager roles to users
3. **Customer Portal**: Access customer portal at `/customer-portal`
4. **Reports**: Access manager reports from the Reports section

## API Endpoints

- `get_customer_projects()` - Get projects for customer
- `get_project_summary()` - Get project summary data
- `get_billing_data()` - Get detailed billing information
- `get_customer_dashboard_data()` - Get complete dashboard data
- `get_available_months()` - Get available months with data

## Customization

The app includes several customization hooks:
- Project validation and hour updates
- Timesheet calculation and locking
- Task creation restrictions
- Approval status management

## License

MIT
