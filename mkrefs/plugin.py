#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys ; sys.path.insert(0, "../kglab/")
import kglab

from pprint import pprint
import jinja2  # pylint: disable=E0401
import json
import mkdocs.config
import mkdocs.plugins
import mkdocs.structure.files
import pathlib
import tempfile
import typing


class MkRefsPlugin (mkdocs.plugins.BasePlugin):

    config_scheme = (
        ("mkrefs_bib_page", mkdocs.config.config_options.Type(str, default="biblio.md")),
        ("mkrefs_bib_graph", mkdocs.config.config_options.Type(str, default="biblio.ttl")),
        ("mkrefs_bib_template", mkdocs.config.config_options.Type(str, default="biblio.template")),
    )

    def __init__ (self):
        print("__init__", self.config_scheme)

        self.enabled = True
        self.biblio_kg = None
        self.biblio_file = None


    def on_config (self, config, **kwargs):
        print("on_config")
        pprint(config)

        if self.config["mkrefs_bib_graph"]:
            biblio_path = pathlib.Path(config["docs_dir"]) / self.config["mkrefs_bib_graph"]
            self.biblio_kg = kglab.KnowledgeGraph()
            self.biblio_kg.load_rdf(biblio_path, format="ttl")

        return config


    def on_pre_build (self, config, **kwargs):
        print("on_pre_build")
        return


    def on_files (self, files, config, **kwargs):
        for file in files.documentation_pages():
            print(file.src_path, file.dest_path)

        self.biblio_file = mkdocs.structure.files.File(
            path = config["mkrefs_bib_page"],
            src_dir = config["docs_dir"],
            dest_dir = config["site_dir"],
            use_directory_urls = config["use_directory_urls"],
            )

        files.append(self.biblio_file)

        groups = transform_to_groups(self.biblio_kg)
        biblio_path = pathlib.Path(config["docs_dir"]) / self.biblio_file.src_path

        with open(biblio_path, "w") as f:
            template = get_jinja2_template(config["mkrefs_bib_template"], config["docs_dir"])
            f.write(template.render(groups=groups))

        return files


    def on_page_read_source (self, page, config, **kwargs):
        print("on_page_read_source")
        #pprint(vars(page.file))

        if page.file.abs_src_path == config["mkrefs_bib_page"]:
            print("FOUND!", config["mkrefs_bib_page"])

        return None


    ######################################################################
    ## unused events

    def on_env (self, env, config, files, **kwargs):
        print("on_env")
        return env

    def on_nav (self, nav, config, files, **kwargs):
        print("on_nav")
        return nav

    def on_pre_template (self, template, template_name, config, **kwargs):
        return template

    def on_template_context (self, context, template_name, config, **kwargs):
        return context
    
    def on_post_template (self, output_content, template_name, config, **kwargs):
        return output_content
    
    def on_pre_page (self, page, config, files, **kwargs):
        return page

    def on_page_markdown (self, markdown, page, config, files, **kwargs):
        return markdown

    def on_page_content (self, html, page, config, files, **kwargs):
        return html

    def on_page_context (self, context, page, config, nav, **kwargs):
        return context

    def on_post_page (self, output_content, page, config, **kwargs):
        return output_content

    def on_post_build (self, config, **kwargs):
        return

    def on_serve (self, server, **kwargs):
        return server


######################################################################
## bibliography

def get_jinja2_template (
    template_file: str,
    dir: str,
    ) -> jinja2.Template:
    """
Load a Jinja2 template.
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


def transform_to_groups (
    kg: kglab.KnowledgeGraph,  # pylint: disable=W0621
    ) -> typing.Dict[str, list]:
    """
Transform a KG into groups of entries that can be rendered
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
    #ic(types)

    # who are the authors?
    authors = {
        item["@id"]: item
        for item in bib_g
        if is_kind(item, ["Author"])
        }
    #ic(authors)

    # which are the publishers?
    pubs = {
        item["@id"]: item
        for item in bib_g
        if is_kind(item, ["Collection", "Journal", "Proceedings"])
        }
    #ic(pubs)

    # enumerate and sort the content entries
    content = sorted(
        [
            item
            for item in bib_g
            if is_kind(item, ["Article", "Slideshow"])
            ],
        key = lambda item: item["https://derwen.ai/ns/v1#citeKey"],
        )
    #ic(content)

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
        #ic(item)

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

        #ic(trans)
        letter = item["https://derwen.ai/ns/v1#citeKey"][0].upper()
        groups[letter].append(trans)

    return groups
