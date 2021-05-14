#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MkDocs Plugin.

https://www.mkdocs.org/
https://github.com/DerwenAI/mkrefs
"""

from pprint import pprint
import pathlib
import typing

from mkdocs.config import config_options
import mkdocs.plugins
import mkdocs.structure.files
import mkdocs.structure.nav
import mkdocs.structure.pages

import jinja2  # pylint: disable=E0401

from .biblio import load_kg, render_biblio


class MkRefsPlugin (mkdocs.plugins.BasePlugin):

    config_scheme = (
        ("mkrefs_bib_page", config_options.Type(str, default="biblio.md")),
        ("mkrefs_bib_graph", config_options.Type(str, default="biblio.ttl")),
        ("mkrefs_bib_template", config_options.Type(str, default="biblio.template")),
    )

    def __init__ (self):
        #print("__init__", self.config_scheme)
        self.enabled = True
        self.biblio_kg = None
        self.biblio_file = None


    def on_config (
        self,
        config: config_options.Config,
        **kwargs: typing.Any,
        ) -> typing.Dict[str, typing.Any]:
        """
The `config` event is the first event called on MkDocs build and gets
run immediately after the user configuration is loaded and validated.
Any alterations to the configuration should be made here.

https://www.mkdocs.org/user-guide/plugins/#on_config

    config:
the default global configuration object

    returns:
the modified global configuration object
        """
        #print("on_config")
        #pprint(config)

        if self.config["mkrefs_bib_graph"]:
            biblio_ttl_path = pathlib.Path(config["docs_dir"]) / self.config["mkrefs_bib_graph"]
            self.biblio_kg = load_kg(biblio_ttl_path)

        return config


    def on_files (
        self,
        files: mkdocs.structure.files.Files,
        config: config_options.Config,
        **kwargs: typing.Any,
        ) -> mkdocs.structure.files.Files:
        """

    config:
the default global configuration object
        """
        self.biblio_file = mkdocs.structure.files.File(
            path = config["mkrefs_bib_page"],
            src_dir = config["docs_dir"],
            dest_dir = config["site_dir"],
            use_directory_urls = config["use_directory_urls"],
            )

        files.append(self.biblio_file)

        template_path = pathlib.Path(config["docs_dir"]) / config["mkrefs_bib_template"]
        markdown_path = pathlib.Path(config["docs_dir"]) / self.biblio_file.src_path
        render_biblio(self.biblio_kg, template_path, markdown_path)

        return files


    ######################################################################
    ## other events

    def on_pre_build (
        self,
        config: config_options.Config,
        **kwargs: typing.Any,
        ):
        """
https://www.mkdocs.org/user-guide/plugins/#on_pre_build
        """
        #print("on_pre_build")
        return


    def on_env (
        self,
        env: jinja2.Environment,
        config: config_options.Config,
        files: mkdocs.structure.files.Files,
        **kwargs: typing.Any,
        ) -> jinja2.Environment:
        """
https://www.mkdocs.org/user-guide/plugins/#on_env
        """
        #print("on_env")
        #pprint(vars(env))
        return env


    def on_nav (
        self,
        nav: mkdocs.structure.nav.Navigation,
        config: config_options.Config,
        files: mkdocs.structure.files.Files,
        **kwargs: typing.Any,
        ) -> mkdocs.structure.nav.Navigation:
        """
https://www.mkdocs.org/user-guide/plugins/#on_nav
        """
        #print("on_nav")
        #pprint(vars(nav))
        return nav


    def on_pre_template (
        self,
        template,
        template_name: str,
        config: config_options.Config,
        **kwargs: typing.Any,
        ):
        """
https://www.mkdocs.org/user-guide/plugins/#on_pre_template
        """
        return template


    def on_template_context (
        self,
        context: dict,
        template_name: str,
        config: config_options.Config,
        **kwargs: typing.Any,
        ) -> dict:
        """
https://www.mkdocs.org/user-guide/plugins/#on_template_context
        """
        return context


    def on_post_template (
        self,
        output_content,
        template_name: str,
        config: config_options.Config,
        **kwargs: typing.Any,
        ):
        """
https://www.mkdocs.org/user-guide/plugins/#on_post_template
        """
        return output_content


    def on_pre_page (
        self,
        page: mkdocs.structure.pages.Page,
        config: config_options.Config,
        files: mkdocs.structure.files.Files,
        **kwargs: typing.Any,
        ):
        """
https://www.mkdocs.org/user-guide/plugins/#on_pre_page
        """
        return page


    def on_page_read_source (
        self,
        page: mkdocs.structure.pages.Page,
        config: config_options.Config,
        **kwargs: typing.Any,
        ):
        """
https://www.mkdocs.org/user-guide/plugins/#on_page_read_source
        """
        return None


    def on_page_markdown (
        self,
        markdown: str,
        page: mkdocs.structure.pages.Page,
        config: config_options.Config,
        files: mkdocs.structure.files.Files,
        **kwargs: typing.Any,
        ) -> str:
        """
The `page_markdown` event is called after the page's Markdown gets loaded
from its file, and can be used to alter the Markdown source text.
The metadata has been parsed and is available as `page.meta` at this
point.

https://www.mkdocs.org/user-guide/plugins/#on_page_markdown

    markdown:
Markdown source text of the page as a string

    page:
page instance

    config:
global configuration object

    files:
file list

    returns:
Markdown source text of this page as a string
"""
        return markdown


    def on_page_content (
        self,
        html,
        page: mkdocs.structure.pages.Page,
        config: config_options.Config,
        files: mkdocs.structure.files.Files,
        **kwargs: typing.Any,
        ):
        """
https://www.mkdocs.org/user-guide/plugins/#on_page_content
        """
        return html


    def on_page_context (
        self,
        context: dict,
        page: mkdocs.structure.pages.Page,
        config: config_options.Config,
        nav: mkdocs.structure.nav.Navigation,
        **kwargs: typing.Any,
        ) -> dict:
        """
https://www.mkdocs.org/user-guide/plugins/#on_page_context
        """
        return context


    def on_post_page (
        self,
        output_content,
        page: mkdocs.structure.pages.Page,
        config: config_options.Config,
        **kwargs: typing.Any,
        ):
        """
https://www.mkdocs.org/user-guide/plugins/#on_post_page
        """
        return output_content


    def on_post_build (
        self,
        config: config_options.Config,
        **kwargs: typing.Any,
        ) -> None:
        """
Run on post build.

https://www.mkdocs.org/user-guide/plugins/#on_post_build
        """
        return


    def on_serve (
        self,
        server,
        **kwargs: typing.Any,
        ):
        """
https://www.mkdocs.org/user-guide/plugins/#on_serve
        """
        return server
