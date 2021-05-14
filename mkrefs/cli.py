#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pathlib
import typer

from .biblio import load_kg, render_biblio

app = typer.Typer()


@app.command()
def biblio (
    graph:str,
    template:str,
    markdown:str,
    ) -> None:
    """
Command to generate a bibliography.
    """
    kg = load_kg(pathlib.Path(graph))
    render_biblio(kg, pathlib.Path(template), pathlib.Path(markdown))


@app.command()
def glossary (  # pylint: disable=W0613
    graph:str,
    template:str,
    markdown:str,
    ) -> None:
    """
Command to generate a glossary.
    """
    print("glossary", graph)


def cli () -> None:
    """
Entry point for Typer-based CLI.
    """
    app()
