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
 * `template` – a Jinja2 template to generate the Markdown, e.g., `biblio.jinja`
 * `queries` – SPARQL queries used to extract bibliography data from the knowledge graph

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


## License and Copyright

Source code for **MkRefs** plus its logo, documentation, and examples
have an [MIT license](https://spdx.org/licenses/MIT.html) which is
succinct and simplifies use in commercial applications.

All materials herein are Copyright &copy; 2021 Derwen, Inc.


## Acknowledgements

This plugin code is based on the marvelous examples in
<https://github.com/byrnereese/mkdocs-plugin-template>
with kudos to [@byrnereese](https://github.com/byrnereese/)
and also many thanks to 
[@louisguitton](https://github.com/louisguitton)
and
[@dmccreary](https://github.com/dmccreary)
for their inspiration and insights.