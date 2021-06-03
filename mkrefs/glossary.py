#!/usr/bin/env python
# -*- coding: utf-8 -*-
# see license https://github.com/DerwenAI/mkrefs#license-and-copyright

import typing

import pathlib

import kglab

from .util import get_jinja2_template, render_reference


def render_glossary (  # pylint: disable=R0914
    local_config: dict,
    kg: kglab.KnowledgeGraph,
    template_path: pathlib.Path,
    markdown_path: pathlib.Path,
    ) -> typing.Dict[str, list]:
    """
Render the Markdown for a glossary, based on the given KG and
Jinja2 template.

    local_config:
local configuration, including user-configurable SPARQL queries

    kg:
the KG graph object

    template_path:
file path for Jinja2 template for rendering a glossary page in MkDocs

    markdown_path:
file path for the rendered Markdown file

    returns:
rendered Markdown
    """
    groups: typing.Dict[str, list] = {  # pylint: disable=W0621
        }

    return groups
