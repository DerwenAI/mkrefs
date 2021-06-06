#!/usr/bin/env python
# -*- coding: utf-8 -*-
# see license https://github.com/DerwenAI/mkrefs#license-and-copyright

from pprint import pprint
import pathlib
import typer
import yaml

from .glossary import render_glossary
from .biblio import render_biblio
from .util import load_kg


APP = typer.Typer()


@APP.command()
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


@APP.command()
def glossary (  # pylint: disable=W0613
    config_file: str,
    ) -> None:
    """
Command to generate a glossary.
    """
    config_path = pathlib.Path(config_file)
    docs_dir = config_path.parent
    local_config = yaml.safe_load(config_path.read_text())

    graph_path = docs_dir / local_config["glossary"]["graph"]
    kg = load_kg(graph_path)

    template_path = docs_dir / local_config["glossary"]["template"]
    markdown_path = docs_dir / local_config["glossary"]["page"]

    groups = render_glossary(local_config, kg, template_path, markdown_path)
    pprint(groups)


def cli () -> None:
    """
Entry point for Typer-based CLI.
    """
    APP()
