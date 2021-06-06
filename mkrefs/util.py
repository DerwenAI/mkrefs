#!/usr/bin/env python
# -*- coding: utf-8 -*-
# see license https://github.com/DerwenAI/mkrefs#license-and-copyright

from collections import defaultdict
import re
import typing

import jinja2  # type: ignore # pylint: disable=E0401
import kglab
import pathlib
import pandas as pd  # type: ignore # pylint: disable=E0401


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


def abbrev_key (
    key: str,
    ) -> str:
    """
Abbreviate the IRI, if any

    key:
string content to abbreviate

    returns:
abbreviated IRI content
    """
    if key.startswith("@"):
        return key[1:]

    key = key.split(":")[-1]
    key = key.split("/")[-1]
    key = key.split("#")[-1]

    return key


def abbrev_iri (
    item: typing.Any,
    ) -> typing.Any:
    """
Abbreviate the IRIs in JSON-LD graph content, so that Jinja2 templates
can use it.

    item:
scalar, list, or dictionary to iterate through

    returns:
data with abbreviated IRIs
    """
    if isinstance(item, dict):
        d = {
            abbrev_key(k): abbrev_iri(v)
            for k, v in item.items()
            }

        return d

    if isinstance(item, list):
        l = [
            abbrev_iri(x)
            for x in item
            ]

        return l

    return item


def denorm_entity (
    df: pd.DataFrame,
    entity_name: str,
    ) -> dict:
    """
Denormalize the result set from a SPARQL query, to collect a specific
class of entities from the KG, along with attribute for each instance.

    df:
SPARQL query result set, as a dataframe

    entity_name:
column name for the entity

    returns:
denormalized entity list with attributes, as a dict
    """
    col_names = list(df.columns)
    denorm = {}

    for rec in df.to_records(index=False):
        values = {}

        for i, val in enumerate(rec):
            if pd.isna(val):
                val = None
            else:
                s = re.search(r"\<(.*)\>", val)

                if s:
                    val = s.group(1)

            if col_names[i] == entity_name:
                entity = str(val)
            else:
                values[col_names[i]] = None if pd.isna(val) else str(val)

        denorm[entity] = values

    return denorm


def de_bracket (
    url: str,
    ) -> str:
    """
Extract the URL value from its RDF "bracketed" representation.

    url:
input URL string

    returns:
de-bracketed URL string
    """
    s = re.search(r"\<(.*)\>", url)

    if s:
        url = s.group(1)

    return url


def get_item_list (
    kg: kglab.KnowledgeGraph,
    sparql: str,
    ) -> typing.Tuple[str, dict]:
    """
Query to get a list of entity identifiers to substitute in JSON-LD.

    kg:
the KG graph object

    sparql:
SPARQL query

    returns:
a tuple of the list relation to replace, and the identifier values
    """
    df = kg.query_as_df(sparql, simplify=False, pythonify=True)
    list_name = df.columns[1]

    list_ids: typing.Dict[str, list] = defaultdict(list)

    for rec in df.to_records(index=False):
        key = str(de_bracket(rec[0]))
        val = str(de_bracket(rec[1]))
        list_ids[key].append(val)

    return list_name, list_ids


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
