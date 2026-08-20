# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased](https://github.com/at-gmbh/personio-py/compare/v0.2.3...HEAD)

* add the `project` field to the `Attendance` model: attendance records now expose their
  project as a typed `Project` object (previously the field was silently dropped), and a
  project assigned to an `Attendance` is sent as `project_id` when creating or patching it.
  `ObjectFieldMapping` now passes the full nested dict to `from_dict()`, so a top-level `id`
  next to the `attributes` dict is preserved. ([#51](https://github.com/at-gmbh/personio-py/pull/51))
* migrate build & dependency management to [Poetry](https://python-poetry.org/): replace
  `setup.py` and `requirements*.txt` with a single `pyproject.toml` (PEP 621) plus committed
  `poetry.lock` and `test`/`linter`/`docs`/`dev` dependency groups; CI now builds, tests and
  publishes via Poetry (with `.venv` caching) ([#48](https://github.com/at-gmbh/personio-py/pull/48)
* fix parsing of multi-select (tags) custom attributes when the Personio API returns them as a
  JSON-encoded list string (e.g. `'["A","B"]'`) instead of a comma-separated string ([#48](https://github.com/at-gmbh/personio-py/pull/48)
* drop support for Python 3.7-3.9 (all end-of-life); personio-py now requires Python >= 3.10 ([#46](https://github.com/at-gmbh/personio-py/pull/46)
* raise the `requests` requirement to a modern version ([#46](https://github.com/at-gmbh/personio-py/pull/46)
* modernize the development tooling: replace flake8 with ruff, add pip-audit and bandit to
  pre-commit, bump all pre-commit hooks, and migrate the Sphinx docs to myst-parser ([#46](https://github.com/at-gmbh/personio-py/pull/46)
* send auth credentials in the request body instead of the query string, as required by
  the Personio API security update effective 2025-12-01 (query-string credentials return
  a 403 Forbidden from that date on) ([#45](https://github.com/at-gmbh/personio-py/pull/45)
* fix `PersonioError: Missing Authorization Header in response` for the attendances and
  projects endpoints, which do not return a rotating auth token (disable auth rotation for
  those requests, consistent with the existing image endpoints)
* fix `AttributeError` in `to_dict()` when an object field is returned
  empty (`""` or `[]`) instead of `null` by the Personio API; such empty object fields are now
  deserialized to `None` ([#47](https://github.com/at-gmbh/personio-py/pull/47)
* add support for providing a custom `requests.Session` in client
  ([#39](https://github.com/at-gmbh/personio-py/pull/39)

## [0.2.3](https://github.com/at-gmbh/personio-py/tree/v0.2.3) - 2023-05-05

* add support for Projects ([#36](https://github.com/at-gmbh/personio-py/pull/36))
* add support for attendances, with paginated API requests ([#35](https://github.com/at-gmbh/personio-py/pull/35))

## [0.2.2](https://github.com/at-gmbh/personio-py/tree/v0.2.2) - 2022-07-04

* add new fields: 'updated_at' and 'category' to the Absence and AbsenceType classes ([#26](https://github.com/at-gmbh/personio-py/pull/26))
* Upgrade Sphinx and fix CI job ([#27](https://github.com/at-gmbh/personio-py/pull/27))

## [0.2.1](https://github.com/at-gmbh/personio-py/tree/v0.2.1) - 2021-04-09

* add a basic in-memory search index for employees ([#19](https://github.com/at-gmbh/personio-py/pull/19))
* fix pagination for absence and attencence lists ([#20](https://github.com/at-gmbh/personio-py/pull/20))

## [0.2.0](https://github.com/at-gmbh/personio-py/tree/v0.2.0) - 2021-03-10

* add support for new API functions: `get_absences`, `get_absence_types`, `create_absence`, `delete_absence`, `get_attendances` (thanks [philipflohr](https://github.com/philipflohr)!)
* add support for paginated API requests (required for attendances & absences)
* make `from_dict()` and `to_dict()` behave consistently
* meta: improve CI builds & tests, better pre-commit hooks
* lots of mock tests & documentation

## [0.1.1](https://github.com/at-gmbh/personio-py/tree/v0.1.1) - 2020-08-19

- This is the first release of the Personio API client library
- Created Python module `personio_py`
- Documentation using Sphinx (on [GitHub Pages](https://at-gmbh.github.io/personio-py/))
