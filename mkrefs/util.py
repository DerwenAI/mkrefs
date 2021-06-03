#!/usr/bin/env python
# -*- coding: utf-8 -*-
# see license https://github.com/DerwenAI/mkrefs#license-and-copyright

import typing

import jinja2  # type: ignore # pylint: disable=E0401
import pathlib

import kglab


def load_kg (
    path: pathlib.Path,
    ) -> kglab.KnowledgeGraph:
    """
Load a KG from an RDF file in "Turtle" (TTL) format.

    path:
path to the RDF file

    returns:
populated KG
    """
    kg = kglab.KnowledgeGraph()
    kg.load_rdf(path, format="ttl")

    return kg


def get_jinja2_template (
    template_file: str,
    dir: str,
    ) -> jinja2.Template:
    """
Load a Jinja2 template.
Because MkDocs runs the `on_env` event way too late in the lifecycle to use it to generate markdown files.

    template_file:
file name of the Jinja2 template file

    dir:
subdirectory in which the template file is located

    returns:
loaded Jinja2 template
    """
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(dir),
        autoescape=True,
        )

    return env.get_template(template_file)


def render_reference (
    template_path: pathlib.Path,
    markdown_path: pathlib.Path,
    groups: typing.Dict[str, list],
    ) -> str:
    """
Render the Markdown for a MkRefs reference component, based on the
given Jinja2 template.

    template_path:
file path for Jinja2 template for rendering a reference page in MkDocs

    markdown_path:
file path for the rendered Markdown file

    groups:
JSON denomalized content data

    returns:
rendered Markdown
    """
    template_file = str(template_path.relative_to(template_path.parent))
    template = get_jinja2_template(template_file, str(template_path.parent))

    # render the JSON into Markdown using the Jinja2 template
    with open(markdown_path, "w") as f:
        f.write(template.render(groups=groups))

    return template.render(groups=groups)
