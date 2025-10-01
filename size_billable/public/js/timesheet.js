frappe.ui.form.on("Timesheet", {
    refresh: function (frm) {
        // Add custom button for manager approval
        if (frm.doc.status === "Submitted" && frm.doc.parent_project) {
            frappe.call({
                method: "size_billable.api.project.get_project_manager",
                args: { "project": frm.doc.parent_project },
                callback: function (r) {
                    if (r.message === frappe.session.user) {
                        frm.add_custom_button(__("Approve Entries"), function () {
                            frappe.route_options = { "project": frm.doc.parent_project };
                            frappe.set_route("Report", "Timesheet Approval Report");
                        }, __("Size Billable"));
                    }
                }
            });
        }

        // Add approval status summary
        if (frm.doc.status === "Submitted") {
            frm.add_custom_button(__("Approval Status"), function () {
                show_approval_status(frm.doc);
            }, __("Size Billable"));
        }
    }
});

frappe.ui.form.on("Timesheet Detail", {
    hours: function (frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (row.hours && row.billable_hours === undefined) {
            row.billable_hours = 0;
            row.non_billable_hours = row.hours;
            frm.refresh_field("time_logs");
        }
    },

    billable_hours: function (frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (row.hours && row.billable_hours !== undefined) {
            row.non_billable_hours = row.hours - row.billable_hours;
            frm.refresh_field("time_logs");
        }
    }
});

function show_approval_status(timesheet) {
    frappe.call({
        method: "size_billable.api.timesheet.get_timesheet_approval_status",
        args: { "timesheet_name": timesheet.name },
        callback: function (r) {
            if (r.message) {
                const summary = r.message;
                const dialog = new frappe.ui.Dialog({
                    title: __("Timesheet Approval Status"),
                    size: "large",
                    fields: [
                        {
                            fieldtype: "HTML",
                            fieldname: "status_container"
                        }
                    ]
                });

                dialog.show();

                const statusContainer = dialog.fields_dict.status_container.$wrapper;
                statusContainer.html(`
                    <div class="row mb-3">
                        <div class="col-md-3">
                            <div class="card text-center">
                                <div class="card-body">
                                    <h4 class="text-primary">${summary.total_entries}</h4>
                                    <small class="text-muted">Total Entries</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card text-center">
                                <div class="card-body">
                                    <h4 class="text-warning">${summary.pending_entries}</h4>
                                    <small class="text-muted">Pending</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card text-center">
                                <div class="card-body">
                                    <h4 class="text-success">${summary.approved_entries}</h4>
                                    <small class="text-muted">Approved</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card text-center">
                                <div class="card-body">
                                    <h4 class="text-danger">${summary.rejected_entries}</h4>
                                    <small class="text-muted">Rejected</small>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>Project</th>
                                    <th>Task</th>
                                    <th>Activity</th>
                                    <th>Hours</th>
                                    <th>Billable</th>
                                    <th>Status</th>
                                    <th>Approved By</th>
                                    <th>Approved On</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${summary.entries.map(entry => `
                                    <tr>
                                        <td>${entry.project}</td>
                                        <td>${entry.task || '-'}</td>
                                        <td>${entry.activity_type || '-'}</td>
                                        <td>${entry.hours}</td>
                                        <td>${entry.billable_hours}</td>
                                        <td>
                                            <span class="badge ${getStatusBadgeClass(entry.approval_status)}">
                                                ${entry.approval_status}
                                            </span>
                                        </td>
                                        <td>${entry.approved_by || '-'}</td>
                                        <td>${entry.approved_on ? frappe.datetime.str_to_user(entry.approved_on) : '-'}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                `);
            }
        }
    });
}

function getStatusBadgeClass(status) {
    switch (status) {
        case "Approved": return "bg-success";
        case "Pending": return "bg-warning";
        case "Rejected": return "bg-danger";
        default: return "bg-secondary";
    }
}

