"""
personio-py

a lightweight Personio API client
"""

__title__ = "personio-py"
__copyright__ = "© 2020-2023 Alexander Thamm GmbH"

from .version import __version__
from .errors import (
    MissingCredentialsError,
    PersonioApiError,
    PersonioError,
    UnsupportedMethodError
)
from .models import (
    update_model,
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
    ShortEmployee,
    Team,
    WorkSchedule,
    Project
)
from .search import SearchIndex
from .client import Personio
