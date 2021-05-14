#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MkDocs Plugin.

https://www.mkdocs.org/
https://github.com/DerwenAI/mkrefs
"""

from pprint import pprint  # pylint: disable=W0611
import pathlib
import typing

from mkdocs.config import config_options  # type: ignore  # pylint: disable=E0401
import mkdocs.plugins  # type: ignore  # pylint: disable=E0401
import mkdocs.structure.files  # type: ignore  # pylint: disable=E0401
import mkdocs.structure.nav  # type: ignore  # pylint: disable=E0401
import mkdocs.structure.pages  # type: ignore  # pylint: disable=E0401

import jinja2
import livereload  # type: ignore  # pylint: disable=E0401

from .biblio import load_kg, render_biblio


class MkRefsPlugin (mkdocs.plugins.BasePlugin):
    """
MkDocs plugin for semantic reference pages, constructed from a knowledge graph.
    """

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


    def on_config (  # pylint: disable=W0613
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
the possibly modified global configuration object
        """
        #print("on_config")
        #pprint(config)

        if self.config["mkrefs_bib_graph"]:
            biblio_ttl_path = pathlib.Path(config["docs_dir"]) / self.config["mkrefs_bib_graph"]
            self.biblio_kg = load_kg(biblio_ttl_path)

        return config


    def on_files (  # pylint: disable=W0613
        self,
        files: mkdocs.structure.files.Files,
        config: config_options.Config,
        **kwargs: typing.Any,
        ) -> mkdocs.structure.files.Files:
        """
The `files` event is called after the files collection is populated
from the `docs_dir` parameter.
Use this event to add, remove, or alter files in the collection.
Note that `Page` objects have not yet been associated with the file
objects in the collection.
Use [Page Events](https://www.mkdocs.org/user-guide/plugins/#page-events)
to manipulate page-specific data.

    files:
default global files collection

    config:
the default global configuration object

    returns:
the possibly modified global files collection
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

    def on_pre_build (  # pylint: disable=R0201,W0613
        self,
        config: config_options.Config,
        **kwargs: typing.Any,
        ) -> None:
        """
This event does not alter any variables.
Use this event to call pre-build scripts.

https://www.mkdocs.org/user-guide/plugins/#on_pre_build

    config:
global configuration object
        """
        #print("on_pre_build")
        return


    def on_nav (  # pylint: disable=R0201,W0613
        self,
        nav: mkdocs.structure.nav.Navigation,
        config: config_options.Config,
        files: mkdocs.structure.files.Files,
        **kwargs: typing.Any,
        ) -> mkdocs.structure.nav.Navigation:
        """
The `nav` event is called after the site navigation is created and can
be used to alter the site navigation.

https://www.mkdocs.org/user-guide/plugins/#on_nav

    nav:
the default global navigation object

    config:
global configuration object

    files:
global files collection

    returns:
the possibly modified global navigation object
        """
        #print("on_nav")
        #pprint(vars(nav))
        return nav


    def on_env (  # pylint: disable=R0201,W0613
        self,
        env: jinja2.Environment,
        config: config_options.Config,
        files: mkdocs.structure.files.Files,
        **kwargs: typing.Any,
        ) -> jinja2.Environment:
        """
The `env` event is called after the Jinja template environment is
created and can be used to alter the Jinja environment.

https://www.mkdocs.org/user-guide/plugins/#on_env

    env:
global Jinja environment

    config:
global configuration object

    files:
global files collection

    returns:
the possibly modified global Jinja environment
        """
        #print("on_env")
        #pprint(vars(env))
        return env


    def on_post_build (  # pylint: disable=R0201,W0613
        self,
        config: config_options.Config,
        **kwargs: typing.Any,
        ) -> None:
        """
This event does not alter any variables.
Use this event to call post-build scripts.

https://www.mkdocs.org/user-guide/plugins/#on_post_build

    config:
global configuration object
        """
        return


    def on_pre_template (  # pylint: disable=R0201,W0613
        self,
        template: str,
        template_name: str,
        config: config_options.Config,
        **kwargs: typing.Any,
        ) -> str:
        """
The `pre_template` event is called immediately after the subject
template is loaded and can be used to alter the content of the
template.

https://www.mkdocs.org/user-guide/plugins/#on_pre_template

    template:
the template contents, as a string

    template_name:
filename for the template, as a string

    config:
global configuration object

    returns:
the possibly modified template contents, as string
        """
        return template


    def on_template_context (  # pylint: disable=R0201,W0613
        self,
        context: dict,
        template_name: str,
        config: config_options.Config,
        **kwargs: typing.Any,
        ) -> dict:
        """
The `template_context` event is called immediately after the context
is created for the subject template and can be used to alter the
context for that specific template only.

https://www.mkdocs.org/user-guide/plugins/#on_template_context

    context:
template context variables, as a dict

    template_name:
