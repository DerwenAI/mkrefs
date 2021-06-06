#!/usr/bin/env python
# -*- coding: utf-8 -*-
# see license https://github.com/DerwenAI/mkrefs#license-and-copyright

from collections import OrderedDict
import json
import tempfile
import typing

import kglab
import pathlib

from .util import abbrev_iri, denorm_entity, get_item_list, render_reference


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
    entity_map: dict = {}

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

        items = {
            item["@id"]: abbrev_iri(item)
            for item in bib_j["@graph"]
        }

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
        letter: []
        for letter in letters
        }

    # build the grouping of content entries, with the authors and
    # publishers denormalized
    for citekey, entry in entries.items():
        letter = citekey[0].lower()
        groups[letter].append(entry)

    # render the JSON into Markdown using the Jinja2 template
    _ = render_reference(template_path, markdown_path, groups)

    return groups
