// Enhanced Timesheet Approval Report with interactive features
frappe.query_reports["Timesheet Approval Report"] = {
    onload: function (report) {
        // Add custom buttons to the report
        report.page.add_inner_button(__("Approve Selected"), function () {
            bulk_approve_entries(report);
        }, __("Actions"));

        report.page.add_inner_button(__("Reject Selected"), function () {
            bulk_reject_entries(report);
        }, __("Actions"));

        report.page.add_inner_button(__("Save Changes"), function () {
            save_hour_changes(report);
        }, __("Actions"));

        report.page.add_inner_button(__("Refresh Data"), function () {
            report.refresh();
        }, __("Actions"));

        // Add event listeners for hour editing
        setup_hour_editing(report);
    },

    onload_view: function (report) {
        // Setup real-time hour calculation
        setup_real_time_calculation(report);
    }
};

function setup_hour_editing(report) {
    // Add event listeners for editable fields
    $(document).on('change', 'input[data-fieldname="billable_hours"]', function () {
        const row = $(this).closest('tr');
        const billable_hours = parseFloat($(this).val()) || 0;
        const total_hours = parseFloat(row.find('td[data-fieldname="hours"]').text()) || 0;
        const non_billable_hours = total_hours - billable_hours;

        // Update non-billable hours
        row.find('td[data-fieldname="non_billable_hours"]').text(non_billable_hours.toFixed(2));

        // Highlight changed row
        row.addClass('table-warning');
    });

    $(document).on('change', 'input[data-fieldname="non_billable_hours"]', function () {
        const row = $(this).closest('tr');
        const non_billable_hours = parseFloat($(this).val()) || 0;
        const total_hours = parseFloat(row.find('td[data-fieldname="hours"]').text()) || 0;
        const billable_hours = total_hours - non_billable_hours;

        // Update billable hours
        row.find('input[data-fieldname="billable_hours"]').val(billable_hours.toFixed(2));

        // Highlight changed row
        row.addClass('table-warning');
    });
}

function setup_real_time_calculation(report) {
    // Add visual feedback for hour changes
    $(document).on('input', 'input[data-fieldname="billable_hours"], input[data-fieldname="non_billable_hours"]', function () {
        const row = $(this).closest('tr');
        const billable_hours = parseFloat(row.find('input[data-fieldname="billable_hours"]').val()) || 0;
        const non_billable_hours = parseFloat(row.find('input[data-fieldname="non_billable_hours"]').val()) || 0;
        const total_hours = parseFloat(row.find('td[data-fieldname="hours"]').text()) || 0;

        // Validate total
        const calculated_total = billable_hours + non_billable_hours;
        if (Math.abs(calculated_total - total_hours) > 0.01) {
            row.addClass('table-danger');
            $(this).addClass('is-invalid');
        } else {
            row.removeClass('table-danger');
            $(this).removeClass('is-invalid');
        }
    });
}

function bulk_approve_entries(report) {
    const selected_rows = get_selected_rows(report);

    if (selected_rows.length === 0) {
        frappe.msgprint(__("Please select at least one entry to approve"));
        return;
    }

    // Validate hour distribution for selected rows
    const invalid_rows = validate_hour_distribution(selected_rows);
    if (invalid_rows.length > 0) {
        frappe.msgprint(__("Please fix hour distribution for selected entries before approving"));
        return;
    }

    frappe.confirm(
        __("Are you sure you want to approve {0} selected entries?", [selected_rows.length]),
        function () {
            const timesheet_details = selected_rows.map(row => row.name);
            const project_name = get_current_project(report);

            frappe.call({
                method: "size_billable.api.project.approve_timesheet_entries",
                args: {
                    project_name: project_name,
                    timesheet_details: timesheet_details,
                    action: "approve"
                },
                callback: function (r) {
                    if (r.message) {
                        frappe.msgprint(__("Successfully approved {0} entries", [r.message.approved_count]));
                        report.refresh();
                    }
                }
            });
        }
    );
}

