from typing import Any, Dict, Type

from requests import Response


class PersonioError(Exception):
    """A generic error caused by personio-py"""


class MissingCredentialsError(PersonioError):
    """you are missing some strictly required credentials"""


class PersonioApiError(PersonioError):
    """An error response from the Personio HTTP API"""

    def __init__(self, status_code: int, message: str, error_code: int = None, errors: Dict[str, Any] = None, response: Response = None):
        super().__init__()
        self.status_code = status_code
        self.message = message
        self.error_code = error_code
        self.errors = errors
        self.response = response

    @classmethod
    def from_response(cls, response: Response):
        try:
            data: Dict = response.json()
            error = data.get('error', {})
            code = error.get('code')
            message = error.get('message')
            error_dict: Dict = error.get('errors')
            return PersonioApiError(
                status_code=response.status_code,
                message=message,
                error_code=code,
                errors=error_dict,
                response=response)
        except ValueError as e:
            return PersonioApiError(
                status_code=response.status_code,
                message=response.text,
                response=response)

    def __str__(self):
        message = f"request failed with HTTP status code {self.status_code}: {self.message}"
        if self.error_code:
            message += f" (error code {self.error_code})"
        if self.errors:
            if message[-1] != '.':
                message += '.'
            message += f" Details: {self.errors}"
        return message


class UnsupportedMethodError(PersonioError):
    """this method is not supported by this class (but it might be by a similar one)"""

    def __init__(self, method: str, clazz: Type):
        super().__init__()
        self.method = method
        self.clazz = clazz

    def __str__(self):
        return f"method '{self.method}' is not available for {self.clazz.__name__}"
