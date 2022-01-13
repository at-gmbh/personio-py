"""
personio-py

a lightweight Personio API client
"""

__title__ = "personio-py"
__copyright__ = "© 2020-2022 Alexander Thamm GmbH"

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
)
from personio_py.client import Personio
