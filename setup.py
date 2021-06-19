# type: ignore

import importlib.util
import pathlib
import setuptools
import typing


KEYWORDS = [
    "apidocs",
    "bibliography",
    "documentation",
    "glossary",
    "kglab",
    "knowledge graph",
    "mkdocs",
    "plugin",
    "reference",
    ]


def parse_requirements_file (filename: str) -> typing.List:
    """read and parse a Python `requirements.txt` file, returning as a list of str"""
    with pathlib.Path(filename).open() as f:
        return [ l.strip().replace(" ", "") for l in f.readlines() ]


if __name__ == "__main__":
    spec = importlib.util.spec_from_file_location("mkrefs.version", "mkrefs/version.py")
    mkrefs_version = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mkrefs_version)

    setuptools.setup(
        name = "mkrefs",
        version = mkrefs_version.__version__,

        description = "MkDocs plugin to generate semantic reference Markdown pages",
        long_description = pathlib.Path("README.md").read_text(),
        long_description_content_type = "text/markdown",

        author = "Paco Nathan",
        author_email = "paco@derwen.ai",
        license = "MIT",
        url = "",

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

        keywords = ", ".join(KEYWORDS),
        classifiers = [
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "Intended Audience :: Information Technology",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3 :: Only",
            "Topic :: Documentation",
            "Topic :: Software Development :: Documentation",
            "Topic :: Text Processing :: Markup :: Markdown",
            ]
        )
