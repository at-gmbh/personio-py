import logging
import time
import unicodedata
from typing import Dict, List, Optional, TYPE_CHECKING

from personio_py import Employee

if TYPE_CHECKING:
    from personio_py import Personio

logger = logging.getLogger('personio_py')


class SearchCache:

    DEFAULT_CACHE_TIMEOUT = 6 * 60 * 60

    def __init__(self, client: 'Personio', cache_timeout: int = DEFAULT_CACHE_TIMEOUT):
        super().__init__()
        self.client = client
        self.cache_timeout = cache_timeout
        self.index: Optional[Dict[Employee, str]] = None
        self.last_update = 0.0
        self.valid = False

    def search(self, query: str, active_only=True) -> List[Employee]:
        # check if update is required
        if not self.index:
            logger.debug("creating search cache for the first time")
            self._update()
        elif not self.valid:
            logger.debug("updating search cache because it was invalidated")
            self._update()
        elif time.time() > self.last_update + self.cache_timeout:
            logger.debug(f"updating search cache because it has not been updated "
                         f"for more than {self.cache_timeout} seconds")
            self._update()

        # run the actual search
        query_norm = query.lower()
        query_tokens = [t.lower() for t in query.split()]
        full_match = []
        partial_match = []
        for employee, text in self.index.items():
            if active_only and employee.status == 'inactive':
                continue
            if query_norm in text:
                full_match.append(employee)
            else:
                for token in query_tokens:
                    if token in text:
                        partial_match.append(employee)
        return full_match + partial_match

    def search_first(self, query: str) -> Optional[Employee]:
        results = self.search(query)
        if results:
            return results[0]

    def invalidate(self):
        self.valid = False

    def _update(self):
        # get new list of employees & build index
        employees = self.client.get_employees()
        self.index = self._build_index(employees)
        self.last_update = time.time()
        self.valid = True

    @classmethod
    def _build_index(cls, employees: List[Employee]) -> Dict[Employee, str]:
        return {e: cls._get_keywords(e) for e in employees}

    @classmethod
    def _get_keywords(cls, e: Employee) -> str:
        keywords = [
            e.first_name,
            e.last_name,
            e.position,
            e.email,
            e.status,
            e.subcompany
        ]
        if e.office:
            keywords.append(e.office.name)
        if e.department:
            keywords.append(e.department.name)
        if e.team:
            keywords.append(e.team.name)
        keyword_string = ' '.join(t for t in keywords if t).lower()
        return keyword_string
