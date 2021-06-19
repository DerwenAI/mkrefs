#!/usr/bin/env python
# -*- coding: utf-8 -*-
# see license https://github.com/DerwenAI/mkrefs#license-and-copyright

"""
Implementation of apidoc-ish documentation which generates actual
Markdown that can be used with MkDocs, and fits with Diátaxis design
principles for effective documentation.

Because the others really don't.

In particular, this library...

  * is aware of type annotations (PEP 484, etc.)
  * provides non-bassackwards parameter descriptions (eyes on *you*, GOOG)
  * handles forward references (prior to Python 3.8)
  * links to source lines in a Git repo
  * fixes bugs in `typing` and `inspect`
  * does not require use of a separate apidocs plugin
  * uses `icecream` for debugging
  * exists b/c Sphinx sucks

You're welcome.
"""

import inspect
import os
import re
import sys
import traceback
import typing

from icecream import ic  # type: ignore # pylint: disable=E0401
import pathlib

from .util import render_reference


class PackageDoc:
    """
There doesn't appear to be any other Markdown-friendly docstring support in Python.

See also:

  * [PEP 256](https://www.python.org/dev/peps/pep-0256/)
  * [`inspect`](https://docs.python.org/3/library/inspect.html)
    """
    PAT_PARAM = re.compile(r"(    \S+.*\:\n(?:\S.*\n)+)", re.MULTILINE)
    PAT_NAME = re.compile(r"^\s+(.*)\:\n(.*)")
    PAT_FWD_REF = re.compile(r"ForwardRef\('(.*)'\)")


    def __init__ (
        self,
        package_name: str,
        git_url: str,
        class_list: typing.List[str],
        ) -> None:
        """
Constructor, to configure a `PackageDoc` object.

    package_name:
name of the Python package

    git_url:
URL for the Git source repository

    class_list:
list of the classes to include in the apidocs
        """
        self.package_name = package_name
        self.git_url = git_url
        self.class_list = class_list

        self.package_obj = sys.modules[self.package_name]

        # prepare a file path prefix (to remove later, per file)
        pkg_path = os.path.dirname(inspect.getfile(self.package_obj))
        self.file_prefix = "/".join(pkg_path.split("/")[0:-1])

        self.md: typing.List[str] = [
            "# Reference: `{}` package".format(self.package_name),
            ]

        self.meta = {
            "package": self.package_name,
            "git_url": self.git_url,
            "class": {},
            "function": {},
            "type": {},
        }


    def show_all_elements (
        self
        ) -> None:
        """
Show all possible elements from `inspect` for the given package, for
debugging purposes.
        """
        for name, obj in inspect.getmembers(self.package_obj):
            for n, o in inspect.getmembers(obj):
                ic(name, n, o)
                ic(type(o))


    def get_todo_list (
        self
        ) -> typing.Dict[ str, typing.Any]:
        """
Walk the package tree to find class definitions to document.

    returns:
a dictionary of class objects which need apidocs generated
        """
        todo_list: typing.Dict[ str, typing.Any] = {
            class_name:  class_obj
            for class_name, class_obj in inspect.getmembers(self.package_obj, inspect.isclass)
            if class_name in self.class_list
            }

        return todo_list


    def build (
        self
        ) -> None:
        """
Build the apidocs documentation as markdown.
        """
        todo_list: typing.Dict[ str, typing.Any] = self.get_todo_list()

        # markdown for top-level package description
        docstring = self.get_docstring(self.package_obj)
        self.md.extend(docstring)

        self.meta["docstring"] = "\n".join(docstring).strip()

        # find and format the class definitions
        for class_name in self.class_list:
            class_obj = todo_list[class_name]
            self.format_class(class_name, class_obj)

        # format the function definitions and types
        self.format_functions()
        self.format_types()


    def get_docstring (  # pylint: disable=W0102
        self,
        obj: typing.Any,
        parse: bool = False,
        arg_dict: dict = {},
        ) -> typing.List[str]:
        """
Get the docstring for the given object.

    obj:
class definition for which its docstring will be inspected and parsed

    parse:
flag to parse docstring or use the raw text; defaults to `False`

    arg_dict:
optional dictionary of forward references, if parsed

    returns:
list of lines of markdown
        """
        local_md: typing.List[str] = []
        raw_docstring = obj.__doc__

        if raw_docstring:
            docstring = inspect.cleandoc(raw_docstring)

            if parse:
                local_md.append(self.parse_method_docstring(obj, docstring, arg_dict))
            else:
                local_md.append(docstring)

            local_md.append("\n")

        return local_md


    def parse_method_docstring (
        self,
        obj: typing.Any,
        docstring: str,
        arg_dict: dict,
        ) -> str:
        """
Parse the given method docstring.

    obj:
class definition currently being inspected

    docstring:
input docstring to be parsed

    arg_dict:
optional dictionary of forward references

    returns:
parsed/fixed docstring, as markdown
        """
        local_md: typing.List[str] = []

        for chunk in self.PAT_PARAM.split(docstring):
            m_param = self.PAT_PARAM.match(chunk)

            if m_param:
                param = m_param.group()
                m_name = self.PAT_NAME.match(param)

                if m_name:
                    name = m_name.group(1).strip()

                    if name not in arg_dict:
                        code = obj.__code__
                        line_num = code.co_firstlineno
                        module = code.co_filename
                        raise Exception(f"argument `{name}` described at line {line_num} in {module} is not in the parameter list")
                        
                    anno = self.fix_fwd_refs(arg_dict[name])
                    descrip = m_name.group(2).strip()

                    if name == "returns":
                        local_md.append("\n  * *{}* : `{}`  \n{}".format(name, anno, descrip))
                    elif name == "yields":
                        local_md.append("\n  * *{}* :  \n{}".format(name, descrip))
                    else:
                        local_md.append("\n  * `{}` : `{}`  \n{}".format(name, anno, descrip))
            else:
                chunk = chunk.strip()

                if len(chunk) > 0:
                    local_md.append(chunk)

        return "\n".join(local_md)


    def fix_fwd_refs (
        self,
        anno: str,
        ) -> typing.Optional[str]:
        """
Substitute the quoted forward references for a given package class.

    anno:
raw annotated type for the forward reference

    returns:
fixed forward reference, as markdown; or `None` if no annotation is supplied
        """
        results: list = []

        if not anno:
            return None

        for term in anno.split(", "):
            for chunk in self.PAT_FWD_REF.split(term):
                if len(chunk) > 0:
                    results.append(chunk)

        return ", ".join(results)


    def document_method (
        self,
        path_list: list,
        name: str,
        obj: typing.Any,
        func_kind: str,
        func_meta: dict,
        ) -> typing.Tuple[int, typing.List[str]]:
        """
Generate apidocs markdown for the given class method.

    path_list:
elements of a class path, as a list

    name:
class method name

    obj:
class method object

    func_kind:
function kind

    func_meta:
function metadata

    returns:
line number, plus apidocs for the method as a list of markdown lines
        """
        local_md: typing.List[str] = ["---"]

        # format a header + anchor
        frag = ".".join(path_list + [ name ])
        anchor = "#### [`{}` {}](#{})".format(name, func_kind, frag)
        local_md.append(anchor)

        func_meta["ns_path"] = frag

        # link to source code in Git repo
        code = obj.__code__
        line_num = code.co_firstlineno
        file = code.co_filename.replace(self.file_prefix, "")

        src_url = "[*\[source\]*]({}{}#L{})\n".format(self.git_url, file, line_num)  # pylint: disable=W1401
        local_md.append(src_url)

        func_meta["file"] = file
        func_meta["line_num"] = line_num

        # format the callable signature
        sig = inspect.signature(obj)
        arg_list = self.get_arg_list(sig)
        arg_list_str = "{}".format(", ".join([ a[0] for a in arg_list ]))

        local_md.append("```python")
        local_md.append("{}({})".format(name, arg_list_str))
        local_md.append("```")

        func_meta["arg_list_str"] = arg_list_str

        # include the docstring, with return annotation
        arg_dict: dict = {
            name.split("=")[0]: anno
            for name, anno in arg_list
            }

        arg_dict["yields"] = None

        ret = sig.return_annotation

        if ret:
            arg_dict["returns"] = self.extract_type_annotation(ret)

        arg_docstring = self.get_docstring(obj, parse=True, arg_dict=arg_dict)
        local_md.extend(arg_docstring)
        local_md.append("")

        func_meta["arg_dict"] = arg_dict
        func_meta["arg_docstring"] = "\n".join(arg_docstring).strip()

        return line_num, local_md


    def get_arg_list (
        self,
        sig: inspect.Signature,
        ) -> list:
        """
Get the argument list for a given method.

    sig:
inspect signature for the method

    returns:
argument list of `(arg_name, type_annotation)` pairs
        """
        arg_list: list = []

        for param in sig.parameters.values():
            #ic(param.name, param.empty, param.default, param.annotation, param.kind)

            if param.name == "self":
                pass
            else:
                if param.kind == inspect.Parameter.VAR_POSITIONAL:
                    name = "*{}".format(param.name)
                elif param.kind == inspect.Parameter.VAR_KEYWORD:
                    name = "**{}".format(param.name)
                elif param.default == inspect.Parameter.empty:
                    name = param.name
                else:
                    if isinstance(param.default, str):
                        default_repr = repr(param.default).replace("'", '"')
                    else:
                        default_repr = param.default

                    name = "{}={}".format(param.name, default_repr)

                anno = self.extract_type_annotation(param.annotation)
                arg_list.append((name, anno))

        return arg_list


    @classmethod
    def extract_type_annotation (
        cls,
        sig: inspect.Signature,
        ):
        """
Extract the type annotation for a given method, correcting `typing`
formatting problems as needed.

    sig:
inspect signature for the method

    returns:
corrected type annotation
        """
        type_name = str(sig)
        type_class = sig.__class__.__module__

        try:
            if type_class != "typing":
                if type_name.startswith("<class"):
                    type_name = type_name.split("'")[1]

            if type_name == "~AnyStr":
                type_name = "typing.AnyStr"
            elif type_name.startswith("~"):
                type_name = type_name[1:]

        except Exception:  # pylint: disable=W0703
            ic(type_name)
            traceback.print_exc()

        return type_name


    def document_type (
        self,
        path_list: list,
        name: str,
        obj: typing.Any,
        ) -> typing.List[str]:
        """
Generate apidocs markdown for the given type definition.

    path_list:
elements of a class path, as a list

    name:
type name

    obj:
type object

    returns:
apidocs for the type, as a list of lines of markdown
        """
        local_md: typing.List[str] = []

        type_meta = {}
        self.meta["type"][name] = type_meta

        # format a header + anchor
        frag = ".".join(path_list + [ name ])
        anchor = "#### [`{}` {}](#{})".format(name, "type", frag)
        local_md.append(anchor)

        type_meta["ns_path"] = frag

        # show type definition
        local_md.append("```python")
        local_md.append("{} = {}".format(name, obj))
        local_md.append("```")
        local_md.append("")

        type_meta["obj"] = repr(obj)

        return local_md


    @classmethod
    def find_line_num (
        cls,
        src: typing.Tuple[typing.List[str], int],
        member_name: str,
        ) -> int:
        """
Corrects for the error in parsing source line numbers of class methods that have decorators:
<https://stackoverflow.com/questions/8339331/how-to-get-line-number-of-function-with-without-a-decorator-in-a-python-module>

    src:
list of source lines for the class being inspected

    member_name:
name of the class member to locate

    returns:
corrected line number of the method definition
        """
        correct_line_num = -1

        for line_num, line in enumerate(src[0]):
            tokens = line.strip().split(" ")

            if tokens[0] == "def" and tokens[1] == member_name:
                correct_line_num = line_num

        return correct_line_num


    def format_class (
        self,
        class_name: str,
        class_obj: typing.Any,
        ) -> None:
        """
Format apidocs as markdown for the given class.

    class_name:
name of the class to document

    class_obj:
class object
        """
        self.md.append("## [`{}` class](#{})".format(class_name, class_name))  # pylint: disable=W1308

        docstring = class_obj.__doc__
        src = inspect.getsourcelines(class_obj)

        class_meta = {
            "docstring": docstring,
            "method": {},
            }

        self.meta["class"][class_name] = class_meta

        if docstring:
            # add the raw docstring for a class
            self.md.append(docstring)

        obj_md_pos: typing.Dict[int, typing.List[str]] = {}

        for member_name, member_obj in inspect.getmembers(class_obj):
            path_list = [self.package_name, class_name]

            if member_name.startswith("__") or not member_name.startswith("_"):
                if member_name not in class_obj.__dict__:
                    # inherited method
                    continue

                if inspect.isfunction(member_obj):
                    func_kind = "method"
                elif inspect.ismethod(member_obj):
                    func_kind = "classmethod"
                else:
                    continue

                func_meta = {}
                class_meta["method"][member_name] = func_meta

                _, obj_md = self.document_method(path_list, member_name, member_obj, func_kind, func_meta)
                line_num = self.find_line_num(src, member_name)
                obj_md_pos[line_num] = obj_md

        for _, obj_md in sorted(obj_md_pos.items()):
            self.md.extend(obj_md)


    def format_functions (
        self
        ) -> None:
        """
Walk the package tree, and for each function definition format its
apidocs as markdown.
        """
        self.md.append("---")
        self.md.append("## [package functions](#{})".format(self.package_name))

        for func_name, func_obj in inspect.getmembers(self.package_obj, inspect.isfunction):
            if not func_name.startswith("_"):
                func_meta = {}
                self.meta["function"][func_name] = func_meta

                _, obj_md = self.document_method([self.package_name], func_name, func_obj, "function", func_meta)
                self.md.extend(obj_md)


    def format_types (
        self
        ) -> None:
        """
Walk the package tree, and for each type definition format its apidocs
as markdown.
        """
        self.md.append("---")
        self.md.append("## [package types](#{})".format(self.package_name))

        for name, obj in inspect.getmembers(self.package_obj):
            if obj.__class__.__module__ == "typing":
                if not str(obj).startswith("~"):
                    obj_md = self.document_type([self.package_name], name, obj)
                    self.md.extend(obj_md)


