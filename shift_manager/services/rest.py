import frappe
from frappe import _
from datetime import datetime, timedelta
import random
import string


@frappe.whitelist(allow_guest=True)
def generate_employee_id():
    last_id = frappe.db.get_value(
        'Employee', {}, 'employee_id', order_by='creation DESC')

    if last_id:
        last_num = int(last_id.split('-')[-1])
        new_num = last_num + 1
    else:
        new_num = 1
    new_id = f'SH-EMP-{new_num:03d}'
    return new_id


@frappe.whitelist()
def schedule_employee_shift_batch(employees, from_date, to_date, shift):

    if isinstance(employees, str):
        employees = frappe.parse_json(employees)

    from_date = datetime.strptime(from_date, '%Y-%m-%d')
    to_date = datetime.strptime(to_date, '%Y-%m-%d')

    for employee in employees:
        current_date = from_date
        while current_date <= to_date:
            employee_shift = frappe.new_doc("Employee Shift")
            employee_shift.employee = employee
            employee_shift.date = current_date.strftime('%Y-%m-%d')
            employee_shift.shift_type = shift
            employee_shift.insert()

            current_date += timedelta(days=1)

    frappe.db.commit()
    return True


@frappe.whitelist(allow_guest=True)
def generate_shift_id(shift):
    now = datetime.now()
    year = now.year
    month = now.month

    random_string = ''.join(random.choices(
        string.ascii_uppercase + string.digits, k=5))

    shift_id = f'{shift}-{year}-{month:02d}-{random_string}'

    while frappe.db.exists("Employee Shift", {"shift_id": shift_id}):
        random_string = ''.join(random.choices(
            string.ascii_uppercase + string.digits, k=5))
        shift_id = f'{shift}-{year}-{month:02d}-{random_string}'

    return shift_id
