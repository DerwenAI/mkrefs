#!/usr/bin/env python
# -*- coding: utf-8 -*-

import typer
import typing

from .biblio import load_kg, get_jinja2_template, render_biblio

app = typer.Typer()


@app.command()
def biblio (
    graph:str,
    ):
    print("biblio", graph)


@app.command()
def glossary (
    graph:str,
    ):
    print("glossary", graph)


def cli ():
    app()
