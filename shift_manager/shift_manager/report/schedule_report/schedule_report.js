// Copyright (c) 2024, Verckys Orwa and contributors
// For license information, please see license.txt

frappe.query_reports["Schedule Report"] = {
  filters: [
    {
      fieldname: "from_date",
      label: __("From Date"),
      fieldtype: "Date",
      default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
      reqd: 1,
    },
    {
      fieldname: "to_date",
      label: __("To Date"),
      fieldtype: "Date",
      default: frappe.datetime.get_today(),
      reqd: 1,
    },
  ],
  onload: function (report) {
    report.page.add_inner_button(__("Export to CSV"), function () {
      let filters = report.get_values();
      frappe.call({
        method:
          "shift_manager.shift_manager.report.schedule_report.schedule_report.export_to_csv",
        args: {
          filters: filters,
        },
        callback: function (r) {
          if (r.message) {
            let csv_data = r.message;
            let blob = new Blob([csv_data], {
              type: "text/csv;charset=utf-8;",
            });
            let link = document.createElement("a");
            if (link.download !== undefined) {
              let url = URL.createObjectURL(blob);
              link.setAttribute("href", url);
              link.setAttribute(
                "download",
                `schedule_report_${filters.from_date}_to_${filters.to_date}.csv`
              );
              link.style.visibility = "hidden";
              document.body.appendChild(link);
              link.click();
              document.body.removeChild(link);
            }
          }
        },
      });
    });

    report.page.add_inner_button(__("Send Email"), function () {
      let filters = report.get_values();
      let d = new frappe.ui.Dialog({
        title: "Send Report Email",
        fields: [
          {
            label: "Email Address",
            fieldname: "email_address",
            fieldtype: "Data",
            options: "Email",
            reqd: 1,
          },
        ],
        primary_action_label: "Send",
        primary_action(values) {
          frappe.call({
            method:
              "shift_manager.shift_manager.report.schedule_report.schedule_report.send_report_email",
            args: {
              filters: filters,
              email_address: values.email_address,
            },
            callback: function (r) {
              if (r.message) {
                frappe.show_alert({
                  message: __("Email sent successfully"),
                  indicator: "green",
                });
              } else {
                frappe.throw(
                  __("Failed to send email. Please check the error logs.")
                );
              }
            },
          });
          d.hide();
        },
      });
      d.show();
    });
  },
};
