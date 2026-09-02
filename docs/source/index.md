# personio-py

**personio-py** is a lightweight Personio API client library for Python. Also, it's pretty intuitive to use. But don't take my word for it, please have a look:

```python
>>> from personio_py import Personio
>>> p = Personio(client_id='***', client_secret='***')
>>> ada = p.search_first("Ada")
>>> ada.last_name
'Lovelace'
>>> absences = p.get_absences(ada)
>>> len(absences)
12
>>> absences[0].model_dump()
{'id': 42, 'status': 'approved', 'start_date': datetime.date(2020, 8, 1), 'end_date': datetime.date(2020, 8, 16), ...}
```

**personio-py** aims to provide Python function wrappers and object mappings for all endpoints of the [Personio REST API](https://developer.personio.de/reference). Because personio-py is a third party library, and the REST API may change from time to time, we cannot guarantee that all functions are covered, but we try our best.

If something appears to be broken, please have a look at the [open issues](https://github.com/at-gmbh/personio-py/issues) and vote for an existing issue or create a new one, if you can't find an issue that describes your problem.

## Index

```{toctree}
:maxdepth: 2

guide
examples
contributing
changelog
api
```

## Features

* Aims to cover all functions of the Personio API (work in progress)
* Python function wrappers for all API endpoints as part of the {py:class}`Personio <personio_py.Personio>` class
* Object mappings for all API resources, e.g. an {py:class}`Employee <personio_py.models.Employee>` is an object with properties for all the information that is provided by the REST API.
* Completely transparent handling of authentication and key rotation
* Support for Type Hints
* Two lightweight dependencies: [requests](https://pypi.org/project/requests/) and [pydantic](https://docs.pydantic.dev/) (v2)

## Getting Started

The package is available on [PyPI](https://pypi.org/project/personio-py/) and can be installed with

    pip install personio-py

Now you can `import personio_py` and start coding. Please have a look at the [User Guide](guide.md) and the [Examples](examples.md) section for more details.
