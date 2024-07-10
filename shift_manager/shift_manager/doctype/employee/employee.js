// Copyright (c) 2024, Verckys Orwa and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee", {
  validate(frm) {
    frappe.call({
      method: "shift_manager.services.rest.generate_employee_id",
      callback: function (r) {
        if (r.message) {
          frm.set_value("employee_id", r.message);
        }
      },
    });
  },
  
});
