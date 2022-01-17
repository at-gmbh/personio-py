# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased](https://github.com/at-gmbh/personio-py/compare/v0.2.1...HEAD)

* The data model was completely rebuilt based on [pydantic](https://pydantic-docs.helpmanual.io/), which makes it easier to work with different data types and allows for a better integration of custom attributes.
  - aliases are generated for all custom attributes based on their name in Personio
  - you can assign new values to the custom attribute field or its alias, they are always kept in sync
* New API endpoints
  - update employee: update the attributes of an employee
  - absence balance: retrieve the current absence balance of an employee
* Updated API Endpoints
  - create employee: now supports more attributes, including custom attributes
* Use poetry as build tool and improve the build process (including GitHub Actions)
* Upgrade Sphinx Documentation Generator and make it more robust
* Breaking changes:
  - required Python version: 3.8 or later
  - custom attributes (previous name: dynamic fields) are now direct attributes of the Employee object. The `dynamic` dict is not available anymore

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
