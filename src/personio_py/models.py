from datetime import datetime
from typing import List


class PersonioResource:

    def __init__(self):
        # TODO how to get the client reference to do updates & stuff? 🤔
        pass


class WritablePersonioResource(PersonioResource):

    can_create = True
    can_update = True
    can_delete = True

    def __init__(self):
        super().__init__()

    def create(self):
        # TODO make a request to create this resource
        pass

    def update(self):
        # TODO make a request to update this resource
        pass

    def delete(self):
        # TODO make a request to update this resource
        pass


class AbsenceEntitlement(PersonioResource):

    def __init__(self):
        super().__init__()
        # TODO implement


class AbsenceType(PersonioResource):

    def __init__(self, id_: int, name: str):
        super().__init__()


class CostCenter(PersonioResource):

    def __init__(self, id_: int, name: str, percentage: float):
        super().__init__()
        self.id_ = id_
        self.name = name
        self.percentage = percentage


class Department(PersonioResource):

    def __init__(self, name: str):
        super().__init__()
        self.name = name


class HolidayCalendar(PersonioResource):

    def __init__(self, id_: int, name: str, country: str, state: str):
        super().__init__()
        self.id_ = id_
        self.name = name
        self.country = country
        self.state = state


class Office(PersonioResource):

    def __init__(self, name: str):
        super().__init__()
        self.name = name


class ShortEmployee(PersonioResource):

    def __init__(self, id_: int, first_name: str, last_name: str, email: str):
        super().__init__()
        self.id_ = id_
        self.first_name = first_name
        self.last_name = last_name
        self.email = email

    def resolve(self):
        # TODO get full employee
        pass


class Team(PersonioResource):

    def __init__(self, id_: int, name: str):
        super().__init__()
        self.id_ = id_
        self.name = name


class WorkSchedule(PersonioResource):

    def __init__(self, id_: int, name: str, monday: str, tuesday: str, wednesday: str,
                 thursday: str, friday: str, saturday: str, sunday: str):
        super().__init__()
        self.id_ = id_
        self.name = name
        # pattern: ^\d\d:\d\d$
        self.monday = monday
        self.tuesday = tuesday
        self.wednesday = wednesday
        self.thursday = thursday
        self.friday = friday
        self.saturday = saturday
        self.sunday = sunday


class Absence(WritablePersonioResource):

    def __init__(self,
                 id_: int,
                 status: str,
                 comment: str,
                 start_date: datetime,
                 end_date: datetime,
                 days_count: float,
                 half_day_start: float,
                 half_day_end: float,
                 time_off_type: List[AbsenceType],
                 employee: ShortEmployee,
                 certificate: str,
                 created_at: datetime):
        super().__init__()


class Attendance(WritablePersonioResource):

    def __init__(self,
                 employee_id: int,
                 date: datetime,
                 start_time: str,
                 end_time: str,
                 break_duration: int,
                 comment: str = None,
                 is_holiday=False,
                 is_on_time_off=False):
        super().__init__()


class Employee(WritablePersonioResource):

    can_delete = False

    def __init__(self,
                 id_: int,
                 first_name: str,
                 last_name: str,
                 email: str,
                 gender: str,
                 status: str,
                 position: str,
                 supervisor: ShortEmployee,
                 employment_type: str,
                 weekly_working_hours: str,
                 hire_date: datetime,
                 contract_end_date: datetime = None,
                 termination_date: datetime = None,
                 termination_type: str = None,
                 termination_reason: str = None,
                 probation_period_end: datetime = None,
                 created_at: datetime = None,
                 last_modified_at: datetime = None,
                 office: Office = None,
                 department: Department = None,
                 cost_centers: List[CostCenter] = None,
                 fix_salary: float = None,
                 hourly_salary: float = None,
                 vacation_day_balance: float = None,
                 last_working_day: datetime = None,
                 holiday_calendar: HolidayCalendar = None,
                 work_schedule: WorkSchedule = None,
                 absence_entitlement: AbsenceEntitlement = None,
                 profile_picture: str = None,
                 team: Team = None):
        super().__init__()
        pass

    def picture(self) -> bytes:
        # TODO request from api & cache
        pass
