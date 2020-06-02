"""
personio-py

a lightweight Personio API client
"""

__title__ = "personio-py"
__copyright__ = "© 2020 Alexander Thamm GmbH"

from .version import __version__
from .errors import (
    PersonioError,
    MissingCredentialsError,
    PersonioApiError,
    UnsupportedMethodError,
)
from .mapping import (
    DynamicMapping
)
from .models import (
    Absence,
    AbsenceEntitlement,
    AbsenceType,
    Attendance,
    CostCenter,
    Department,
    DynamicAttr,
    Employee,
    HolidayCalendar,
    Office,
    ShortEmployee,
    Team,
    WorkSchedule,
)
from personio_py.client import Personio
