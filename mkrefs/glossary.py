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
    # get the glossary entry identifiers
    sparql = local_config["glossary"]["queries"]["entry"]
    df = kg.query_as_df(sparql, simplify=False, pythonify=True)
    entry_ids = denorm_entity(df, "entry")

    sparql = local_config["glossary"]["queries"]["entry_syn"]
    _, syn_labels = get_item_list(kg, sparql)

    # get the entity maps
    entity_map: dict = {}

    sparql = local_config["glossary"]["queries"]["entry_ref"]
    list_name, list_ids = get_item_list(kg, sparql)
    entity_map[list_name] = list_ids

    ## localize the taxonomy for hypernyms
    sparql = local_config["glossary"]["queries"]["entry_hyp"]
    list_name, list_ids = get_item_list(kg, sparql)
    localized_hyp_ids: dict = {}

    for topic_uri, items in list_ids.items():
        hyp_ids: list = []

        for hypernym in items:
            if hypernym in entry_ids:
                hyp_label = entry_ids[hypernym]["label"]
                hyp_link = hyp_label.replace(" ", "-")

                hyp_ids.append(f"[{hyp_label}](#{hyp_link})")
            else:
                hyp_ids.append(f"<a href='{hypernym}' target='_blank'>{hypernym}</a>")

        localized_hyp_ids[topic_uri] = hyp_ids

    entity_map[list_name] = localized_hyp_ids

    ## localize the citekey entries for the bibliography
    sparql = local_config["glossary"]["queries"]["entry_cite"]
    list_name, list_ids = get_item_list(kg, sparql)
    biblio_page = "../{}/".format(local_config["biblio"]["page"].replace(".md", ""))
    localized_cite_ids: dict = {}

    for topic_uri, items in list_ids.items():
        localized_cite_ids[topic_uri] = [
            f"[[{citekey}]]({biblio_page}#{citekey})"
            for citekey in items
            ]

    entity_map[list_name] = localized_cite_ids

    # extract content as JSON-LD
    entries: dict = {}

    json_path = pathlib.Path(tempfile.NamedTemporaryFile().name)
    kg.save_jsonld(json_path)

    with open(json_path, "r") as f:  # pylint: disable=W0621
        gloss_j = json.load(f)

        entries = {
            entry_ids[item["@id"]]["label"]: abbrev_iri(item)
            for item in gloss_j["@graph"]
            if item["@id"] in entry_ids
        }

    # denormalize the JSON-LD for glossary entries
    for id, val_dict in entry_ids.items():
        definition = val_dict["label"]

        for key, entry in entity_map.items():
            for topic_uri, items in entry.items():
                if topic_uri == id:
                    entries[definition][key] = items

    # add redirects for the synonyms
    for topic_uri, items in syn_labels.items():
        for synonym in items:
            entries[synonym] = {
                "label": synonym,
                "redirect": entry_ids[topic_uri]["label"],
            }

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

    # build the grouping of content entries
    for definition, entry in entries.items():
        letter = definition[0].lower()
        groups[letter].append(entry)

    # render the JSON into Markdown using the Jinja2 template
    _ = render_reference(template_path, markdown_path, groups)

    return groups
