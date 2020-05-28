import logging
import os
from datetime import datetime
from typing import Any, Dict, List
from urllib.parse import urljoin

import requests

from personio_py import Absence, AbsenceType, Attendance, Employee
from personio_py.errors import MissingCredentialsError, PersonioApiError, PersonioError

logger = logging.getLogger('personio_py')


class Personio:

    BASE_URL = "https://api.personio.de/v1/"

    def __init__(self, base_url: str = None, client_id: str = None, client_secret: str = None):
        self.base_url = base_url or self.BASE_URL
        self.client_id = client_id or os.getenv('CLIENT_ID')
        self.client_secret = client_secret or os.getenv('CLIENT_SECRET')
        self.headers = {'accept': 'application/json'}
        self.authenticated = False

    def authenticate(self):
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

    def request(self, path: str, method='GET', params: Dict[str, Any] = None):
        # check if we are already authenticated
        if not self.authenticated:
            self.authenticate()
        # make the request
        url = urljoin(self.base_url, path)
        response = requests.request(method, url, headers=self.headers, params=params)
        # re-new the authorization header
        authorization = response.headers.get('Authorization')
        if authorization:
            self.headers['Authorization'] = authorization
        else:
            raise PersonioError("Missing Authorization Header in response")
        # handle the response
        if response.ok:
            try:
                data = response.json()
                return data
            except ValueError as e:
                raise PersonioError(f"Failed to parse response as json: {response.text}")
        else:
            raise PersonioApiError.from_response(response)

    def get_employees(self) -> List[Employee]:
        response = self.request('company/employees')
        employees = [Employee.from_dict(d['attributes']) for d in response['data']]
        return employees

    def get_employee(self, employee_id: int) -> Employee:
        response = self.request(f'company/employees/{employee_id}')
        employee_dict = response['data']['attributes']
        employee = Employee.from_dict(employee_dict, self)
        return employee

    def get_employee_picture(self, employee_id: int) -> bytes:
        # TODO implement
        pass

    def create_employee(self, employee: Employee):
        # TODO implement
        pass

    def update_employee(self, employee: Employee):
        # TODO implement
        pass

    def get_attendances(
            self, start_date: datetime, end_date: datetime = None, employee_ids: List[int] = None,
            limit: int = None, offset=0) -> List[Attendance]:
        # TODO implement
        pass

    def create_attendances(self, attendances: List[Attendance]):
        # attendances can be created individually, but here you can push a huge bunch of items
        # in a single request, which can be significantly faster
        # TODO implement
        pass

    def update_attendance(self, attendance_id: int):
        # TODO implement
        pass

    def delete_attendance(self, attendance_id: int):
        # TODO implement
        pass

    def get_absence_types(self) -> List[AbsenceType]:
        # TODO implement
        pass

    def get_absences(
            self, start_date: datetime, end_date: datetime = None, employee_ids: List[int] = None,
            limit: int = None, offset=0) -> List[Absence]:
        # TODO implement
        pass

    def get_absence(self, absence_id: int) -> Absence:
        # TODO implement
        pass

    def create_absence(self, absence: Absence):
        # TODO implement
        pass

    def delete_absence(self, absence_id: int):
        # TODO implement
        pass
