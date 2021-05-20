# mkrefs

MkDocs plugin to generate reference Markdown pages from a knowledge
graph, leveraging
[`kglab`](https://github.com/DerwenAI/kglab).

This plugin code is based on the marvelous examples in
<https://github.com/byrnereese/mkdocs-plugin-template>
with kudos to [@byrnereese](https://github.com/byrnereese/)


## Setup

To install the plugin using pip:

```
pip install mkrefs
```

Then activate the plugin in `mkdocs.yml`:
```yaml
plugins:
  - mkrefs
```


## Configuration

The following parameters are expected:

* `mkrefs_config` - YAML configuration file for MkRefs; defaults to `mkrefs.yml`


## Usage

```
mkrefs biblio docs/mkrefs.yml
```


## See Also

[mkdocs-plugins]: http://www.mkdocs.org/user-guide/plugins/
[mkdocs-template]: https://www.mkdocs.org/user-guide/custom-themes/#template-variables
[mkdocs-block]: https://www.mkdocs.org/user-guide/styling-your-docs/#overriding-template-blocks
