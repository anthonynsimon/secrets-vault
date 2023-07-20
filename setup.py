#!/usr/bin/env python
import pathlib
import sys

from setuptools import find_packages, setup

assert sys.version_info >= (3, 9), "Requires Python v3.9 or above."

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()
REQUIREMENTS = [
    x.strip() for x in (HERE / "requirements.txt").read_text().split("\n") if not x.startswith("#") and x.strip()
]

# Load version without importing anything from the package
exec(open("secrets_vault/version.py").read())

setup(
    name="secrets-vault",
    version=__version__,
    author="Anthony N. Simon",
    url="https://github.com/anthonynsimon/secrets-vault",
    description="Simple encrypted secrets for Python",
    long_description=README,
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "secrets-vault=secrets_vault.__main__:cli",
            "secrets=secrets_vault.__main__:cli",
        ]
    },
    install_requires=REQUIREMENTS,
    tests_require=[],
)
