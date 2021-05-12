# type: ignore

import pathlib
import setuptools
import typing


def parse_requirements_file (filename: str) -> typing.List:
    """read and parse a Python `requirements.txt` file, returning as a list of str"""
    with pathlib.Path(filename).open() as f:
        return [ l.strip().replace(" ", "") for l in f.readlines() ]


setuptools.setup(
    name = "mkrefs",
    version = "0.1.0",

    description = "MkDocs plugin to generate reference Markdown pages",
    long_description = pathlib.Path("README.md").read_text(),
    long_description_content_type = "text/markdown",

    author = "Paco Nathan",
    author_email = "paco@derwen.ai",
    license = "MIT",

    url = "",
    keywords = "mkdocs",

    python_requires = ">=3.6",
    packages = setuptools.find_packages(exclude=[ "docs" ]),
    install_requires = parse_requirements_file("requirements.txt"),

    entry_points = {
        "mkdocs.plugins": [
            "mkrefs = mkrefs.plugin:MkRefsPlugin",
            ],

        "console_scripts": [
            "mkrefs = mkrefs.cli:cli",
            ],
        },

    classifiers = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ]
)
