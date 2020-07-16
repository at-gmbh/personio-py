# personio-py

![build](https://github.com/at-gmbh/personio-py/workflows/build/badge.svg?branch=master&event=push)

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

## Features

* Aims to cover all functions of the Personio API (work in progress)
* Python function wrappers for all API endpoints as part of the Personio class
* Object mappings for all API resources, e.g. an Employee is an object with properties for all the information that is provided by the REST API.
* Completely transparent handling of authentication and key rotation
* Support for Type Hints
* Only one dependency: [requests](https://pypi.org/project/requests/)

## Getting Started

The package is available on [PyPI](https://pypi.org/project/personio-py/) and can be installed with

    pip install personio-py

Now you can `import personio_py` and start coding. Please have a look at the [User Guide](guide.md) and the [Examples](examples.md) section for more details.

## Contributing

Contributions are very welcome! For our contribution guidelines, please have a look at [CONTRIBUTING.md](./CONTRIBUTING.md).

To set up your local development environment, please use a fresh virtual environment, then run

    pip install -r requirements.txt -r requirements-dev.txt

This project is intended to be used as library, so there is no command line interface or stuff like that.

We use `pytest` as test framework. To execute the tests, please run

    python setup.py test

To build a distribution package (wheel), please use

    python setup.py dist

this will clean up the build folder and then run the `bdist_wheel` command.

Before contributing code, please set up the pre-commit hooks to reduce errors and ensure consistency

    pip install -U pre-commit && pre-commit install

## Contact

Sebastian Straub (sebastian.straub [at] alexanderthamm.com)

## License

    Copyright 2020 Alexander Thamm GmbH

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
