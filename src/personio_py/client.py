"""
Implementation of the Personio API functions
"""
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar, Union
from urllib.parse import urljoin

import requests
from requests import Response

from personio_py import Absence, AbsenceType, Attendance, DynamicMapping, Employee, Project
from personio_py.errors import MissingCredentialsError, PersonioApiError, PersonioError
from personio_py.models import PersonioResource
from personio_py.search import SearchIndex

logger = logging.getLogger('personio_py')

PersonioResourceType = TypeVar('PersonioResourceType', bound=PersonioResource, covariant=True)


class Personio:
    """
    the Personio API client.

    :param base_url: use this custom base URL instead of the default https://api.personio.de/v1/
    :param client_id: the client id for API authentication
           (if not provided, defaults to the ``CLIENT_ID`` environment variable)
    :param client_secret: the client secret for API authentication
           (if not provided, defaults to the ``CLIENT_SECRET`` environment variable)
    :param dynamic_fields: definition of expected dynamic fields.
           List of :py:class:`DynamicMapping` tuples.
    """

    BASE_URL = "https://api.personio.de/v1/"
    """base URL of the Personio HTTP API"""
    ATTENDANCE_URL = 'company/attendances'
    ABSENCE_URL = 'company/time-offs'
    PROJECT_URL = 'company/attendances/projects'

    def __init__(self, base_url: str = None, client_id: str = None, client_secret: str = None,
                 dynamic_fields: List[DynamicMapping] = None):
        self.base_url = base_url or self.BASE_URL
        self.client_id = client_id or os.getenv('CLIENT_ID')
        self.client_secret = client_secret or os.getenv('CLIENT_SECRET')
        self.headers = {'accept': 'application/json'}
        self.authenticated = False
        self.dynamic_fields = dynamic_fields
        self.search_index = SearchIndex(self)

    def authenticate(self):
        """
        Try to authenticate (using Personio's ``/auth`` endpoint) with the credentials
        (client ID and secret) that were provided to this instance.

        There should be no need to explicitly call this function, because you will be automatically
        authenticated when you make your first request.

        If the authentication was successful, the authentication token is stored in the
        headers dictionary (``self.headers``). This token will be sent with every request and
        it will be automatically rotated whenever necessary.
        If the authentication failed, a ``PersonioApiError`` will be raised.
        """
        if not (self.client_id and self.client_secret):
            raise MissingCredentialsError(
                "both client_id and client_secret must be provided in order to authenticate")
        url = urljoin(self.base_url, 'auth')
        logger.debug(f"authenticating to {url} with client_id {self.client_id}")
        params = {"client_id": self.client_id, "client_secret": self.client_secret}
        response = requests.request("POST", url, headers=self.headers, params=params)
        if response.ok:
            token = response.json()['data']['token']
            self.headers['Authorization'] = f"Bearer {token}"
            self.authenticated = True
        else:
            raise PersonioApiError.from_response(response)

    def request(self, path: str, method='GET', params: Dict[str, Any] = None,
                data: Dict[str, Any] = None, headers: Dict[str, str] = None,
                auth_rotation=True) -> Response:
        """
        Make a request against the Personio API.
        Returns the HTTP response, which might be successful or not.

        Rotation of authorization tokens is handled in this function. If no token is available
        (first request of this instance), the ``authenticate()`` function is called. On subsequent
        requests, the new authorization token is read from the response headers and replaces the
        previous one. Note that this behavior can be turned off by setting auth_rotation=False,
        which is required for some requests that do not return a new authorization token.

        :param path: the URL path for this request (relative to the Personio API base URL)
        :param method: the HTTP request method (default: GET)
        :param params: dictionary of URL parameters (optional)
        :param data: dictionary of data to send in the request body (optional)
        :param headers: additional request headers (authentication is handled separately)
        :param auth_rotation: set to True, if authentication keys should be rotated
               during this request (default: True)
        :return: the HTTP response (the caller is responsible for handling HTTP errors)
        """
        # check if we are already authenticated
        if not self.authenticated:
            self.authenticate()
        # define headers
        _headers = self.headers
        if headers:
            _headers.update(headers)
        # make the request
        url = urljoin(self.base_url, path)
        response = requests.request(method, url, headers=_headers, params=params, json=data)
        # re-new the authorization header
        authorization = response.headers.get('Authorization')
        if authorization:
            self.headers['Authorization'] = authorization
        elif auth_rotation:
            raise PersonioError("Missing Authorization Header in response")
        # return the response, let the caller handle any issues
        return response

    def request_json(self, path: str, method='GET', params: Dict[str, Any] = None,
                     data: Dict[str, Any] = None, auth_rotation=True) -> Dict[str, Any]:
        """
        Make a request against the Personio API, expecting a json response.
        Returns the parsed json response as dictionary. Will raise a PersonioApiError if the
        request fails.

        :param path: the URL path for this request (relative to the Personio API base URL)
        :param method: the HTTP request method (default: GET)
        :param params: dictionary of URL parameters (optional)
        :param data: dictionary of data to send in the request body (optional)
        :param auth_rotation: set to True, if authentication keys should be rotated
               during this request (default: True for json requests)
        :return: the parsed json response, when the request was successful, or a PersonioApiError
        """
        response = self.request(path, method, params, data, auth_rotation=auth_rotation)
        if response.ok:
            try:
                return response.json()
            except ValueError:
                raise PersonioError(f"Failed to parse response as json: {response.text}")
        else:
            raise PersonioApiError.from_response(response)

    def request_paginated(self, path: str, method='GET', params: Dict[str, Any] = None,
                          data: Dict[str, Any] = None, auth_rotation=True, limit=200
                          ) -> Dict[str, Any]:
        """
        Make a request against the Personio API, expecting a json response that may be paginated,
        i.e. not all results might have been returned after the first request. Will continue
        to make requests until no more results are provided by the Personio API.
        Returns the parsed json response as dictionary. Will raise a PersonioApiError if the
        request fails.

        :param path: the URL path for this request (relative to the Personio API base URL)
        :param method: the HTTP request method (default: GET)
        :param params: dictionary of URL parameters (optional)
        :param data: dictionary of data to send in the request body (optional)
        :param auth_rotation: set to True, if authentication keys should be rotated
               during this request (default: True for json requests)
        :param limit: the max. number of items to return in response to a single request.
               A higher limit means fewer requests will be made (though there is an upper bound
               that is enforced on the server side)
        :return: the parsed json response, when the request was successful, or a PersonioApiError
        """
        if self.ABSENCE_URL == path:
            offset = 1
            url_type = 'absence'
        elif self.ATTENDANCE_URL == path:
            offset = 0
            url_type = 'attendance'
        else:
            raise ValueError(f"Invalid path: {path}")

        if params is None:
            params = {}
        params['limit'] = limit
        params['offset'] = offset
        data_acc = []
        while True:
            response = self.request_json(path, method, params, data, auth_rotation=auth_rotation)
            resp_data = response.get('data')
            if resp_data:
                if url_type == 'absence':
                    data_acc.extend(resp_data)
                    if response['metadata']['current_page'] == response['metadata']['total_pages']:
                        break
                    else:
                        params['offset'] += 1
                elif url_type == 'attendance':
                    if params['offset'] >= response['metadata']['total_elements']:
                        break
                    else:
                        data_acc.extend(resp_data)
                        params['offset'] += limit
            else:
                break
        # return the accumulated data
        response['data'] = data_acc
        return response

    def request_image(self, path: str, method='GET', params: Dict[str, Any] = None,
                      auth_rotation=False) -> Optional[bytes]:
        """
        Request an image file (as png or jpg) from the Personio API.
        Returns the image as byte array, or None, if no image is available for this resource
        (HTTP status 404).
        When any other errors occur, a PersonioApiError is raised.

        :param path: the URL path for this request (relative to the Personio API base URL)
        :param method: the HTTP request method (default: GET)
        :param params: dictionary of URL parameters (optional)
        :param auth_rotation: set to True, if authentication keys should be rotated
               during this request (default: False for image requests)
        :return: the image (bytes) or None, if no image is available
        """
        headers = {'accept': 'image/png, image/jpeg'}
        response = self.request(path, method, params, headers=headers, auth_rotation=auth_rotation)
        if response.ok:
            # great, we have our image as png or jpg
            return response.content
        elif response.status_code == 404:
            # no image? how disappointing...
            return None
        else:
            # oh noes, something went terribly wrong!
            raise PersonioApiError.from_response(response)

    def get_employees(self) -> List[Employee]:
        """
        Get a list of all employee records in your account.
        Does not involve pagination.

        :return: list of ``Employee`` instances
        """
        response = self.request_json('company/employees')
        employees = [Employee.from_dict(d, self) for d in response['data']]
        return employees

    def get_employee(self, employee_id: int) -> Employee:
        """
        Get a single employee with the specified ID.
        Does not involve pagination.

        :param employee_id: the Personio ID of the employee to fetch
        :return: an ``Employee`` instance or a PersonioApiError, if the employee does not exist
        """
        response = self.request_json(f'company/employees/{employee_id}')
        employee = Employee.from_dict(response['data'], self)
        return employee

    def get_employee_picture(self, employee: Union[int, Employee], width: int = None) \
            -> Optional[bytes]:
        """
        Get the profile picture of the specified employee as image file
        (usually png or jpg).

        :param employee: get the picture of this employee or the employee with
               the specified Personio ID
        :param width: optionally scale the profile picture to this width.
               Defaults to the original width of the profile picture.
        :return: the profile picture as png or jpg file (bytes)
        """
        employee_id = employee.id_ if isinstance(employee, Employee) else int(employee)
        path = f'company/employees/{employee_id}/profile-picture'
        if width:
            path += f'/{width}'
        return self.request_image(path, auth_rotation=False)

    def create_employee(self, employee: Employee, refresh=True) -> Employee:
        """
        placeholder; not ready to be used
        """
        # TODO warn about limited selection of fields
        data = {
            'employee[email]': employee.email,
            'employee[first_name]': employee.first_name,
            'employee[last_name]': employee.last_name,
            'employee[gender]': employee.gender,
            'employee[position]': employee.position,
            'employee[department]': employee.department.name,
            'employee[hire_date]': employee.hire_date.isoformat()[:10],
            'employee[weekly_hours]': employee.weekly_working_hours,
        }
        response = self.request_json('company/employees', method='POST', data=data)
        employee.id_ = response['data']['id']
        if refresh:
            return self.get_employee(employee.id_)
        else:
            return employee

    def update_employee(self, employee: Employee):
        """
        placeholder; not ready to be used
        """
        raise NotImplementedError()

    def get_attendances(
            self, employees: Union[int, List[int], Employee, List[Employee]],
            start_date: datetime = None, end_date: datetime = None) -> List[Attendance]:
        """
        Get a list of all attendance records for the employees with the specified IDs

        Note that internally, multiple requests may be made by this function due to limitations
        of the Personio API: Only a limited number of records can be retrieved in a single request
        and only a limited number of employee IDs can be passed as URL parameters. The results
        are still presented as a single list, no matter how many requests are made.

        :param employees: a single employee or a list of employee objects or IDs.
               Attendance records for all matching employees will be retrieved.
        :param start_date: only return attendance records from this date (inclusive, optional)
        :param end_date: only return attendance records up to this date (inclusive, optional)
        :return: list of ``Attendance`` records for the specified employees
        """
        attendances = self._get_employee_metadata(
            self.ATTENDANCE_URL, Attendance, employees, start_date, end_date)
        for attendance in attendances:
            attendance._client = self
        return attendances

    def create_attendances(self, attendances: List[Attendance]) -> bool:
        """
        Create all given attendance records.

        Note: If one or more attendances can not be created, other attendances will be created but
        their corresponding objects passed as attendances will not be updated.

        :param attendances: A list of attendance records to be created.
        """
        data_to_send = [
            attendance.to_body_params(patch_existing_attendance=False) for attendance in attendances
        ]
        response = self.request_json(
            path=self.ATTENDANCE_URL,
            method='POST',
            data={"attendances": data_to_send}
        )
        if response['success']:
            for attendance, response_id in zip(attendances, response['data']['id']):
                attendance.id_ = response_id
                attendance.client = self
            return True
        return False

    def update_attendance(self, attendance: Attendance):
        """
        Update an existing attendance record

        Either an attendance id or o remote query is required. Remote queries are only executed
        if required. An Attendance object returned by get_attendances() include the attendance id.
        DO NOT SET THE ID YOURSELF.

        :param attendance: The Attendance object holding the new data.
        :raises:
            ValueError: If a query is required but not allowed or the query does not provide
            exactly one result.
        """
        if attendance.id_ is not None:
            # remote query not necessary
            response = self.request_json(
                path=f'{self.ATTENDANCE_URL}/{attendance.id_}',
                method='PATCH',
                data=attendance.to_body_params(patch_existing_attendance=True)
            )
            return response
        else:
            raise ValueError("You need to provide the attendance id")

    def delete_attendance(self, attendance: Attendance or int):
        """
        Delete an existing record

        Either an attendance id or o remote query is required. Remote queries are only
        executed if required. An Attendance object returned by get_attendances() include the
        attendance id. DO NOT SET THE ID YOURSELF.

        :param attendance: The Attendance object holding the new data or an attendance record id to
            delete.
        :raises:
            ValueError: If a query is required but not allowed or the query does not provide
            exactly one result.
        """
        if isinstance(attendance, int):
            response = self.request_json(path=f'{self.ATTENDANCE_URL}/{attendance}',
                                         method='DELETE')
            return response
        elif isinstance(attendance, Attendance):
            if attendance.id_ is not None:
                return self.delete_attendance(attendance.id_)
            else:
                raise ValueError("You need to provide the attendance")
        else:
            raise ValueError("attendance must be an Attendance object or an integer")

    def get_absence_types(self) -> List[AbsenceType]:
        """
        Get a list of all available absence types, e.g. "paid vacation" or "parental leave".

        The absence types are used to classify the absences of employees
        (see ``get_absences`` to get a list of all absences for the employees).
        Each ``Absence`` also contains the ``AbsenceType`` for this instance; the purpose
        of this function is to provide you with a list of all possible options that can show up.
        """
        response = self.request_json('company/time-off-types')
        absence_types = [AbsenceType.from_dict(d, self) for d in response['data']]
        return absence_types

    def get_absences(
            self, employees: Union[int, List[int], Employee, List[Employee]],
            start_date: datetime = None, end_date: datetime = None) -> List[Absence]:
        """
        Get a list of all absence records for the employees with the specified IDs.

        Note that internally, multiple requests may be made by this function due to limitations
        of the Personio API: Only a limited number of records can be retrieved in a single request
        and only a limited number of employee IDs can be passed as URL parameters. The results
        are still presented as a single list, no matter how many requests are made.

        :param employees: a single employee or a list of employee objects or IDs.
               Absence records for all matching employees will be retrieved.
        :param start_date: only return absence records from this date (inclusive, optional)
        :param end_date: only return absence records up to this date (inclusive, optional)
        :return: list of ``Absence`` records for the specified employees
        """
        return self._get_employee_metadata(
            self.ABSENCE_URL, Absence, employees, start_date, end_date)

    def get_absence(self, absence: Union[Absence, int]) -> Absence:
        """
        Get an absence record from a given id.

        :param absence: The absence id to fetch.
        """
        if isinstance(absence, int):
            response = self.request_json(f'{self.ABSENCE_URL}/{absence}')
            return Absence.from_dict(response['data'], self)
        else:
            if absence.id_:
                return self.get_absence(absence.id_)
            else:
                self.__add_remote_absence_id(absence)
                return self.get_absence(absence.id_)

    def create_absence(self, absence: Absence) -> Absence:
        """
        Creates an absence record on the Personio servers

        :param absence: The absence object to be created
        :raises PersonioError: If the absence could not be created on the Personio servers
        """
        data = absence.to_body_params()
        response = self.request_json(self.ABSENCE_URL, method='POST', data=data)
        if response['success']:
            absence.id_ = response['data']['attributes']['id']
            return absence
        raise PersonioError("Could not create absence")

    def delete_absence(self, absence: Union[Absence, int]):
        """
        Delete an existing record

        An absence id is required.

        :param absence: The Absence object holding
               the new data or an absence record id to delete.
        :raises ValueError: If a query is required but not allowed
                or the query does not provide exactly one result.
        """
        if isinstance(absence, int):
            response = self.request_json(path=f'{self.ABSENCE_URL}/{absence}', method='DELETE')
            return response['success']
        elif isinstance(absence, Absence):
            if absence.id_ is not None:
                return self.delete_absence(absence.id_)
            else:
                raise ValueError("Only an absence with an absence id can be deleted.")
        else:
            raise ValueError("absence must be an Absence object or an integer")

    def search(self, query: str, active_only=True) -> List[Employee]:
        """
        Execute a search on the search index.

        If the index does not exist, or has been invalidated or is expired, the full list
        of employees will be requested from the API.

        During the search we perform a case insensitive match on the keywords in the search index.
        All tokens of the query will be matched individually. Tokens are separated by whitespace.
        A full match (i.e. all tokens match the keywords in order) is preferred over
        a partial match (only one or more tokens match).

        For more details, please refer to :class:`SearchIndex`.

        :param query: the query string
        :param active_only: exclude inactive employees from the results (default: yes)
        :return: the list of employees that matches the search query
        """
        return self.search_index.search(query, active_only=active_only)

    def search_first(self, query: str, active_only=True) -> Optional[Employee]:
        """
        Execute a search on the search index and return the first result (if there is one) or None.

        This is basically the "I'm Feeling Lucky" button.
        For details about the search function, please refer to :class:`SearchIndex`.

        :param query: the query string
        :param active_only: exclude inactive employees from the results (default: yes)
        :return: the first search result or None, if there were no results
        """
        return self.search_index.search_first(query, active_only=active_only)

    def invalidate_index(self):
        """
        Invalidates the search index. New data will be requested on the next search.
        """
        self.search_index.invalidate()

    def get_projects(self) -> List[Project]:
        """
        Get a list of all company projects.

        :return: list of ``Project`` records
        """
        response = self.request_json(self.PROJECT_URL)
        projects = [Project.from_dict(d, self) for d in response['data']]
        return projects

    def create_project(self, project: Project) -> Project:
        """
        Creates a project record on the Personio servers.

        :param project: The project object to be created
        :raises PersonioError: If the project could not be created on the Personio servers
        """
        data = project.to_body_params()
        response = self.request_json(self.PROJECT_URL, method='POST', data=data)
        if response['success']:
            project.id_ = response['data']['id']
            return project
        raise PersonioError("Could not create project")

    def update_project(self, project: Project) -> Project:
        """
        Updates a project record on the Personio servers.

        :param project: The project object to be updated
        :raises PersonioErrror: If the project could not be created on the Personio servers
        """
        data = project.to_body_params()
        response = self.request_json(f'{self.PROJECT_URL}/{project.id_}', method='PATCH', data=data)
        if response['success']:
            return project
        raise PersonioError("Could not update project")

    def delete_project(self, project: Union[Project, int]) -> None:
        """
        Deletes a project record on the Personio servers.

        :param project: The project object to be updated
        :raises ValueError: If a query is required but not allowed
            or the query does not provide exactly one result.
        """
        if isinstance(project, int):
            response = self.request(f'{self.PROJECT_URL}/{project}', method='DELETE')
            return response
        elif isinstance(project, Project):
            if project.id_ is not None:
                return self.delete_project(project.id_)
            else:
                raise ValueError("Only a project with a project id can be deleted.")
        else:
            raise ValueError("project must be a Project object or an integer")

    def _get_employee_metadata(
            self, path: str, resource_cls: Type[PersonioResourceType],
            employees: Union[int, List[int], Employee, List[Employee]], start_date: datetime = None,
            end_date: datetime = None) -> List[PersonioResourceType]:
        # resolve params to match API requirements
        employees, start_date, end_date = self._normalize_timeframe_params(
            employees, start_date, end_date)
        params = {
            "start_date": start_date.isoformat()[:10],
            "end_date": end_date.isoformat()[:10],
        }
        # request in batches of up to 50 employees (keeps URL length well below 2000 chars)
        data_acc = []
        for i in range(0, len(employees), 50):
            params["employees[]"] = employees[i:i + 50]
            response = self.request_paginated(path, params=params)
            data_acc.extend(response['data'])
        # create objects from accumulated API responses
        parsed_data = [resource_cls.from_dict(d, self) for d in data_acc]
        return parsed_data

    @classmethod
    def _normalize_timeframe_params(
            cls, employees: Union[int, List[int], Employee, List[Employee]],
            start_date: datetime = None, end_date: datetime = None) \
            -> Tuple[List[int], datetime, datetime]:
        """
        Whenever we need a list of employee IDs, a start date and an end date, this function comes
        in handy:

        * wraps a single employee ID into a list
        * sets the start date way into the past, if it was not provided
        * sets the end date way into the future, if it was not provided

        :param employees: a single employee or a list of employees (employee objects or just IDs)
        :param start_date: a start date (optional)
        :param end_date: an end date (optional)
        :return: a tuple of (list of employee IDs, start date, end date), no None values.
        """
        if not employees:
            raise ValueError("need at least one employee ID, got nothing")
        if start_date is None:
            start_date = datetime(1900, 1, 1)
        if end_date is None:
            end_date = datetime(datetime.now().year + 10, 1, 1)
        if not isinstance(employees, list):
            employees = [employees]
        employee_ids = [(e.id_ if isinstance(e, Employee) else e) for e in employees]
        return employee_ids, start_date, end_date

    def __add_remote_absence_id(self, absence: Absence) -> Absence:
        """
        Queries the API for an absence record matching
        the given Absence object and adds the remote id.

        :param absence: The absence object to be updated
        :return: The absence object with the absence_id set
        """
        if absence.employee is None:
            raise ValueError("For a remote query an employee_id is required")
        if absence.start_date is None:
            raise ValueError("For a remote query a start date is required")
        if absence.end_date is None:
            raise ValueError("For a remote query an end date is required")
        matching_remote_absences = self.get_absences(employees=[absence.employee.id_],
                                                     start_date=absence.start_date,
                                                     end_date=absence.end_date)
        if len(matching_remote_absences) == 0:
            raise PersonioError("The absence to patch was not found")
        elif len(matching_remote_absences) > 1:
            raise PersonioError("More than one absence found.")
        absence.id_ = matching_remote_absences[0].id_
        return absence
