# personio-py

a lightweight Personio API client.

## Getting Started

To set up your local development environment, please use a fresh virtual environment.

Then run:

    pip install -r requirements.txt -r requirements-dev.txt

This project is intended to be used as library, so there is no command line interface or stuff like that.

### Testing

We use `pytest` as test framework. To execute the tests, please run

    python setup.py test

To run the tests with coverage information, please use

    python setup.py testcov

and have a look at the `htmlcov` folder, after the tests are done.

### Distribution Package

To build a distribution package (wheel), please use

    python setup.py dist

this will clean up the build folder and then run the `bdist_wheel` command.

### Contributions

Before contributing, please set up the pre-commit hooks to reduce errors and ensure consistency

    pip install -U pre-commit && pre-commit install

## Contact

Sebastian Straub (sebastian.straub@alexanderthamm.com)

## License

© Alexander Thamm GmbH
