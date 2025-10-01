/**
 * Manager Approval Report - Interactive Client Script
 * 
 * This script provides interactive functionality for the Manager Approval Report,
 * enabling SB Project Managers to efficiently manage timesheet approvals through
 * a user-friendly interface with bulk operations and dynamic hour adjustments.
 * 
 * Key Features:
 * - Multi-select functionality for bulk operations
 * - Dynamic hour adjustment with total preservation
 * - Real-time validation and feedback
 * - Bulk approve/reject operations
 * - Save changes functionality
 * - Data refresh capabilities
 * 
 * Security:
 * - Project filtering restricted to manager's assigned projects
 * - Employee filtering limited to active employees
 * - All operations validated server-side
 */

frappe.query_reports["Manager Approval Report"] = {
    "filters": [
        {
            "fieldname": "project",
            "label": __("Project"),
            "fieldtype": "Link",
            "options": "Project",
            "get_query": function () {
                return {
                    "filters": {
                        "project_manager_user": frappe.session.user,
                        "status": ["!=", "Cancelled"]
                    }
                };
            }
        },
        {
            "fieldname": "employee",
            "label": __("Employee"),
            "fieldtype": "Link",
            "options": "Employee",
            "get_query": function () {
                return {
                    "filters": {
                        "status": "Active"
                    }
                };
            }
        },
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_days(frappe.datetime.get_today(), -30)
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today()
        },
        {
            "fieldname": "approval_status",
            "label": __("Approval Status"),
            "fieldtype": "Select",
            "options": ["", "Pending", "Approved", "Rejected"],
            "default": ""
        }
    ],

    "formatter": function (value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        // Highlight editable cells
        if (column.fieldname === "billable_hours" || column.fieldname === "non_billable_hours") {
            if (data.can_edit) {
                value = `<div class="editable-cell" data-field="${column.fieldname}" data-row="${row}">${value}</div>`;
            }
        }

        // Color code status
        if (column.fieldname === "approval_status") {
            if (data.is_approved) {
                value = `<span class="badge badge-success">${value}</span>`;
            } else if (data.is_pending) {
                value = `<span class="badge badge-warning">${value}</span>`;
            } else if (data.is_rejected) {
                value = `<span class="badge badge-danger">${value}</span>`;
            }
        }

        return value;
    },

    "onload": function (report) {
        // Add custom buttons
        add_custom_buttons(report);

        // Add event listeners
        setup_event_listeners(report);

        // Initialize hour adjustment functionality
        initialize_hour_adjustment(report);
    },

    "after_datatable_render": function (report) {
        // Make cells editable after table renders
        make_cells_editable(report);
    }
};

function add_custom_buttons(report) {
    // Create button container
    const button_container = $(`
        <div class="manager-approval-buttons" style="margin-bottom: 15px;">
            <button class="btn btn-primary btn-sm" id="approve-selected">
                <i class="fa fa-check"></i> Approve Selected
            </button>
            <button class="btn btn-warning btn-sm" id="reject-selected">
                <i class="fa fa-times"></i> Reject Selected
            </button>
            <button class="btn btn-success btn-sm" id="save-changes">
                <i class="fa fa-save"></i> Save Changes
            </button>
            <button class="btn btn-info btn-sm" id="refresh-data">
                <i class="fa fa-refresh"></i> Refresh Data
            </button>
            <span class="text-muted" id="selection-count" style="margin-left: 15px;"></span>
        </div>
    `);

    // Insert buttons before the report
    report.$wrapper.find('.report-content').prepend(button_container);
}

function setup_event_listeners(report) {
    // Approve selected entries
    report.$wrapper.find('#approve-selected').on('click', function () {
        approve_selected_entries(report);
    });

    // Reject selected entries
    report.$wrapper.find('#reject-selected').on('click', function () {
        reject_selected_entries(report);
    });

    // Save hour changes
    report.$wrapper.find('#save-changes').on('click', function () {
        save_hour_changes(report);
    });

    // Refresh data
    report.$wrapper.find('#refresh-data').on('click', function () {
        report.refresh();
    });

    // Update selection count when checkboxes change
    report.$wrapper.on('change', 'input[type="checkbox"]', function () {
        update_selection_count(report);
    });
}

function initialize_hour_adjustment(report) {
    // Add CSS for editable cells
    const style = `
        <style>
            .editable-cell {
                cursor: pointer;
                border: 1px solid transparent;
                padding: 2px 4px;
                border-radius: 3px;
            }
            .editable-cell:hover {
                background-color: #f8f9fa;
                border-color: #007bff;
            }
            .editable-cell.editing {
                background-color: #fff3cd;
                border-color: #ffc107;
            }
            .hour-changed {
                background-color: #d4edda !important;
                border-color: #28a745 !important;
            }
            .manager-approval-buttons {
                padding: 10px;
                background-color: #f8f9fa;
                border-radius: 5px;
                border: 1px solid #dee2e6;
            }
        </style>
    `;
    $('head').append(style);
}

