import json
from functools import lru_cache
from typing import Dict

from tests import resource_dir


@lru_cache(maxsize=None)
def load_mock_data(file: str) -> Dict:
    with (resource_dir / file).open('r') as fp:
        return json.load(fp)
