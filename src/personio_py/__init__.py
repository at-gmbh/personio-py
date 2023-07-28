"""
personio-py

a lightweight Personio API client
"""

__title__ = "personio-py"
__copyright__ = "© 2020-2023 Alexander Thamm GmbH"

from .client import Personio
from .errors import MissingCredentialsError, PersonioApiError, PersonioError, UnsupportedMethodError
from .models import Absence, AbsenceBalance, AbsenceEntitlement, AbsenceType, Attendance, \
    BaseEmployee, CostCenter, CustomAttribute, Department, Employee, HolidayCalendar, Office, \
    PersonioResource, PersonioResourceType, Project, ShortEmployee, Team, WorkSchedule, \
    update_model
from .search import SearchIndex
from .version import __version__
