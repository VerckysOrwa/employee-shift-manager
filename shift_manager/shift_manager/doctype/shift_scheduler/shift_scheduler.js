// Copyright (c) 2024, Verckys Orwa and contributors
// For license information, please see license.txt

frappe.ui.form.on("Shift Scheduler", {
  refresh(frm) {
    let today = frappe.datetime.get_today();
    frm.set_value("date", today);
    frm.add_custom_button(__("Batch Schedule"), function () {
      console.log("I have been Clicked");
    });
    // frm.set_df_property("date","read_only",1)
  },
  shift_name(frm) {
    frappe.db.get_doc("Shift", frm.doc.shift_name).then((doc) => {
      let { from_time, to_time } = doc;
      frm.set_value({
        from_time,
        to_time,
      });
    });
  },
});

frappe.ui.form.on("Employee Shift Table", {
  employee_id(frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);
    let id = row.employee_id;

    let duplicate = frm.doc.shifts.some(
      (item) => item.employee_id === id && item.name !== row.name
    );

    if (duplicate) {
      frm.refresh_field("shifts");
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
