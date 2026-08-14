# setup.py
#
# The version is read from schema_contract.SCHEMA_VERSION rather than
# duplicated here. Two hand-maintained version numbers is how a package
# ends up claiming 0.1.0 while its declared public surface is at 1.2.0 --
# which is exactly what this file used to do.
#
# tests/ and legacy/ are excluded from the distribution. legacy/ has no
# __init__.py so find_packages() already skips it; the explicit exclude
# is there so that adding one by accident does not silently ship
# quarantined, superseded code. See legacy/README.md.

import re
from pathlib import Path

from setuptools import find_packages, setup

HERE = Path(__file__).parent


def read_version() -> str:
    """Parse SCHEMA_VERSION out of schema_contract.py without importing
    it -- importing would pull in the whole sensor suite at build time."""
    source = (HERE / "schema_contract.py").read_text(encoding="utf-8")
    match = re.search(
        r'^SCHEMA_VERSION\s*=\s*["\']([^"\']+)["\']', source, re.MULTILINE
    )
    if not match:
        raise RuntimeError("could not find SCHEMA_VERSION in schema_contract.py")
    return match.group(1)


setup(
    name="logic-ferret",
    version=read_version(),
    author="JinnZ2",
    description=(
        "Detects rhetorical camouflage and discourse collapse in text: a "
        "14-sensor suite, a 9-layer conflict-diagnosis pipeline, and a "
        "critical-thinking check for human readers."
    ),
    long_description=(HERE / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url="https://github.com/JinnZ2/Logic-Ferret",
    # Matches the LICENSE file at repo root. Note that every module in
    # knowledge/ declares "License: CC0" in its own docstring, which
    # predates this file and conflicts with it -- see the open questions
    # in legacy/README.md. Declaring MIT here follows LICENSE, which is
    # the authoritative one; resolving the conflict is the owner's call.
    license="MIT",
    packages=find_packages(exclude=["tests", "tests.*", "legacy", "legacy.*"]),
    python_requires=">=3.8",
    # The analysis core is pure standard library on purpose -- it must be
    # runnable anywhere, including offline. Tkinter ships with CPython and
    # is only needed for the optional GUI, so it is not a hard dependency.
    install_requires=[],
    extras_require={"gui": []},
    entry_points={
        "console_scripts": [
            "logic-ferret=run_conflict_diagnosis:main",
            "logic-ferret-check=run_article_check:main",
            "logic-ferret-gui=fallacy_gui:main",
        ]
    },
    py_modules=[
        "schema_contract",
        "run_conflict_diagnosis",
        "run_full_sensor_scan",
        "run_article_check",
        "fallacy_gui",
        "truth_integrity_score",
    ],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Topic :: Text Processing :: Linguistic",
        "Intended Audience :: Education",
    ],
)
