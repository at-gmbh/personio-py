# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased](https://github.com/at-gmbh/personio-py/compare/v0.2.3...HEAD)

* add support for providing a custom `requests.Session` in client
  ([#39](https://github.com/at-gmbh/personio-py/pull/39)

* add pagination to get employees method
  ([#42](https://github.com/at-gmbh/personio-py/pull/42))

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
