

#import sys ; sys.path.insert(0, "../kglab/")
#import kglab

from pprint import pprint
import mkdocs.config
import mkdocs.plugins
import mkdocs.structure.files
import pathlib


class MkRefsPlugin (mkdocs.plugins.BasePlugin):

    config_scheme = (
        ("biblio_graph", mkdocs.config.config_options.Type(str, default="biblio.ttl")),
        ("biblio_page", mkdocs.config.config_options.Type(str, default="biblio.md")),
    )

    def __init__ (self):
        print("__init__", self.config_scheme)

        self.enabled = True
        self.graph_file = None
        self.biblio_file = None


    def on_config (self, config, **kwargs):
        print("on_config")
        pprint(config)

        if self.config["biblio_graph"]:
            self.graph_file = self.config["biblio_graph"]

            biblio_path = pathlib.Path(config["docs_dir"]) / self.graph_file

            #kg = kglab.KnowledgeGraph()
            #kg.load_rdf(biblio_path)
            #pprint(vars(kg))

        return config


    def on_pre_build (self, config, **kwargs):
        print("on_pre_build")
        return


    def on_files (self, files, config, **kwargs):
        print("on_files")
        pprint(files)

        for file in files.documentation_pages():
            print(file.src_path, file.dest_path)

        self.biblio_file = mkdocs.structure.files.File(
            path = config["biblio_page"],
            src_dir = config["docs_dir"],
            dest_dir = config["site_dir"],
            use_directory_urls = config["use_directory_urls"],
            )

        print(self.biblio_file)
        pprint(vars(self.biblio_file))

        biblio_path = pathlib.Path(config["docs_dir"]) / self.biblio_file.src_path

        with open(biblio_path, "w") as f:
            f.write("# Bibliography\n")
            f.write("pls read sekret stuffs\n")

        files.append(self.biblio_file)

        return files


    def on_page_read_source (self, page, config, **kwargs):
        print("on_page_read_source")
        pprint(vars(page.file))

        if page.file.abs_src_path == config["biblio_page"]:
            print("FOUND!", config["biblio_page"])

        return None


    ######################################################################
    ## unused events

    def on_env (self, env, config, files, **kwargs):
        return env

    def on_nav (self, nav, config, files, **kwargs):
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