filename for the template, as a string

    config:
global configuration object

    returns:
the possibly modified template context variables, as a dict
        """
        return context


    def on_post_template (  # pylint: disable=R0201,W0613
        self,
        output_content: str,
        template_name: str,
        config: config_options.Config,
        **kwargs: typing.Any,
        ) -> str:
        """
The `post_template` event is called after the template is rendered,
but before it is written to disc and can be used to alter the output
of the template.
If an empty string is returned, the template is skipped and nothing is
is written to disc.

https://www.mkdocs.org/user-guide/plugins/#on_post_template

    output_content:
output of rendered the template, as string

template_name:
    filename for the template, as a string

config: global configuration object

    returns:
the possibly modified output of the rendered template, as string
        """
        return output_content


    def on_pre_page (  # pylint: disable=R0201,W0613
        self,
        page: mkdocs.structure.pages.Page,
        config: config_options.Config,
        files: mkdocs.structure.files.Files,
        **kwargs: typing.Any,
        ) -> mkdocs.structure.pages.Page:
        """
The `pre_page` event is called before any actions are taken on the
subject page and can be used to alter the `Page` instance.

https://www.mkdocs.org/user-guide/plugins/#on_pre_page

    page:
the default Page instance

    config:
global configuration object

    files:
global files collection

    returns:
the possibly Page instance
        """
        return page


    def on_page_read_source (  # pylint: disable=R0201,W0613
        self,
        page: mkdocs.structure.pages.Page,
        config: config_options.Config,
        **kwargs: typing.Any,
        ) -> typing.Optional[str]:
        """
The `on_page`_read_source event can replace the default mechanism to
read the contents of a page's source from the filesystem.

https://www.mkdocs.org/user-guide/plugins/#on_page_read_source

    page:
the default Page instance

    config:
global configuration object

    returns:
The raw source for a page as unicode string; if `None` is returned, the default loading from a file will be performed.
        """
        return None


    def on_page_markdown (  # pylint: disable=R0201,W0613
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
Markdown source text of the page, as a string

    page:
Page instance

    config:
global configuration object

    files:
file list

    returns:
the possibly modified Markdown source text of this page, as a string
"""
        return markdown


    def on_page_content (  # pylint: disable=R0201,W0613
        self,
        html: str,
        page: mkdocs.structure.pages.Page,
        config: config_options.Config,
        files: mkdocs.structure.files.Files,
        **kwargs: typing.Any,
        ) -> str:
        """
The `page_content` event is called after the Markdown text is rendered
to HTML (but before being passed to a template) and can be used to
alter the HTML body of the page.

https://www.mkdocs.org/user-guide/plugins/#on_page_content

    html:
the HTML rendered from Markdown source, as string

    page:
Page instance

    config:
global configuration object

    files:
global files collection

    returns:
the possibly modified HTML rendered from Markdown source, as string
        """
        return html


    def on_page_context (  # pylint: disable=R0201,W0613
        self,
        context: dict,
        page: mkdocs.structure.pages.Page,
        config: config_options.Config,
        nav: mkdocs.structure.nav.Navigation,
        **kwargs: typing.Any,
        ) -> dict:
        """
The `page_context` event is called after the context for a page is
created and can be used to alter the context for that specific page
only.

https://www.mkdocs.org/user-guide/plugins/#on_page_context

    context:
template context variables, as a dict

    page:
Page instance

    config:
global configuration object

    nav:
global navigation object

    returns:
the possibly modified template context variables, as a dict
        """
        return context


    def on_post_page (  # pylint: disable=R0201,W0613
        self,
        output_content: str,
        page: mkdocs.structure.pages.Page,
        config: config_options.Config,
        **kwargs: typing.Any,
        ) -> str:
        """
The `post_page` event is called after the template is rendered, but
before it is written to disc and can be used to alter the output of
the page.
If an empty string is returned, the page is skipped and nothing gets
written to disk.

https://www.mkdocs.org/user-guide/plugins/#on_post_page

    output:
the default output of the rendered template, as string

    page:
Page instance

    config:
global configuration object

    returns:
the possibly modified output of the rendered template, as string
        """
        return output_content


    def on_serve (  # pylint: disable=R0201,W0613
        self,
        server: livereload.Server,
        config: config_options.Config,
        builder: typing.Any,
        **kwargs: typing.Any,
        ) -> livereload.Server:
        """
The `serve` event is only called when the serve command is used during
development.
It is passed the `Server` instance which can be modified before it is
activated.
For example, additional files or directories could be added to the
list of "watched" files for auto-reloading.

https://www.mkdocs.org/user-guide/plugins/#on_serve

    server:
default livereload.Server instance

    config:
global configuration object

    builder:
a callable which gets passed to each call to `server.watch()`

    returns:
the possibly modified livereload.Server instance
        """
        return server
