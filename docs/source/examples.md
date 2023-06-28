# Examples

🚧 this page is still a work in progress 🚧

If you'd like to make a contribution, please join the project [on GitHub](https://github.com/at-gmbh/personio-py)

First of all you need to create a personio client instance:

```
from personio_py import Personio
p = Personio(client_id='***', client_secret='***')
```

You can get a list of all employees with:

    p.get_employees()

Or you can get a specific employee with the specified ID:

    p.get_employee(employee_id)

You can get the employees picture from wither the employee ID or employee instance:

    p.get_employee_picture(employee_id)
OR

    p.get_employee_picture(employee)

You can create a new employee with:

    tim = Employee(
        first_name='John',
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
        supervisor_id=5,
        )
    p.create_employee(tim)

Different fields of an employee can be updated as following:

    tim.position='team lead'
    tim.weekly_working_hours = '30'
    tim.update()

The absence balance for the specified employee is retrieved with:

    p.get_absence_balance(tim)


# Absence

You can retrienve a list of all absence records for an employee or a list of employees by
providing either the employee object or employee id:

    p.get_absences(tim)

An absence record can be created from an Absence object using the personio client 
or directly from the absence object:

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

Similarly the absence can be deleted:

    p.delete_absence(absence_id or Absence object)
    absence.delete()

The details of an absent employee can be retrieved from an absence record:

    absence.get_employee()