function bulk_reject_entries(report) {
    const selected_rows = get_selected_rows(report);

    if (selected_rows.length === 0) {
        frappe.msgprint(__("Please select at least one entry to reject"));
        return;
    }

    frappe.confirm(
        __("Are you sure you want to reject {0} selected entries?", [selected_rows.length]),
        function () {
            const timesheet_details = selected_rows.map(row => row.name);
            const project_name = get_current_project(report);

            frappe.call({
                method: "size_billable.api.project.approve_timesheet_entries",
                args: {
                    project_name: project_name,
                    timesheet_details: timesheet_details,
                    action: "reject"
                },
                callback: function (r) {
                    if (r.message) {
                        frappe.msgprint(__("Successfully rejected {0} entries", [r.message.approved_count]));
                        report.refresh();
                    }
                }
            });
        }
    );
}

function save_hour_changes(report) {
    const changed_rows = get_changed_rows(report);

    if (changed_rows.length === 0) {
        frappe.msgprint(__("No changes to save"));
        return;
    }

    // Validate all changed rows
    const invalid_rows = validate_hour_distribution(changed_rows);
    if (invalid_rows.length > 0) {
        frappe.msgprint(__("Please fix hour distribution before saving"));
        return;
    }

    const hour_updates = {};
    changed_rows.forEach(row => {
        const billable_hours = parseFloat(row.find('input[data-fieldname="billable_hours"]').val()) || 0;
        const non_billable_hours = parseFloat(row.find('input[data-fieldname="non_billable_hours"]').val()) || 0;

        hour_updates[row.name] = {
            billable_hours: billable_hours,
            non_billable_hours: non_billable_hours
        };
    });

    frappe.call({
        method: "size_billable.api.timesheet_detail.bulk_update_hours",
        args: {
            timesheet_details: Object.keys(hour_updates),
            billable_hours_dict: hour_updates
        },
        callback: function (r) {
            if (r.message) {
                frappe.msgprint(__("Successfully updated {0} entries", [r.message.updated_count]));
                // Remove highlighting
                changed_rows.forEach(row => {
                    row.removeClass('table-warning');
                });
                report.refresh();
            }
        }
    });
}

function get_selected_rows(report) {
    const selected_rows = [];
    report.wrapper.find('input[data-fieldname="checkbox"]:checked').each(function () {
        const row = $(this).closest('tr');
        const row_data = report.datatable.datamanager.getRow(row.index());
        selected_rows.push({
            name: row_data.name,
            element: row
        });
    });
    return selected_rows;
}

function get_changed_rows(report) {
    const changed_rows = [];
    report.wrapper.find('tr.table-warning').each(function () {
        const row = $(this);
        const row_data = report.datatable.datamanager.getRow(row.index());
        changed_rows.push({
            name: row_data.name,
            element: row
        });
    });
    return changed_rows;
}

function validate_hour_distribution(rows) {
    const invalid_rows = [];

    rows.forEach(row => {
        const billable_hours = parseFloat(row.element.find('input[data-fieldname="billable_hours"]').val()) || 0;
        const non_billable_hours = parseFloat(row.element.find('input[data-fieldname="non_billable_hours"]').val()) || 0;
        const total_hours = parseFloat(row.element.find('td[data-fieldname="hours"]').text()) || 0;

        const calculated_total = billable_hours + non_billable_hours;
        if (Math.abs(calculated_total - total_hours) > 0.01) {
            invalid_rows.push(row);
        }
    });

    return invalid_rows;
}

function get_current_project(report) {
    // Get project from filters
    const filters = report.get_filter_values();
    return filters.project || null;
}

// Add CSS for better visual feedback
frappe.ready(function () {
    $('<style>')
        .prop('type', 'text/css')
        .html(`
            .table-warning {
                background-color: #fff3cd !important;
            }
            .table-danger {
                background-color: #f8d7da !important;
            }
            .is-invalid {
                border-color: #dc3545 !important;
            }
            .btn-group .btn {
                margin-right: 5px;
            }
        `)
        .appendTo('head');
});
