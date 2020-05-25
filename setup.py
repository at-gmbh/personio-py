import os
import shutil
import subprocess
import sys
from distutils.cmd import Command
from runpy import run_path

from setuptools import find_packages, setup

# read the program version from version.py (without loading the module)
__version__ = run_path('src/personio_py/version.py')['__version__']


def read(fname):
    """Utility function to read the README file."""
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


class DistCommand(Command):

    description = "build the distribution packages (in the 'dist' folder)"
    user_options = []

    def initialize_options(self): pass
    def finalize_options(self): pass

    def run(self):
        if os.path.exists('build'):
            shutil.rmtree('build')
        subprocess.run(["python", "setup.py", "sdist", "bdist_wheel"])


class TestCommand(Command):

    description = "run all tests with pytest"
    user_options = []

    def initialize_options(self): pass
    def finalize_options(self): pass

    def run(self):
        sys.path.append('src')
        import pytest
        return pytest.main(['tests', '--no-cov'])


class TestCovCommand(Command):

    description = "run all tests with pytest and write a test coverage report"
    user_options = []

    def initialize_options(self): pass
    def finalize_options(self): pass

    def run(self):
        sys.path.append('src')
        params = "tests --doctest-modules --junitxml=junit/test-results.xml " \
                 "--cov=src --cov-report=xml --cov-report=html"
        import pytest
        return pytest.main(params.split(' '))


setup(
    name="personio-py",
    version=__version__,
    author="Sebastian Straub",
    author_email="sebastian.straub@alexanderthamm.com",
    description="a lightweight Personio API client",
    license="proprietary",
    url="",
    packages=find_packages("src"),
    package_dir={"": "src"},
    package_data={'personio_py': ['res/*']},
    long_description=read('README.md'),
    install_requires=[],
    tests_require=[
        'pytest',
        'pytest-cov',
        'pre-commit',
    ],
    cmdclass={
        'dist': DistCommand,
        'test': TestCommand,
        'testcov': TestCovCommand,
    },
    platforms='any',
    python_requires='>=3.7',
)
