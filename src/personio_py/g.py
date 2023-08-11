from typing import TYPE_CHECKING, Optional

from personio_py import PersonioError

if TYPE_CHECKING:
    from personio_py.client import Personio


client: Optional['Personio'] = None


def get_client() -> 'Personio':
    if client:
        return client
    else:
        raise PersonioError(
            "No Personio client has been configured so far. Please create a Personio client "
            "instance to make API requests"
        )
