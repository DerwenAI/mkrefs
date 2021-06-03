#!/usr/bin/env python
# -*- coding: utf-8 -*-
# see license https://github.com/DerwenAI/mkrefs#license-and-copyright

from collections import defaultdict, OrderedDict
from pprint import pprint  # type: ignore # pylint: disable=W0611
import json
import re
import tempfile
import typing

import pandas as pd  # type: ignore # pylint: disable=E0401
import pathlib

import kglab

from .util import get_jinja2_template, render_reference


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
                entity = val
            else:
                values[col_names[i]] = None if pd.isna(val) else val

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
    df = kg.query_as_df(sparql)
    list_name = df.columns[1]

    list_ids: typing.Dict[str, list] = defaultdict(list)

    for rec in df.to_records(index=False):
        key = de_bracket(rec[0])
        val = de_bracket(rec[1])
        list_ids[key].append(val)

    return list_name, list_ids


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


def render_biblio (  # pylint: disable=R0914
    local_config: dict,
    kg: kglab.KnowledgeGraph,
    template_path: pathlib.Path,
    markdown_path: pathlib.Path,
    ) -> typing.Dict[str, list]:
    """
Render the Markdown for a bibliography, based on the given KG and
Jinja2 template.

    local_config:
local configuration, including user-configurable SPARQL queries

    kg:
the KG graph object

    template_path:
file path for Jinja2 template for rendering a bibliography page in MkDocs

    markdown_path:
file path for the rendered Markdown file

    returns:
rendered Markdown
    """
    # get the bibliograph entry identifiers
    sparql = local_config["biblio"]["queries"]["entry"]
    df = kg.query_as_df(sparql)
    entry_ids = denorm_entity(df, "entry")

    # get the entity maps
    entity_map:dict = {}

    sparql = local_config["biblio"]["queries"]["entry_author"]
    list_name, list_ids = get_item_list(kg, sparql)
    entity_map[list_name] = list_ids

    sparql = local_config["biblio"]["queries"]["entry_publisher"]
    list_name, list_ids = get_item_list(kg, sparql)
    entity_map[list_name] = list_ids

    # extract content as JSON-LD
    items: dict = {}

    json_path = pathlib.Path(tempfile.NamedTemporaryFile().name)
    kg.save_jsonld(json_path)

    with open(json_path, "r") as f:  # pylint: disable=W0621
        bib_j = json.load(f)

        for item in bib_j["@graph"]:
            id = item["@id"]
            items[id] = abbrev_iri(item)

    # remap the JSON-LD for bibliography entries
    entries: dict = {}

    for id, val_dict in entry_ids.items():
        citekey = val_dict["citeKey"]
        entries[citekey] = items[id]

        for key in entries[citekey].keys():
            if key in entity_map:
                entries[citekey][key] = [
                    items[mapped_id]
                    for mapped_id in entity_map[key][id]
                    ]

    # initialize the `groups` grouping of entries
    entries = OrderedDict(sorted(entries.items()))
    letters = sorted(list({
                key[0].lower()
                for key in entries.keys()
                }))

    groups: typing.Dict[str, list] = {  # pylint: disable=W0621
        l: []
        for l in letters
        }

    # build the grouping of content entries, with the authors and
    # publishers denormalized
    for citekey, entry in entries.items():
        groups[citekey[0].lower()].append(entry)

    # render the JSON into Markdown using the Jinja2 template
    _ = render_reference(template_path, markdown_path, groups)

    return groups
