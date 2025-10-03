frappe.ui.form.on("Project", {
    refresh: function (frm) {
        // Add custom buttons based on billing type
        if (frm.doc.billing_type === "Hourly Billing") {
            frm.add_custom_button(__("Hour Consumption Chart"), function () {
                show_hour_consumption_chart(frm.doc);
            }, __("Size Billable"));

            frm.add_custom_button(__("Billing Summary"), function () {
                show_billing_summary(frm.doc);
            }, __("Size Billable"));
        }

        // Add button to open timesheet approval report
        if (frm.doc.project_manager_user === frappe.session.user) {
            frm.add_custom_button(__("Approve Timesheets"), function () {
                frappe.route_options = { "project": frm.doc.name };
                frappe.set_route("Report", "Timesheet Approval Report");
            }, __("Size Billable"));
        }

        // Add customer portal link
        if (frm.doc.customer) {
            frm.add_custom_button(__("Customer Portal"), function () {
                window.open("/customer-portal", "_blank");
            }, __("Size Billable"));
        }
    },

    billing_type: function (frm) {
        // Reset hour-related fields when changing billing type
        if (frm.doc.billing_type === "Fixed Cost") {
            frm.set_value("total_purchased_hours", 0);
            frm.set_value("hourly_rate", 0);
            frm.set_value("total_consumed_hours", 0);
        }
    },

    total_purchased_hours: function (frm) {
        // Validate purchased hours
        if (frm.doc.billing_type === "Hourly Billing" && frm.doc.total_purchased_hours <= 0) {
            frappe.msgprint(__("Total Purchased Hours must be greater than 0 for Hourly Billing projects"));
        }
    }
});

function show_hour_consumption_chart(project) {
    const dialog = new frappe.ui.Dialog({
        title: __("Hour Consumption Chart"),
        size: "large",
        fields: [
            {
                fieldtype: "HTML",
                fieldname: "chart_container"
            }
        ]
    });

    dialog.show();

    // Load chart data
    frappe.call({
        method: "size_billable.api.project.get_project_billing_summary",
        args: { "project_name": project.name },
        callback: function (r) {
            if (r.message) {
                const data = r.message;
                const chartContainer = dialog.fields_dict.chart_container.$wrapper;

                chartContainer.html(`
                    <div class="row">
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    <h6>Hour Consumption Progress</h6>
                                </div>
                                <div class="card-body">
                                    <div class="progress mb-3" style="height: 30px;">
                                        <div class="progress-bar ${getProgressBarClass(data.consumption_percentage)}" 
                                             style="width: ${data.consumption_percentage}%">
                                            ${data.total_consumed_hours} / ${data.total_purchased_hours} hours
                                        </div>
                                    </div>
                                    <div class="row text-center">
                                        <div class="col-4">
                                            <h4 class="text-primary">${data.total_purchased_hours}</h4>
                                            <small class="text-muted">Purchased</small>
                                        </div>
                                        <div class="col-4">
                                            <h4 class="text-success">${data.total_consumed_hours}</h4>
                                            <small class="text-muted">Consumed</small>
                                        </div>
                                        <div class="col-4">
                                            <h4 class="text-info">${data.remaining_hours}</h4>
                                            <small class="text-muted">Remaining</small>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    <h6>Billing Summary</h6>
                                </div>
                                <div class="card-body">
                                    <table class="table table-sm">
                                        <tr>
                                            <td>Hourly Rate:</td>
                                            <td><strong>${format_currency(data.hourly_rate)}</strong></td>
                                        </tr>
                                        <tr>
                                            <td>Total Billable Amount:</td>
                                            <td><strong>${format_currency(data.total_billable_amount)}</strong></td>
                                        </tr>
                                        <tr>
                                            <td>Consumption %:</td>
                                            <td><strong>${data.consumption_percentage.toFixed(1)}%</strong></td>
                                        </tr>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                `);
            }
        }
    });
}

function show_billing_summary(project) {
    frappe.route_options = { "project": project.name };
    frappe.set_route("Report", "Project Billing Summary");
}

function getProgressBarClass(percentage) {
    if (percentage >= 90) return "bg-danger";
    if (percentage >= 75) return "bg-warning";
    return "bg-success";
}

function format_currency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}




