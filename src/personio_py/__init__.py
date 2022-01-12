"""
personio-py

a lightweight Personio API client
"""

__title__ = "personio-py"
__copyright__ = "© 2020-2022 Alexander Thamm GmbH"

from personio_py.client import Personio
from .errors import (
    MissingCredentialsError,
    PersonioApiError,
    PersonioError,
    UnsupportedMethodError
)
from .models import (
    Absence,
    AbsenceEntitlement,
    AbsenceType,
    Attendance,
    CostCenter,
    CustomAttribute,
    Department,
    Employee,
    HolidayCalendar,
    Office,
    ShortEmployee,
    Team,
    WorkSchedule,
)
from .version import __version__
