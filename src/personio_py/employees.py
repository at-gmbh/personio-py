import datetime
from typing import List

from personio_py.common import AbsenceEntitlement, CostCenter, Department, HolidayCalendar, \
    Office, ShortEmployee, Team, WorkSchedule


class Employee:

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
                 team: Team = None,
                 ):
        pass
