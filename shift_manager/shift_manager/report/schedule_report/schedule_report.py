# Copyright (c) 2024, Verckys Orwa and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.utils import cstr, get_url, nowdate, formatdate
from frappe.utils.csvutils import to_csv
import csv


def execute(filters=None):
    columns, data = [], []

    columns = [
        {
            "label": _("Employee ID"),
            "fieldname": "employee_id",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Employee Name"),
            "fieldname": "employee_name",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("Location"),
            "fieldname": "location",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("Date"),
            "fieldname": "date",
            "fieldtype": "Date",
            "width": 100
        },
        {
            "label": _("From Time"),
            "fieldname": "from_time",
            "fieldtype": "Time",
            "width": 100
        },
        {
            "label": _("To Time"),
            "fieldname": "to_time",
            "fieldtype": "Time",
            "width": 100
        },
        {
            "label": _("Department"),
            "fieldname": "department",
            "fieldtype": "Data",
            "width": 150
        }
    ]

    conditions = ""
    if filters:
        if filters.get("from_date"):
            conditions += " AND date >= %(from_date)s"
        if filters.get("to_date"):
            conditions += " AND date <= %(to_date)s"

    data = frappe.db.sql(f"""
        SELECT
            employee_id,
            employee_name,
            location,
            date,
            from_time,
            to_time,
            department
        FROM
            `tabEmployee Shift`
        WHERE
            1=1
            {conditions}
        ORDER BY date, employee_name
    """, filters, as_dict=True)

    return columns, data


@frappe.whitelist(allow_guest=True)
def export_to_csv(filters):
    columns, data = execute(frappe.parse_json(filters))

    csv_data = [['Employee ID', 'Employee Name', 'Location',
                 'Date', 'From Time', 'To Time', 'Department']]
    for row in data:
        csv_data.append([
            row.employee_id,
            row.employee_name,
            row.location,
            cstr(row.date),
            cstr(row.from_time),
            cstr(row.to_time),
            row.department
        ])

    return to_csv(csv_data)


@frappe.whitelist(allow_guest=True)
def send_report_email(filters, email_address):
    filters = frappe.parse_json(filters)
    columns, data = execute(filters)
    csv_data = export_to_csv(filters)

    subject = f"Schedule Report from {filters.get('from_date')} to {filters.get('to_date')}"
    message = f"Please find the schedule report for the period {filters.get('from_date')} to {filters.get('to_date')}."

    try:
        frappe.sendmail(
            recipients=[email_address],
            subject=subject,
            message=message,
            attachments=[{
                'fname': f'schedule_report_{filters.get("from_date")}_to_{filters.get("to_date")}.csv',
                'fcontent': csv_data
            }]
        )
        return True
    except Exception as e:
        frappe.log_error(f"Failed to send email: {str(e)}")
        return False


@frappe.whitelist(allow_guest=True)
def generate_daily_report():
    filters = {"date": nowdate()}
    columns, data = execute(filters)
    print(f"\n\n\n\nThis is a cron job test\n\n\n\n")

    csv_data = [['Employee ID', 'Employee Name', 'Location',
                 'Date', 'From Time', 'To Time', 'Department']]
    for row in data:
        csv_data.append([
            row.employee_id,
            row.employee_name,
            row.location,
            cstr(row.date),
            cstr(row.from_time),
            cstr(row.to_time),
            row.department
        ])

    file_path = '/tmp/employee_shift_daily_report.csv'

    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([d['label'] for d in columns])
        for row in data:
            writer.writerow([cstr(row[col['fieldname']])
                            for col in columns])

    subject = f"Daily Schedule Report for {formatdate(filters['date'])}"
    message = f"Please find attached the daily schedule report for {formatdate(filters['date'])}."

    try:
        frappe.sendmail(
            recipients=['verckysorwa@gmail.com'],
            subject=subject,
            message=message,
            attachments=[{
                'fname': f'daily_schedule_report_{filters["date"]}.csv',
                'fcontent': open(file_path, 'rb').read()
            }]
        )
        return True
    except Exception as e:
        frappe.log_error(f"Failed to send daily report email: {str(e)}")
        return False


def auto_mail_report():
    active_status = frappe.db.get_single_value(
        "Shift Report Settings", "activate")
    if active_status == 1:
        return generate_daily_report()
