import json
import os
from typing import Any


def load_test_data(module_path: str) -> Any:
    """
    Fetches data for a test case.
    :param module_path: Relative path to the module of the unittest.
    :return: Raw data for the requested test.
    """
    file_path = f"tests/{module_path}/data.json"  # Run from root
    if os.path.exists(file_path):
        with open(file_path, encoding="utf-8") as file:
            return json.load(file)
    raise IOError(f"File 'tests/{module_path}/data.json' can't be found")
