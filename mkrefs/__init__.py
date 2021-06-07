#!/usr/bin/env python
# -*- coding: utf-8 -*-
# see license https://github.com/DerwenAI/mkrefs#license-and-copyright

from .plugin import MkRefsPlugin

from .apidocs import render_apidocs, PackageDoc

from .biblio import render_biblio

from .glossary import render_glossary

from .util import load_kg

from .cli import cli

from .version import __version__
