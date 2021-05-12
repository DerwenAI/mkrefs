#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pprint import pprint
import pathlib
import typing

import mkdocs.config
import mkdocs.plugins
import mkdocs.structure.files

from .biblio import load_kg, get_jinja2_template, render_biblio


class MkRefsPlugin (mkdocs.plugins.BasePlugin):

    config_scheme = (
        ("mkrefs_bib_page", mkdocs.config.config_options.Type(str, default="biblio.md")),
        ("mkrefs_bib_graph", mkdocs.config.config_options.Type(str, default="biblio.ttl")),
        ("mkrefs_bib_template", mkdocs.config.config_options.Type(str, default="biblio.template")),
    )

    def __init__ (self):
        #print("__init__", self.config_scheme)
        self.enabled = True
        self.biblio_kg = None
        self.biblio_file = None


    def on_config (self, config, **kwargs):
        #print("on_config")
        #pprint(config)

        if self.config["mkrefs_bib_graph"]:
            biblio_ttl_path = pathlib.Path(config["docs_dir"]) / self.config["mkrefs_bib_graph"]
            self.biblio_kg = load_kg(biblio_ttl_path)

        return config


    def on_files (self, files, config, **kwargs):
        self.biblio_file = mkdocs.structure.files.File(
            path = config["mkrefs_bib_page"],
            src_dir = config["docs_dir"],
            dest_dir = config["site_dir"],
            use_directory_urls = config["use_directory_urls"],
            )

        files.append(self.biblio_file)

        template = get_jinja2_template(config["mkrefs_bib_template"], config["docs_dir"])
        biblio_md_path = pathlib.Path(config["docs_dir"]) / self.biblio_file.src_path
        render_biblio(self.biblio_kg, template, biblio_md_path)

        return files


    ######################################################################
    ## unused events

    def on_pre_build (self, config, **kwargs):
        #print("on_pre_build")
        return

    def on_env (self, env, config, files, **kwargs):
        #print("on_env")
        return env

    def on_nav (self, nav, config, files, **kwargs):
        #print("on_nav")
        return nav

    def on_pre_template (self, template, template_name, config, **kwargs):
        return template

    def on_template_context (self, context, template_name, config, **kwargs):
        return context

    def on_post_template (self, output_content, template_name, config, **kwargs):
        return output_content

    def on_pre_page (self, page, config, files, **kwargs):
        return page

    def on_page_read_source (self, page, config, **kwargs):
        return None

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