function make_cells_editable(report) {
    report.$wrapper.find('.editable-cell').each(function () {
        const $cell = $(this);
        const field = $cell.data('field');
        const row = $cell.data('row');

        $cell.on('click', function () {
            if ($cell.hasClass('editing')) return;

            const currentValue = parseFloat($cell.text()) || 0;
            const $input = $(`<input type="number" step="0.01" min="0" value="${currentValue}" class="form-control form-control-sm">`);

            $cell.addClass('editing').html($input);
            $input.focus().select();

            $input.on('blur keypress', function (e) {
                if (e.type === 'keypress' && e.which !== 13) return;

                const newValue = parseFloat($input.val()) || 0;
                const totalHours = parseFloat($cell.closest('tr').find('[data-field="total_hours"]').text()) || 0;

                // Update the cell
                $cell.removeClass('editing').text(newValue.toFixed(2));

                // Adjust the other hour field
                adjust_other_hour_field($cell, field, newValue, totalHours);

                // Mark as changed
                $cell.addClass('hour-changed');
                $cell.closest('tr').addClass('row-changed');
            });
        });
    });
}

function adjust_other_hour_field($currentCell, currentField, newValue, totalHours) {
    const $row = $currentCell.closest('tr');
    const otherField = currentField === 'billable_hours' ? 'non_billable_hours' : 'billable_hours';
    const $otherCell = $row.find(`[data-field="${otherField}"]`);

    if ($otherCell.length) {
        const otherValue = totalHours - newValue;
        $otherCell.text(otherValue.toFixed(2));
        $otherCell.addClass('hour-changed');
    }
}

function update_selection_count(report) {
    const selectedCount = report.$wrapper.find('input[type="checkbox"]:checked').length;
    const $countSpan = report.$wrapper.find('#selection-count');

    if (selectedCount > 0) {
        $countSpan.text(`${selectedCount} entries selected`).removeClass('text-muted').addClass('text-primary');
    } else {
        $countSpan.text('').addClass('text-muted').removeClass('text-primary');
    }
}

function approve_selected_entries(report) {
    const selectedEntries = get_selected_entries(report);

    if (selectedEntries.length === 0) {
        frappe.msgprint(__('Please select entries to approve.'));
        return;
    }

    frappe.confirm(
        __('Are you sure you want to approve {0} selected entries?', [selectedEntries.length]),
        function () {
            frappe.call({
                method: 'size_billable.api.timesheet_approval.approve_entries',
                args: {
                    entries: selectedEntries
                },
                callback: function (r) {
                    if (r.message) {
                        frappe.msgprint(__('Successfully approved {0} entries.', [selectedEntries.length]));
                        report.refresh();
                    }
                }
            });
        }
    );
}

function reject_selected_entries(report) {
    const selectedEntries = get_selected_entries(report);

    if (selectedEntries.length === 0) {
        frappe.msgprint(__('Please select entries to reject.'));
        return;
    }

    frappe.confirm(
        __('Are you sure you want to reject {0} selected entries?', [selectedEntries.length]),
        function () {
            frappe.call({
                method: 'size_billable.api.timesheet_approval.reject_entries',
                args: {
                    entries: selectedEntries
                },
                callback: function (r) {
                    if (r.message) {
                        frappe.msgprint(__('Successfully rejected {0} entries.', [selectedEntries.length]));
                        report.refresh();
                    }
                }
            });
        }
    );
}

function save_hour_changes(report) {
    const changedEntries = get_changed_entries(report);

    if (changedEntries.length === 0) {
        frappe.msgprint(__('No changes to save.'));
        return;
    }

    frappe.call({
        method: 'size_billable.api.timesheet_approval.save_hour_changes',
        args: {
            entries: changedEntries
        },
        callback: function (r) {
            if (r.message) {
                frappe.msgprint(__('Successfully saved changes for {0} entries.', [changedEntries.length]));
                report.refresh();
            }
        }
    });
}

function get_selected_entries(report) {
    const entries = [];

    report.$wrapper.find('input[type="checkbox"]:checked').each(function () {
        const $checkbox = $(this);
        const $row = $checkbox.closest('tr');
        const timesheetDetailId = $row.find('[data-field="timesheet_detail_id"]').text();

        if (timesheetDetailId) {
            entries.push(timesheetDetailId);
        }
    });

    return entries;
}

function get_changed_entries(report) {
    const entries = [];

    report.$wrapper.find('.row-changed').each(function () {
        const $row = $(this);
        const timesheetDetailId = $row.find('[data-field="timesheet_detail_id"]').text();
        const billableHours = parseFloat($row.find('[data-field="billable_hours"]').text()) || 0;
        const nonBillableHours = parseFloat($row.find('[data-field="non_billable_hours"]').text()) || 0;

        if (timesheetDetailId) {
            entries.push({
                timesheet_detail_id: timesheetDetailId,
                billable_hours: billableHours,
                non_billable_hours: nonBillableHours
            });
        }
    });

    return entries;
}
