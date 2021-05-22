#!/usr/bin/env python
# -*- coding: utf-8 -*-
# see license https://github.com/DerwenAI/mkrefs#license-and-copyright

from pprint import pprint
import pathlib
import typer
import yaml

from .biblio import load_kg, render_biblio

app = typer.Typer()


@app.command()
def biblio (
    config_file: str,
    ) -> None:
    """
Command to generate a bibliography.
    """
    config_path = pathlib.Path(config_file)
    docs_dir = config_path.parent
    local_config = yaml.safe_load(config_path.read_text())

    graph_path = docs_dir / local_config["biblio"]["graph"]
    kg = load_kg(graph_path)

    template_path = docs_dir / local_config["biblio"]["template"]
    markdown_path = docs_dir / local_config["biblio"]["page"]

    groups = render_biblio(local_config, kg, template_path, markdown_path)
    pprint(groups)


@app.command()
def glossary (  # pylint: disable=W0613
    config_file: str,
    ) -> None:
    """
Command to generate a glossary.
    """
    print("glossary", config_file)


def cli () -> None:
    """
Entry point for Typer-based CLI.
    """
    app()
