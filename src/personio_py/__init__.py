"""
personio-py

a lightweight Personio API client
"""

__title__ = "personio-py"
__copyright__ = "© 2020 Alexander Thamm GmbH"

from personio_py.client import Personio
from .errors import (MissingCredentialsError, PersonioApiError, PersonioError,
                     UnsupportedMethodError)
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
    Employee,
    HolidayCalendar,
    Office,
    ShortEmployee,
    Team,
    WorkSchedule,
)
from .version import __version__
