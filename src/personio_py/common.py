
class AbsenceEntitlement:

    def __init__(self):
        # TODO implement
        pass


class CostCenter:

    def __init__(self, id_: int, name: str, percentage: float):
        self.id_ = id_
        self.name = name
        self.percentage = percentage


class Department:

    def __init__(self, name: str):
        self.name = name


class HolidayCalendar:

    def __init__(self, id_: int, name: str, country: str, state: str):
        self.id_ = id_
        self.name = name
        self.country = country
        self.state = state


class Office:

    def __init__(self, name: str):
        self.name = name


class ShortEmployee:

    def __init__(self, id_: int, first_name: str, last_name: str, email: str):
        self.id_ = id_
        self.first_name = first_name
        self.last_name = last_name
        self.email = email


Supervisor = ShortEmployee


class Team:

    def __init__(self, id_: int, name: str):
        self.id_ = id_
        self.name = name


class WorkSchedule:

    def __init__(self, id_: int, name: str, monday: str, tuesday: str, wednesday: str,
                 thursday: str, friday: str, saturday: str, sunday: str):
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
