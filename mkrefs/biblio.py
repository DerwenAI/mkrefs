#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pprint import pprint
import json
import pathlib
import tempfile
import typing

import jinja2  # pylint: disable=E0401
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


def is_kind (
    item: dict,
    kind_list: typing.List[str],
    ) -> bool:
    """
Test whether the given JSON-LD content item has a "@type" within the
specified list.
    """
    if "@type" not in item:
        return False

    return any(map(lambda k: item["@type"].endswith(k), kind_list))  # pylint: disable=W0108


def denorm_biblio_groups (
    kg: kglab.KnowledgeGraph,  # pylint: disable=W0621
    ) -> typing.Dict[str, list]:
    """
Denormalize a KG into groups of bibliographic entries so that they can
be rendered as Markdown.

TODO: use queries to filter/segment the needed entities from the KG
    """
    # serialize as JSON-LD
    json_path = pathlib.Path(tempfile.NamedTemporaryFile().name)
    kg.save_jsonld(json_path)

    # extract content as JSON
    bib_g = []

    with open(json_path, "r") as f:  # pylint: disable=W0621
        bib_j = json.load(f)
        bib_g = bib_j["@graph"]

    # what are the types of content?
    types = {  # pylint: disable=W0612
        item["@type"]
        for item in bib_g
        if "@type" in item
        }
    #pprint(types)

    # who are the authors?
    authors = {
        item["@id"]: item
        for item in bib_g
        if is_kind(item, ["Person"])
        }
    #pprint(authors)

    # which are the publishers?
    pubs = {
        item["@id"]: item
        for item in bib_g
        if is_kind(item, ["Collection", "Journal", "Proceedings"])
        }
    #pprint(pubs)

    # enumerate and sort the content entries
    content = sorted(
        [
            item
            for item in bib_g
            if is_kind(item, ["Article", "Slideshow"])
            ],
        key = lambda item: item["https://derwen.ai/ns/v1#citeKey"],
        )
    #pprint(content)

    # initialize the `groups` grouping of entries
    letters = sorted(list({
                item["https://derwen.ai/ns/v1#citeKey"][0].upper()
                for item in content
                }))

    groups: typing.Dict[str, list] = {  # pylint: disable=W0621
        l: []
        for l in letters
        }

    # build the grouping of content entries, with the authors and
    # publishers denormalized
    for item in content:
        #pprint(item)

        trans = {
            "citekey": item["https://derwen.ai/ns/v1#citeKey"],
            "type": item["@type"].split("/")[-1],
            "url": item["@id"],
            "date": item["dct:date"]["@value"],
            "title": item["dct:title"],
            "abstract": item["http://purl.org/ontology/bibo/abstract"],
            }

        trans["auth"] = [
            {
                "url": auth["@id"],
                "name": authors[auth["@id"]]["http://xmlns.com/foaf/0.1/name"],
                }
            for auth in item["http://purl.org/ontology/bibo/authorList"]["@list"]
            ]

        if "http://purl.org/ontology/bibo/doi" in item:
            trans["doi"] = item["http://purl.org/ontology/bibo/doi"]["@value"]

        if "https://derwen.ai/ns/v1#openAccess" in item:
            trans["open"] = item["https://derwen.ai/ns/v1#openAccess"]["@id"]

        if "dct:isPartOf" in item:
            pub = pubs[item["dct:isPartOf"]["@id"]]

            trans["pub"] = {
                "url": pub["dct:identifier"]["@id"],
                "title": pub["http://purl.org/ontology/bibo/shortTitle"],
                }

            if "http://purl.org/ontology/bibo/volume" in item:
                trans["pub"]["volume"] = item["http://purl.org/ontology/bibo/volume"]["@value"]

            if "http://purl.org/ontology/bibo/issue" in item:
                trans["pub"]["issue"] = item["http://purl.org/ontology/bibo/issue"]["@value"]

            if "http://purl.org/ontology/bibo/pageStart" in item:
                trans["pub"]["pageStart"] = item["http://purl.org/ontology/bibo/pageStart"]["@value"]

            if "http://purl.org/ontology/bibo/pageEnd" in item:
                trans["pub"]["pageEnd"] = item["http://purl.org/ontology/bibo/pageEnd"]["@value"]

        #pprint(trans)
        letter = item["https://derwen.ai/ns/v1#citeKey"][0].upper()
        groups[letter].append(trans)

    return groups


def render_biblio (
    kg: kglab.KnowledgeGraph,
    template: jinja2.Template,
    path: pathlib.Path,
    ) -> None:
    """
Render the Markdown for a bibliography, based on the given KG and Jinja2 template.

    kg:
KG containing the bibliography entities

    template:
Jinja2 template for rendering a bibliography page in MkDocs

    path:
file path for the rendered Markdown file
    """
    groups = denorm_biblio_groups(kg)

    with open(path, "w") as f:
        f.write(template.render(groups=groups))
