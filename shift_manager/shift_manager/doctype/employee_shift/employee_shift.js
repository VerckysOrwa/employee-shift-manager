// Copyright (c) 2024, Verckys Orwa and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Shift", {
  refresh(frm) {
    let today = frappe.datetime.get_today();
    frm.set_value("date", today);
  },
  shift(frm) {
    let shiftName = frm.doc.shift;
    frappe.db.get_doc("Shift", shiftName).then((doc) => {
      let { from_time, to_time } = doc;
      frm.set_value({
        from_time,
        to_time,
      });
    });
  },
  employee_id(frm) {
    let employeeId = frm.doc.employee_id;
    frappe.db.get_doc("Employee", employeeId).then((doc) => {
      let { full_name, department } = doc;
      frm.set_value({
        employee_name: full_name,
        department,
      });
    });
  },

  validate(frm) {
    let shiftName = frm.doc.shift;
    frappe.call({
      method: "shift_manager.services.rest.generate_shift_id",
      args: {
        shift: shiftName,
      },
      callback: function (r) {
        if (r.message) {
          frm.set_value("shift_id", r.message);
          frm.set_df_property("is_batch", "read_only", 1);
        }
      },
    });
  },
});

frappe.ui.form.on("Employee Shift Table", {
  employee_id(frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);
    let id = row.employee_id;

    let duplicate = frm.doc.batch.some(
      (item) => item.employee_id === id && item.name !== row.name
    );

    if (duplicate) {
      frm.refresh_field("batch");
      setTimeout(
        () =>
          frappe.throw(__("Selected employee ID already exists in the table ")),
        1000
      );
      frappe.model.set_value(cdt, cdn, "employee_id", "");
      return;
    }

    frappe.db.get_doc("Employee", id).then((doc) => {
      console.log(doc);
      let { full_name, department } = doc;
      // console.log(full_name,department);
      frappe.model.set_value(cdt, cdn, {
        employee_name: full_name,
        department,
      });
    });
  },
});
