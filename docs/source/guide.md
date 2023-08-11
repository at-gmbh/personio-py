# User Guide

🚧 this page is still a work in progress 🚧

If you'd like to make a contribution, please join the project [on GitHub](https://github.com/at-gmbh/personio-py)

---

This user guide should help you to get started with personio-py, which includes installation and basic usage. Explanations of the more advanced features of the individual API functions will also be provided.

## Installation

### Requirements

**personio-py** works with Python 3.8 or higher. Python 2 is not supported, as well as Python 3.6 or lower. Using a recent version of Python allows us to write modern Python code without ugly compatibility layers. Also, we can avoid some dependencies that used to be mandatory, like `python-dateutil`, now that Python comes with more useful date & time handling out of the box.

The only dependency of personio-py is the [`requests`](https://pypi.org/project/requests/) library, which handles all API calls.

### Pip

The easiest way to install personio-py is using [pip](https://pip.pypa.io/en/stable/), which should be already installed when you're using Python 3.8 or higher (which is required to use personio-py).

The package is available on [PyPI](https://pypi.org/project/personio-py/) and can be installed with

    pip install personio-py

You can verify that installation was successful with

    python -c "import personio_py; print(personio_py)"

### From Source

To install personio-py from source, please clone the repo

    git clone git@github.com:at-gmbh/personio-py.git

then switch to the project folder and run

    pip install .

this will build and install the `personio_py` module.

## First Steps

Now that personio-py is installed, we can start making requests. All requests are made through the [Personio](api.html#personio_py.Personio) class, which also handles authentication.

To authenticate, please provide your Client ID and Client Secret, which can be found in the Personio settings. If you have trouble finding your API keys, please refer to the [Personio Developer Hub](https://developer.personio.de/) (note: personio-py is not affiliated with Personio GmbH, therefore we can't provide any support regarding API keys).

When you have your Client ID and Secret, you are ready to make your first request:

```python
from personio_py import Personio

p = Personio(client_id='***', client_secret='***')
p.authenticate()
print(f"am I authenticated? {p.authenticated}")
```

Here we import the `Personio` class and create a new instance, providing our credentials (please replace `***` with your credentials). Then we call `authenticate()` on our `Personio` instance, which remains silent when authentication was successful. We can check that it worked by looking at `p.authenticated`, which should be `True` now.

If authentication fails, you will get a message like this:

    PersonioApiError: request failed with HTTP status code 403: Wrong credentials

In this case, please verify that your Client ID and Secret are correct. If the problem persists, please try to follow the tutorials in the [Personio Developer Hub](https://developer.personio.de/) before you go on with personio-py. If authentication works using the methods described in the Personio Developer Hub, but not with personio-py, you may have found a bug. Please file an [issue report](https://github.com/at-gmbh/personio-py/issues) in this case.

Also note that it is not required to call `authenticate()`; personio-py checks every time you make a request whether you're authenticated and will automatically request an authentication token if you're not. Therefore making your first request right after your `Personio` instance was created is absolutely fine:

```python
from personio_py import Personio

p = Personio(client_id='***', client_secret='***')
employees = p.get_employees()
print(f"got {len(employees)} employees in Personio")
```

That's it for the basics. Next we will get into more detail regarding the available API functions.

## Employees

(wip)

## Attendances

(wip)

## Absences

(wip)
