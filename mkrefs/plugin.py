from mkdocs import utils as mkdocs_utils
from mkdocs.config import config_options, Config
from mkdocs.plugins import BasePlugin
import sys


class MkRefsPlugin (BasePlugin):

    config_scheme = (
        ("biblio_graph", config_options.Type(str, default="biblio.ttl")),
        ("biblio_page", config_options.Type(str, default="biblio.md")),
    )

    def __init__ (self):
        self.enabled = True
        self.graph_file = None


    def on_config (self, config, **kwargs):
        print("CONFIG", config)

        if self.config["biblio_graph"]:
            self.graph_file = self.config["biblio_graph"]

        return config


    def on_serve (self, server, **kwargs):
        return server

    def on_pre_build (self, config, **kwargs):
        return

    def on_files (self, files, config, **kwargs):
        return files

    def on_nav (self, nav, config, files, **kwargs):
        return nav

    def on_env (self, env, config, files, **kwargs):
        return env
    
    def on_post_build (self, config, **kwargs):
        return

    def on_pre_template (self, template, template_name, config, **kwargs):
        return template

    def on_template_context (self, context, template_name, config, **kwargs):
        return context
    
    def on_post_template (self, output_content, template_name, config, **kwargs):
        return output_content
    
    def on_pre_page (self, page, config, files, **kwargs):
        return page

    def on_page_read_source (self, page, config, **kwargs):
        return ""

    def on_page_markdown (self, markdown, page, config, files, **kwargs):
        return markdown

    def on_page_content (self, html, page, config, files, **kwargs):
        return html

    def on_page_context (self, context, page, config, nav, **kwargs):
        return context

    def on_post_page (self, output_content, page, config, **kwargs):
        return output_content
