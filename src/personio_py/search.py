import logging
import time
from typing import Dict, List, Optional, TYPE_CHECKING

from personio_py import Employee

if TYPE_CHECKING:
    from personio_py import Personio

logger = logging.getLogger('personio_py')


class SearchIndex:
    """
    The search index is an implementation of a basic local search function for employees
    that was created because the Personio API lacks a native search function.

    This means that data for all employees will be downloaded from the API and indexed in memory
    before a search can be executed. On subsequent searches, the index will be reused and no more
    data is requested until the index is invalidated or becomes too old.

    To search for an employee, create an instance of the search index and submit a search query:

        index = SearchIndex(personio)
        results = index.search("Smith")

    The index requires a `Personio` client instance to request the list of employees from the API.
    Then we can search for all employees with the name "Smith".

    On the next search, no data will be requested from the API and the search will be a lot faster:

        whatshisname = index.search("john jim james")

    In the result list, we prefer exact matches, but each employee that has at least one token
    match will become part of the results. Also note that queries are case-insensitive.

    If we know exactly who we want and we're fairly certain that there is only one employee with
    that name, we can use `search_first` to get that employee directly

        zack = index.search("zacharias smith")

    If you made some changes or know that something must have changed on the server side, you can
    invalidate the index and make sure that the next search will happen on a fresh index:

        index.invalidate()

    Before the next search, the full list of employees will be requested from the API again and
    the search index will be rebuilt.

    :param client: the Personio API client (to request employee data)
    :param index_timeout: when the
    """

    DEFAULT_INDEX_TIMEOUT = 6 * 60 * 60
    """the default timeout for the search index (6 hours)"""

    def __init__(self, client: 'Personio', index_timeout: int = DEFAULT_INDEX_TIMEOUT):
        super().__init__()
        self.client = client
        self.index_timeout = index_timeout
        self.index: Optional[Dict[Employee, str]] = None
        self.last_update = 0.0
        self.valid = False

    def search(self, query: str, active_only=True) -> List[Employee]:
        """
        Execute a search on the search index.

        If the index does not exist, or has been invalidated or is expired, the full list
        of employees will be requested from the API.

        During the search we perform a case insensitive match on the keywords in the search index.
        All tokens of the query will be matched individually. Tokens are separated by whitespace.
        A full match (i.e. all tokens match the keywords in order) is preferred over
        a partial match (only one or more tokens match).

        :param query: the query string
        :param active_only: exclude inactive employees from the results (default: yes)
        :return: the list of employees that matches the search query
        """
        # update the search index if necessary
        self._update_on_demand()
        # prepare data
        query_norm = query.lower()
        query_tokens = [t.lower() for t in query.split()]
        full_match = []
        partial_match = []
        # run the actual search
        for employee, text in self.index.items():
            if active_only and employee.status == 'inactive':
                continue
            if query_norm in text:
                full_match.append(employee)
            else:
                for token in query_tokens:
                    if token in text:
                        partial_match.append(employee)
        # full matches first, then partial matches
        return full_match + partial_match

    def search_first(self, query: str, active_only=True) -> Optional[Employee]:
        """
        Execute a search on the search index and return the first result (if there is one) or None.

        This is basically the "I'm Feeling Lucky" button.
        For details about the search function, please refer to :func:`search`.

        :param query: the query string
        :param active_only: exclude inactive employees from the results (default: yes)
        :return: the first search result or None, if there were no results
        """
        results = self.search(query, active_only=active_only)
        if results:
            return results[0]

    def invalidate(self):
        """
        Invalidates the search index. New data will be requested on the next search.
        """
        self.valid = False

    def _update_on_demand(self):
        """
        Checks if an update is required and updates the index with new data from the API,
        if this is the case.
        """
        if not self.index:
            logger.debug("creating search index for the first time")
            self._update()
        elif not self.valid:
            logger.debug("updating search index because it was invalidated")
            self._update()
        elif time.time() > self.last_update + self.index_timeout:
            logger.debug(f"updating search index because it has not been updated "
                         f"for more than {self.index_timeout} seconds")
            self._update()

    def _update(self):
        """
        Requests a fresh list of employees and builds a new search index.
        """
        employees = self.client.get_employees()
        self.index = self._build_index(employees)
        self.last_update = time.time()
        self.valid = True

    @classmethod
    def _build_index(cls, employees: List[Employee]) -> Dict[Employee, str]:
        """
        Build a search index from the specified list of employees

        :param employees: the employees to index
        :return: the search index
        """
        return {e: cls._get_keywords(e) for e in employees}

    @classmethod
    def _get_keywords(cls, e: Employee) -> str:
        """
        Specifies the keywords that are to be stored for this employee as part of the search index.
        The keywords consist of all string fields in the employee object that someone might
        reasonably search for: name, position, email, department, team, etc.
        We intentionally avoid to add references to other persons, e.g. the supervisor, as we only
        have a very basic ranking and this may lead to inaccurate search results.
        the keywords are stored as a single lowercase string with tokens separated by whitespace.

        :param e: we calculate the keywords for this employee
        :return: the keywords for this employee as normalized string
                 with tokens separated by whitespace
        """
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
