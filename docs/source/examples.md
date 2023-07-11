# Examples

First of all to get started, create a personio client instance:

```
from personio_py import Personio
p = Personio(client_id='***', client_secret='***')
```

## Employee

You can get a list of all employees:

    p.get_employees()

Or you can get a specific employee with the specified ID:

    p.get_employee(employee_id)

You can get the employee's picture using the employee ID or employee instance:

    p.get_employee_picture(employee_id)

OR

    p.get_employee_picture(employee)

To create a new employee:

    tim = Employee(first_name='John',
                   last_name='Dou',
                   gender='male',
                   position='developer',
                   subcompany='ACME',
                   department='IT',
                   office='Madrid',
                   email='john.dou@demo.com',
                   hire_date=datetime(1989, 3, 12),
                   weekly_working_hours=40,
                   status='active',
                   supervisor_id=5)
    p.create_employee(tim)

Different fields of an employee can be updated as following:

    tim.position='team lead'
    tim.weekly_working_hours = '30'
    tim.update()

The absence balance for the specified employee is retrieved with:

    p.get_absence_balance(tim)


## Absence

The library supports retrieving a list of all absence records for an employee or a list of
employees by providing either the employee object or employee id:

    p.get_absences(tim)

An absence record can be created from an Absence object using the personio client
or directly from the absence object. Before creating an absence, make sure about
the type absence you want to create.

    abselnce_types = p.get_absence_types()

    absence = Absence(
        start_date=date(year=2022, month=1, day=1),
        end_date=date(year=2022, month=1, day=10),
        time_off_type=AbsenceType(),
        employee=tim,
        half_day_start=True,
        half_day_end=False,
        )
    p.create_absence(absence)
    absence.create()

Similarly, the absence can be deleted:

    p.delete_absence(absence_id or Absence object)
    absence.delete()

The details of an absent employee can be retrieved from an absence record:

    absence.get_employee()


## Attendance

You can fetch attendance data for company employees. This is how to get all the attendances of an employee:

    attendances = p.get_attendances(employee)

To create a new attendance for an employee:

    Attendance(employee=employee_id,
               date=datetime(2021, 1, 1),
               start_time="08:00",
               end_time="17:00",
               break_duration=30,
               comment=comment).create()

For a given attendance you can check the attendee employee with:

    attendance.get_employee()

To delete an attendance with the help of the client or from the instance:

    p.delete_attendance(attendance.id or attendance)
    attendance.delete()

## Project

A list of all the companie's projects can be retrieved:

    p.get_projects()

A project can be created, updated or deleted as follow:

    new_project = Project(name="Initial Project", active=True)
    p.create_project(new_project)

    new_project.name = "updated project"
    updated_project = new_project.update()

    new_project.delete()
