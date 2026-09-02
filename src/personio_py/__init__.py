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
from .models import (
    Absence,
    AbsenceBalance,
    AbsenceEntitlement,
    AbsenceType,
    Attendance,
    BaseEmployee,
    CostCenter,
    CustomAttribute,
    Department,
    Employee,
    HolidayCalendar,
    Office,
    PersonioResource,
    PersonioResourceType,
    Project,
    ShortEmployee,
    Team,
    WorkSchedule,
)
from .search import SearchIndex
from personio_py.client import Personio
