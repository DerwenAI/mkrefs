# MkRefs

The **MkRefs** [plugin](http://www.mkdocs.org/user-guide/plugins/)
for [`MkDocs`](https://www.mkdocs.org/) 
generates reference Markdown pages from a knowledge graph, 
based on the [`kglab`](https://github.com/DerwenAI/kglab) project.

No graph database is required; however, let us know if you'd like to
use one in particular.

There are several planned use cases for the **MkRefs** plugin,
including:

  * *biblio* – semantic bibliography entries, generated from RDF
  * *glossary* – semantic glossary entries, generated from RDF
  * *apidocs* – semantic [*apidocs*](https://pypi.org/search/?q=apidocs) supporting the [Diátaxis](https://derwen.ai/docs/kgl/learn/#a-grammar-of-learning) grammar for documentation, generated as RDF from Python source code
  * *depend* – semantic dependency graph for Python libraries, generated as RDF from `setup.py`
  * *index* – semantic search index, generated as RDF from MkDocs content

Only the *biblio* component has been added to **MkRefs** so far,
although these other components exist in other projects and are being
integrated.


## Why does this matter?

A key takeaway is that many software engineering aspects of open
source projects involve graphs, therefore a knowledge graph can
provide an integral part of an open source repository.
Moreover, by using semantic representation (RDF) projects that
integrate with each other can share (i.e., federate) common resources,
for example to share definitions, analyze mutual dependencies, etc.


## Installation

To install the plugin using `pip`:

```
python3 -m pip install mkrefs
```

Then add the plugin into the `mkdocs.yml` file:
```yaml
plugins:
  - mkrefs
```
In addition, the following configuration parameter is expected:

  * `mkrefs_config` - YAML configuration file for **MkRefs**; e.g., `mkrefs.yml`


## Bibliography

A `biblio` parameter within the configuration file expects four
required sub-parameters:

 * `graph` – an RDF graph represented as a Turtle (TTL) file, e.g., `mkrefs.ttl`
 * `page` – name of the generated Markdown page, e.g., `biblio.md`
 * `template` – a [Jinja2 template](https://jinja.palletsprojects.com/en/3.0.x/) to generate Markdown, e.g., `biblio.jinja`
 * `queries` – [SPARQL queries](https://rdflib.readthedocs.io/en/stable/intro_to_sparql.html) used to extract bibliography data from the knowledge graph

See the [`mkrefs.ttl`](https://github.com/DerwenAI/mkrefs/blob/main/docs/mkrefs.ttl)
file for an example bibliography represented in RDF.
This comes from the documentation for the [`pytextrank`](https://derwen.ai/docs/ptr/biblio/)
open source project.

In the example RDF, the [*bibo*](http://bibliontology.com/) vocabulary represents
bibliographic citations, and the [*FOAF*](http://xmlns.com/foaf/spec/) vocabulary
represents authors.
This also uses two custom OWL relations from the [*derwen*](https://derwen.ai/ns/v1)
vocabulary:

  * `derw:citeKey` – citekey used to identify a bibliography entry within the documentation
  * `derw:openAccess` – open access URL for a bibliography entry (if any)

The `queries` parameter has three required SPARQL queries:

  * `entry` – to select the identifiers for all of the bibliograpy entries
  * `entry_author` – a mapping to indentify author links for each bibliography entry
  * `entry_publisher` - the publisher link for each bibliography entry (if any)

Note that the named of the generated Markdown page for the
bibliography must appear in the `nav` section of your `mkdocs.yml`
configuration file.
See the structure used in this repo for an example.

You may use any valid RDF representation for a bibliography.
Just be sure to change the three SPARQL queries and the Jinja2
template accordingly.

While this example uses an adaptation of the
[MLA Citation Style](https://www.easybib.com/guides/citation-guides/mla-format/mla-citation/),
feel free to modify the Jinja2 template to generate whatever
bibliographic style you need.

Let us know if you need features to parse and generate
[BibTeX](http://www.bibtex.org/).


## Best Practices

Where possible, the bibliography entries should use the conventions at
<https://www.bibsonomy.org/>
for their [*citation keys*](https://bibdesk.sourceforge.io/manual/BibDeskHelp_2.html).

Journal abbreviations should use
[*ISO 4*](https://en.wikipedia.org/wiki/ISO_4) standards, 
for example from <https://academic-accelerator.com/Journal-Abbreviation/System>

Links to online versions of cited works should use
[DOI](https://www.doi.org/)
for [*persistent identifiers*](https://www.crossref.org/education/metadata/persistent-identifiers/).

When available, 
[*open access*](https://peerj.com/preprints/3119v1/)
URLs should be listed as well.


## Usage

The standard way to generate documentation with MkDocs is:
```
mkdocs build
```

However, there's also a command line *entry point* provided:
```
mkrefs biblio docs/mkrefs.yml
```

If you'd prefer to generate a bibliography programmatically within
Python scripts, see the code for usage of the `MkRefsPlugin` class,
plus two utility functions:

  * `load_kg()`
  * `render_biblio()`


## What is going on here?

When the plugin runs,

1. It parses its configuration file to identify the target Markdown page to generate and the Jinja2 template
2. The plugin also loads an RDF graph from the indicated TTL file
3. Three SPARQL queries are run to identify the unique entities to extract from the graph
4. The graph is serialized as [JSON-LD](https://derwen.ai/docs/kgl/ref/#kglab.KnowledgeGraph.save_jsonld)
5. The `author`, `publisher`, and bibliography `entry` entities are used to *denormalize* the graph into a JSON data object
6. The JSON is rendered using the Jinja2 template to generate the Markdown
7. The Markdown page is parsed and rendered by MkDocs as HTML, etc.


## Caveats

While the [`MkDocs`](https://www.mkdocs.org/) utility is astoundingly useful,
its documentation (and coding style) leave much room for improvement.
The [documentation for developing plugins](https://www.mkdocs.org/user-guide/plugins/#developing-plugins)
is not even close to what happens when its code executes.

Consequently, the **MkRefs** project is an attempt to reverse-engineer
the code from many other MkDocs plugins, while documenting its observed
event sequence, required parameters, limitations and workarounds, etc.

Two issues persist, where you will see warnings even though the **MkRefs**
code is handling configuration as recommended:

```
WARNING -  Config value: 'mkrefs_config'. Warning: Unrecognised configuration name: mkrefs_config 
```

and

```
INFO    -  The following pages exist in the docs directory, but are not included in the "nav" configuration:
  - biblio.md 
```

For now, you can simply ignore both of these warnings.
Meanwhile, we'll work on eliminating them.


## License and Copyright

Source code for **MkRefs** plus its logo, documentation, and examples
have an [MIT license](https://spdx.org/licenses/MIT.html) which is
succinct and simplifies use in commercial applications.

All materials herein are Copyright &copy; 2021 Derwen, Inc.


## Acknowledgements

This plugin code is based on the marvelous examples in
<https://github.com/byrnereese/mkdocs-plugin-template>
with kudos to [@byrnereese](https://github.com/byrnereese/),
and also many thanks to 
[@louisguitton](https://github.com/louisguitton),
[@dmccreary](https://github.com/dmccreary),
and
[@LarrySwanson](https://github.com/LarrySwanson)
for their inspiration and insights.
