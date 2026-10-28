"""
Chakravyuh Test Runner & Direct-Stat Import Hook.

Note: On 9p virtualized mounts where `os.listdir()` returns empty sets unless files are
stat'd directly, this runner installs a lightweight `MetaPathFinder` that resolves ONLY
project modules (`chakravyuh.*` and `tests.*`) via `os.path.isfile()` / `os.path.isdir()`
and executes the entire Chakravyuh test suite (`tests/test_*.py`).
"""

import importlib.abc
import importlib.machinery
import importlib.util
import os
import sys
import unittest
from typing import Optional, Sequence


class DirectStatPathFinder(importlib.abc.MetaPathFinder):
    """Resolves `chakravyuh` and `tests` packages using direct `os.stat` (`isfile`/`isdir`)."""

    def __init__(self, search_paths: Sequence[str]) -> None:
        self.search_paths = list(search_paths)

    def find_spec(
        self,
        fullname: str,
        path: Optional[Sequence[str]] = None,
        target: Optional[object] = None,
    ) -> Optional[importlib.machinery.ModuleSpec]:
        top_pkg = fullname.split(".")[0]
        if top_pkg not in ("chakravyuh", "tests"):
            return None

        parts = fullname.split(".")
        rel_path = os.path.join(*parts)
        for base in self.search_paths:
            candidate_init = os.path.join(base, rel_path, "__init__.py")
            if os.path.isfile(candidate_init):
                return importlib.util.spec_from_file_location(
                    fullname,
                    candidate_init,
                    submodule_search_locations=[os.path.join(base, rel_path)],
                )
            candidate_mod = os.path.join(base, f"{rel_path}.py")
            if os.path.isfile(candidate_mod):
                return importlib.util.spec_from_file_location(fullname, candidate_mod)
        return None


def main() -> int:
    repo_root = os.path.dirname(os.path.abspath(__file__))
    src_root = os.path.join(repo_root, "src")
    sys.meta_path.insert(0, DirectStatPathFinder([src_root, repo_root]))

    test_modules = [
        "tests.test_unit_voice_and_asr",
        "tests.test_unit_deception_and_ioc",
        "tests.test_integration_api_and_ws",
        "tests.test_security_and_edge_cases",
        "tests.test_phase2_and_phase3_services",
    ]

    suite = unittest.TestSuite()
    loader = unittest.defaultTestLoader
    for mod_name in test_modules:
        mod = __import__(mod_name, fromlist=["*"])
        suite.addTests(loader.loadTestsFromModule(mod))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
