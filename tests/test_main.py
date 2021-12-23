import re

import personio_py
from tests import root


def test_version():
    module_version = personio_py.__version__
    pyproject_toml = (root / 'pyproject.toml').read_text()
    pyproject_version = re.search(r'version = "(.+?)"', pyproject_toml).group(1)
    assert module_version == pyproject_version
