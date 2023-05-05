# personio-py

[![build](https://github.com/at-gmbh/personio-py/workflows/build/badge.svg?branch=master&event=push)](https://github.com/at-gmbh/personio-py/actions?query=workflow%3Abuild)
[![PyPI](https://img.shields.io/pypi/v/personio-py)](https://pypi.org/project/personio-py/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/personio-py)](https://pypi.org/project/personio-py/)
[![documentation](https://img.shields.io/badge/docs-latest-informational)](https://at-gmbh.github.io/personio-py/)
[![Codecov](https://img.shields.io/codecov/c/github/at-gmbh/personio-py)](https://codecov.io/gh/at-gmbh/personio-py)
[![#personio-py:matrix.org](https://img.shields.io/matrix/personio-py:matrix.org)](https://matrix.to/#/#personio-py:matrix.org)
[![PyPI - License](https://img.shields.io/pypi/l/personio-py)](https://github.com/at-gmbh/personio-py/blob/master/LICENSE)

**personio-py** is a lightweight [Personio](https://www.personio.de/) API client library for Python. Also, it's pretty intuitive to use. But don't take my word for it, please have a look:

```python
>>> from personio_py import Personio
>>> p = Personio(client_id='***', client_secret='***')
>>> ada = p.search_first("Ada")
>>> ada.last_name
'Lovelace'
>>> absences = p.get_absences(ada)
>>> len(absences)
12
>>> absences[0].to_dict()
{'id': 42, 'status': 'approved', 'start_date': '2020-08-01', 'end_date': '2020-08-16', ...}
```

**personio-py** aims to provide Python function wrappers and object mappings for all endpoints of the [Personio REST API](https://developer.personio.de/reference). Because personio-py is a third party library, and the REST API may change from time to time, we cannot guarantee that all functions are covered, but we try our best.

If something appears to be broken, please have a look at the [open issues](https://github.com/at-gmbh/personio-py/issues) and vote for an existing issue or create a new one, if you can't find an issue that describes your problem.

**📖 Documentation is available at [at-gmbh.github.io/personio-py](https://at-gmbh.github.io/personio-py/)**

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

Now you can `import personio_py` and start coding. Please have a look at the [User Guide](https://at-gmbh.github.io/personio-py/guide.html) and the [Examples](https://at-gmbh.github.io/personio-py/examples.html) section for more details.

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

### PyPI Release

This project is released on [PyPI](https://pypi.org/project/personio-py/). Most of the tedious steps that are required to test & publish your release are automated by [CI pipelines](https://github.com/at-gmbh/personio-py/actions). All you have to do is to write your code and when the time comes to make a release, please follow these steps:

* update the program version in [`src/personio_py/version.py`](./src/personio_py/version.py)
* write a summary of your changes in [`CHANGELOG.md`](./CHANGELOG.md)
* add a tag on the master branch with the new version number preceded by the letter `v`, e.g. for version 1.0.0 the tag would be `v1.0.0`. To tag the head of the current branch, use `git tag v1.0.0`
* push your changes to github and don't forget to push the tag with `git push origin v1.0.0`
* now have a look at the [release pipeline](https://github.com/at-gmbh/personio-py/actions?query=workflow%3Arelease) on GitHub. If it finishes without errors, you can find your release on [TestPyPI](https://test.pypi.org/project/personio-py). Please verify that your release works as expected.
* Now for the live deployment on PyPI. To avoid mistakes, this is only triggered, when a release is published on GitHub first. Please have a look at the [Releases](https://github.com/at-gmbh/personio-py/releases) now; there should be a draft release with your version number (this was created by the CI pipeline which also made the TestPyPI release). Edit the draft release, copy the text you added to [`CHANGELOG.md`](./CHANGELOG.md) into the description field and publish it.
* After you publish the release, the [deploy pipeline](https://github.com/at-gmbh/personio-py/actions?query=workflow%3Adeploy) is triggered on GitHub. It will publish the release directly to [PyPI](https://pypi.org/project/personio-py/) where everyone can enjoy your latest features.

## API Functions

Since the [Personio API](https://developer.personio.de/reference/introduction) gets extended over time, personio-py usually only implements a subset of all available API features. This section gives an overview, which API functions are accessible through personio-py.

### Available

Authentication

* [`POST /auth`](https://developer.personio.de/reference/post_auth-1): fully transparent authentication handling

Employees

* [`GET /company/employees`](https://developer.personio.de/reference/get_company-employees): list all employees
* [`POST /company/employees`](https://developer.personio.de/reference/post_company-employees): create a new employee
* [`GET /company/employees/{id}`](https://developer.personio.de/reference/get_company-employees-employee-id): get the employee with the specified ID
* [`GET /company/employees/{id}/profile-picture/{width}`](https://developer.personio.de/reference/get_company-employees-employee-id-profile-picture-width): get the profile picture of the specified employee

Attendances

* [`GET /company/attendances`](https://developer.personio.de/reference/get_company-attendances): fetch attendance data for the company employees
* [`POST /company/attendances`](https://developer.personio.de/reference/post_company-attendances): add attendance data for the company employees
* [`DELETE /company/attendances/{id}`](https://developer.personio.de/reference/delete_company-attendances-id): delete the attendance entry with the specified ID
* [`PATCH /company/attendances/{id}`](https://developer.personio.de/reference/patch_company-attendances-id): update the attendance entry with the specified ID

Projects

* [`GET /company/attendances/projects`](https://developer.personio.de/reference/get_company-attendances-projects): provides a list of all company projects
* [`POST /company/attendances/projects`](https://developer.personio.de/reference/post_company-attendances-projects): creates a project into the company account
* [`DELETE /company/attendances/projects/{id}`](https://developer.personio.de/reference/delete_company-attendances-projects-id): deletes a project from the company account
* [`PATCH /company/attendances/projects/{id}`](https://developer.personio.de/reference/patch_company-attendances-projects-id): updates a project with the given data

Absences

* [`GET /company/time-off-types`](https://developer.personio.de/reference/get_company-time-off-types): get a list of available absences types
* [`GET /company/time-offs`](https://developer.personio.de/reference/get_company-time-offs): fetch absence data for the company employees
* [`POST /company/time-offs`](https://developer.personio.de/reference/post_company-time-offs): add absence data for the company employees
* [`GET /company/time-offs/{id}`](https://developer.personio.de/reference/get_company-time-offs-id): get the absence entry with the specified ID
* [`DELETE /company/time-offs/{id}`](https://developer.personio.de/reference/delete_company-time-offs-id): delete the absence entry with the specified ID

### Not yet implemented

* [`PATCH /company/employees/{id}`](https://developer.personio.de/reference/patch_company-employees-employee-id): update an existing employee entry
* [`GET /company/employees/{employee_id}/absences/balance`](https://developer.personio.de/reference/get_company-employees-employee-id-absences-balance): retrieve the absence balance for a specific employee
* [`GET /company/employees/custom-attributes`](https://developer.personio.de/reference/get_company-employees-custom-attributes): this endpoint is an alias for /company/employees/attributes
* [`GET /company/employees/attributes`](https://developer.personio.de/reference/get_company-employees-attributes): lists all the allowed attributes per API credentials including custom (dynamic) attributes.
* [`GET /company/absence-periods`](https://developer.personio.de/reference/get_company-absence-periods)
* [`POST /company/absence-periods`](https://developer.personio.de/reference/post_company-absence-periods)
* [`DELETE /company/absence-periods/{id}`](https://developer.personio.de/reference/delete_company-absence-periods-id)

* [`GET /company/document-categories`](https://developer.personio.de/reference/get_company-document-categories): this endpoint is responsible for fetching all document categories of the company
* [`POST /company/documents`](https://developer.personio.de/reference/post_company-documents): this endpoint is responsible for uploading documents for the company employees
* [`GET /company/custom-reports/reports`](https://developer.personio.de/reference/listreports): this endpoint provides you with metadata about existing custom reports in your Personio account, such as report name, report type, report date / timeframe
* [`GET /company/custom-reports/reports/{report_id}`](https://developer.personio.de/reference/listreportitems): this endpoint provides you with the data of an existing Custom Report
* [`GET /company/custom-reports/columns`](https://developer.personio.de/reference/listcolumns): this endpoint provides human-readable labels for report table columns
* all of the [recruiting API](https://developer.personio.de/reference/introduction-1)

## Contact

Sebastian Straub (sebastian.straub [at] alexanderthamm.com)

Developed with ❤ at [Alexander Thamm GmbH](https://www.alexanderthamm.com/)

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
