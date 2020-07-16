# personio-py

**personio-py** is a lightweight Personio API client library for Python. Also, it's pretty intuitive to use. But don't take my word for it, please have a look:

```python
>>> from personio_py import Personio
>>> p = Personio(client_id='***', client_secret='***')
>>> employees = p.get_employees()
>>> len(employees)
42
>>> ada = employees[0]
>>> ada.last_name
'Lovelace'
>>> absences = p.get_absences(ada.id_)
>>> len(absences)
12
>>> absences[0].to_dict()
{'id': 42, 'status': 'approved', 'start_date': '2020-08-01', 'end_date': '2020-08-16', ...}
```

**personio-py** aims to provide Python function wrappers and object mappings for all endpoints of the [Personio REST API](https://developer.personio.de/reference). Because personio-py is a third party library and the REST API may change from time to time, we cannot guarantee that all functions are covered, but we try our best.

If something appears to be broken, please have a look at the [open issues](https://github.com/at-gmbh/personio-py/issues) and vote for an existing issue or create a new one, if you can't find an issue that describes your problem.

## Index

* [User Guide](guide.md)
* [Examples](examples.md)
* [Contributing](contributing.md)
* [Changelog](changelog.md)
* [API Documentation](api.md)

## Features

* Aims to cover all functions of the Personio API (work in progress)
* Python function wrappers for all API endpoints as part of the [Personio](api.html#personio_py.Personio) class
* Object mappings for all API resources, e.g. an [Employee](api.html#personio_py.models.Employee) is an object with properties for all the information that is provided by the REST API.
* Completely transparent handling of authentication and key rotation
* Support for Type Hints
* Only one dependency: [requests](https://pypi.org/project/requests/)

## Getting Started

The package is available on [PyPI](https://pypi.org/project/personio-py/) and can be installed with

    pip install personio-py

Now you can `import personio_py` and start coding. Please have a look at the [User Guide](guide.md) and the [Examples](examples.md) section for more details.
