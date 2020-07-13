import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urljoin

import requests
from requests import Response

from personio_py import Absence, AbsenceType, Attendance, DynamicMapping, Employee
from personio_py.errors import MissingCredentialsError, PersonioApiError, PersonioError

logger = logging.getLogger('personio_py')


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

    def __init__(self, base_url: str = None, client_id: str = None, client_secret: str = None,
                 dynamic_fields: List[DynamicMapping] = None):
        self.base_url = base_url or self.BASE_URL
        self.client_id = client_id or os.getenv('CLIENT_ID')
        self.client_secret = client_secret or os.getenv('CLIENT_SECRET')
        self.headers = {'accept': 'application/json'}
        self.authenticated = False
        self.dynamic_fields = dynamic_fields

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
        response = requests.request(method, url, headers=_headers, params=params, data=data)
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
        headers = {'accept': 'application/json'}
        response = self.request(path, method, params, data, headers, auth_rotation=auth_rotation)
        if response.ok:
            try:
                return response.json()
            except ValueError:
                raise PersonioError(f"Failed to parse response as json: {response.text}")
        else:
            raise PersonioApiError.from_response(response)

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

        :return: list of ``Employee`` instances
        """
        response = self.request_json('company/employees')
        employees = [Employee.from_dict(d['attributes'], self) for d in response['data']]
        return employees

    def get_employee(self, employee_id: int) -> Employee:
        """
        Get a single employee with the specified ID.

        :param employee_id: the Personio ID of the employee to fetch
        :return: an ``Employee`` instance or a PersonioApiError, if the employee does not exist
        """
        response = self.request_json(f'company/employees/{employee_id}')
        employee_dict = response['data']['attributes']
        employee = Employee.from_dict(employee_dict, self)
        return employee

    def get_employee_picture(self, employee_id: int, width: int = None) -> Optional[bytes]:
        """
        Get the profile picture of the employee with the specified ID as image file
        (usually png or jpg).

        :param employee_id: the Personio ID of the employee to fetch
        :param width: optionally scale the profile picture to this width.
               Defaults to the original width of the profile picture.
        :return: the profile picture as png or jpg file (bytes)
        """
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
        # TODO implement
        pass

    def get_attendances(self, employee_ids: Union[int, List[int]], start_date: datetime = None,
                        end_date: datetime = None) -> List[Attendance]:
        """
        placeholder; not ready to be used
        """
        # TODO automatically resolve paginated requests

        employee_ids, start_date, end_date = self._normalize_timeframe_params(
            employee_ids, start_date, end_date)
        params = {
            "start_date": start_date.isoformat()[:10],
            "end_date": end_date.isoformat()[:10],
            "employees[]": employee_ids,
            "limit": 200,
            "offset": 0
        }
        response = self.request_json('company/attendances', params=params)
        attendances = [Attendance.from_dict(d, self) for d in response['data']]
        return attendances

    def create_attendances(self, attendances: List[Attendance]):
        """
        placeholder; not ready to be used
        """
        # attendances can be created individually, but here you can push a huge bunch of items
        # in a single request, which can be significantly faster
        # TODO implement
        pass

    def update_attendance(self, attendance_id: int):
        """
        placeholder; not ready to be used
        """
        # TODO implement
        pass

    def delete_attendance(self, attendance_id: int):
        """
        placeholder; not ready to be used
        """
        # TODO implement
        pass

    def get_absence_types(self) -> List[AbsenceType]:
        """
        placeholder; not ready to be used
        """
        # TODO implement
        pass

    def get_absences(self, employee_ids: Union[int, List[int]], start_date: datetime = None,
                     end_date: datetime = None) -> List[Absence]:
        """
        placeholder; not ready to be used
        """
        # TODO automatically resolve paginated requests

        employee_ids, start_date, end_date = self._normalize_timeframe_params(
            employee_ids, start_date, end_date)
        params = {
            "start_date": start_date.isoformat()[:10],
            "end_date": end_date.isoformat()[:10],
            "employees[]": employee_ids,
            "limit": 200,
            "offset": 0
        }
        response = self.request_json('company/time-offs', params=params)
        absences = [Absence.from_dict(d['attributes'], self) for d in response['data']]
        return absences

    def get_absence(self, absence_id: int) -> Absence:
        """
        placeholder; not ready to be used
        """
        # TODO implement
        pass

    def create_absence(self, absence: Absence):
        """
        placeholder; not ready to be used
        """
        # TODO implement
        pass

    def delete_absence(self, absence_id: int):
        """
        placeholder; not ready to be used
        """
        # TODO implement
        pass

    @classmethod
    def _normalize_timeframe_params(
            cls, employee_ids: Union[int, List[int]], start_date: datetime = None,
            end_date: datetime = None) -> Tuple[List[int], datetime, datetime]:
        """
        Whenever we need a list of employee IDs, a start date and an end date, this function comes
        in handy:

        * wraps a single employee ID into a list
        * sets the start date way into the past, if it was not provided
        * sets the end date way into the future, if it was not provided

        :param employee_ids: a single employee ID or a list of employee IDs
        :param start_date: a start date (optional)
        :param end_date: an end date (optional)
        :return: a tuple of (list of employee IDs, start date, end date), no None values.
        """
        if not employee_ids:
            raise ValueError("need at least one employee ID, got nothing")
        if start_date is None:
            start_date = datetime(1900, 1, 1)
        if end_date is None:
            end_date = datetime(datetime.now().year + 10, 1, 1)
        if not isinstance(employee_ids, list):
            employee_ids = [employee_ids]
        return employee_ids, start_date, end_date
