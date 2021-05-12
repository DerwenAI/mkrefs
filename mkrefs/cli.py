#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pathlib
import typer
import typing

from .biblio import load_kg, render_biblio

app = typer.Typer()


@app.command()
def biblio (
    graph:str,
    template:str,
    markdown:str,
    ):
    print("biblio", graph, template, markdown)
    render_biblio(load_kg(graph), pathlib.Path(template), pathlib.Path(markdown))


@app.command()
def glossary (
    graph:str,
    template:str,
    markdown:str,
    ):
    print("glossary", graph)


def cli ():
    app()