def render_apidocs (  # pylint: disable=R0914
    local_config: dict,
    template_path: pathlib.Path,
    markdown_path: pathlib.Path,
    ) -> typing.Dict[str, list]:
    """
Render the Markdown for an apidocs reference page, based on the given
Jinja2 template.

    local_config:
local configuration, including user-configurable includes/excludes

    template_path:
file path for Jinja2 template for rendering an apidocs reference page in MkDocs

    markdown_path:
file path for the rendered Markdown file

    returns:
rendered Markdown
    """
    groups: typing.Dict[str, list] = {}

    package_name = local_config["apidocs"]["package"]
    git_url = local_config["apidocs"]["git"]

    includes = [
        name.strip()
        for name in local_config["apidocs"]["includes"].split(",")
    ]

    pkg_doc = PackageDoc(
        package_name,
        git_url,
        includes,
        )

    try:
        # hardcore debug only:
        #pkg_doc.show_all_elements()

        # build the apidocs markdown
        pkg_doc.build()

        # render the JSON into Markdown using the Jinja2 template
        groups = {
            "package": [ pkg_doc.meta ],
        }

        render_reference(
            template_path,
            markdown_path,
            groups,
        )
    except Exception as e:  # pylint: disable=W0703
        print(f"Error rendering apidocs: {e}")
        traceback.print_exc()

    return groups
