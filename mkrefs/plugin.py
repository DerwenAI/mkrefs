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
        self.total_time = 0

    def on_serve (self, server):
        return server

    def on_pre_build (self, config):
        return

    def on_files (self, files, config):
        return files

    def on_nav (self, nav, config, files):
        return nav

    def on_env (self, env, config, files):
        return env
    
    def on_config (self, config):
        return config

    def on_post_build (self, config):
        return

    def on_pre_template (self, template, template_name, config):
        return template

    def on_template_context (self, context, template_name, config):
        return context
    
    def on_post_template (self, output_content, template_name, config):
        return output_content
    
    def on_pre_page (self, page, config, files):
        print("CONFIG", config)
        return page

    def on_page_read_source (self, page, config):
        return ""

    def on_page_markdown (self, markdown, page, config, files):
        return markdown

    def on_page_content (self, html, page, config, files):
        return html

    def on_page_context (self, context, page, config, nav):
        return context

    def on_post_page (self, output_content, page, config):
        return output_content
