# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import json
import inspect
from pathlib import Path
from datetime import datetime
from collections import deque

import sphinx.util
import mlx.traceability
import docutils.nodes

# docutils
from docutils.nodes import NodeVisitor
from docutils.nodes import TreePruningException

# breathe
from breathe.renderer.filter import FilterFactory
from breathe.renderer.filter import OrFilter
from breathe.renderer.filter import AndFilter
from breathe.renderer.filter import OpenFilter
from breathe.renderer.filter import ClosedFilter
from breathe.renderer.filter import UnrecognisedKindError
from breathe.renderer.filter import Node
from breathe.renderer.filter import Parent
from breathe.renderer.filter import Ancestor
from breathe.renderer.filter import HasAncestorFilter

# docxbuilder
from docxbuilder import DocxBuilder


# -- Project util functions -----------------------------------------------------

def generate_include(
    output_file=None
):
    if output_file is None:
        logger.info(f"-- {inspect.currentframe().f_code.co_name}: skip")
        return

    rst_lines = ['####', 'Test', '####', '', 'Abc.', '']

    logger.info(f"-- {inspect.currentframe().f_code.co_name}: '{output_file}'")

    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    Path(output_file).write_text('\n'.join(rst_lines))


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

logger = sphinx.util.logging.getLogger(__name__)
confJson = json.loads(Path(__file__).parent.joinpath('conf.json').read_text())
projectDir = confJson['PROJECT_DIR']
logger.info(f"-- projectDir: '{projectDir}'")
project = Path(projectDir).joinpath('name-version.txt').read_text().split(':')[0].strip()
logger.info(f"-- project: '{project}'")
copyright = '2023, exqudens'
author = 'exqudens'
release = Path(projectDir).joinpath('name-version.txt').read_text().split(':')[1].strip()
logger.info(f"-- release: '{release}'")
rst_prolog = '.. |project| replace:: ' + project + '\n\n'
rst_prolog += '.. |release| replace:: ' + release + '\n\n'
generate_include(None if confJson.get('PROJECT_GENERATED_INCLUDE_PATH') is None else confJson['PROJECT_GENERATED_INCLUDE_PATH'])

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autosectionlabel',
    'linuxdoc.rstFlatTable',
    'breathe',
    'mlx.traceability',
    'docxbuilder',
    'rst2pdf.pdfbuilder'
]

templates_path = []
exclude_patterns = []

# -- Options for AUTO_SECTION_LABEL output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autosectionlabel.html#configuration

autosectionlabel_prefix_document = True

# -- Options for docutils -------------------------------------------------
docutils_text_visited_nodes_size = 10

# -- Options for TRACEABILITY output -------------------------------------------------
# https://melexis.github.io/sphinx-traceability-extension/configuration.html#configuration

traceability_render_relationship_per_item = True
traceability_notifications = {
    'undefined-reference': 'UNDEFINED_REFERENCE'
}

# -- Options for BREATHE -------------------------------------------------
# https://breathe.readthedocs.io/en/latest/quickstart.html

breathe_projects = {
    'main': str(Path(projectDir).joinpath('build', 'doxygen', 'main', 'xml')),
    'test': str(Path(projectDir).joinpath('build', 'doxygen', 'test', 'xml'))
}
breathe_domain_by_extension = {
    'h': 'c',
    'c': 'c',
    'hpp': 'cpp',
    'cpp': 'cpp'
}
breathe_default_project = confJson['PROJECT_BREATHE_DEFAULT']
breathe_new_create_content_filter_apply = True
breathe_new_create_content_filter_log = False
breathe_new_create_render_filter_apply = True
breathe_new_create_render_filter_log = False

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = [str(Path(mlx.traceability.__file__).parent.joinpath('assets'))]

# -- Options for DOCX output -------------------------------------------------
# https://docxbuilder.readthedocs.io/en/latest/docxbuilder.html#usage

docx_documents = [
    (
        'index',
        confJson['PROJECT_TITLE'].replace(' ', '_') + '.docx',
        {
            'title': project + ' documentation',
            'created': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            'subject': project + '-' + release,
            'keywords': ['sphinx']
        },
        False
    )
]
docx_coverpage = False
docx_style = '' if confJson.get('PROJECT_DOCX_STYLE') is None else confJson['PROJECT_DOCX_STYLE']
docx_pagebreak_before_section = int('0' if confJson.get('PROJECT_DOCX_PAGEBREAK_BEFORE_SECTION') is None else confJson['PROJECT_DOCX_PAGEBREAK_BEFORE_SECTION'])
docxbuilder_new_assemble_doctree_apply = True
docxbuilder_new_assemble_doctree_log = False
docxbuilder_new_assemble_doctree_log_node_before = False
docxbuilder_new_assemble_doctree_log_node_after = False

# -- Options for PDF output -------------------------------------------------
# https://rst2pdf.org/static/manual.html#sphinx

pdf_documents = [
    ('index', confJson['PROJECT_TITLE'].replace(' ', '_'), release, author)
]
pdf_use_toc = True
pdf_use_coverpage = False
#pdf_break_level = 2
#pdf_breakside = 'any'


# -- Project setup -----------------------------------------------------
def setup(app):

    # -- Project setup util functions -----------------------------------------------------
    def to_node_string(node, include_path=True):
        if node is None:
            raise Exception("'node' is None")
        if include_path:
            path = []
            n = node
            while n is not None:
                path.append(n)
                n = n.parent
            path.reverse()
            path.pop(len(path) - 1)
            strings = [i.astext() if isinstance(i, docutils.nodes.Text) else i.__class__.__name__ for i in path]
            node_string = "['" + "', '".join(strings) + "']: '" + (node.astext() if isinstance(node, docutils.nodes.Text) else node.__class__.__name__)
        else:
            node_string = node.astext() if isinstance(node, docutils.nodes.Text) else node.__class__.__name__
        return node_string

    def log_node(node):
        logger.info(f"-- {inspect.currentframe().f_code.co_name} start")
        nodes = node.traverse()
        entries = []
        for node in nodes:
            if isinstance(node, docutils.nodes.Text) or len(node) == 0:
                entry = []
                n = node
                while n is not None:
                    entry.append(n)
                    n = n.parent
                entry.reverse()
                strings = [i.astext() if isinstance(i, docutils.nodes.Text) else i.__class__.__name__ for i in entry]
                entries.append(strings)
        for entry in entries:
            logger.info(f"-- {entry}")
        logger.info(f"-- {inspect.currentframe().f_code.co_name} end")

    def find_nodes(node, class_names=None, index_key=None, include_self=False):
        if class_names is None:
            raise Exception("Unspecified 'class_names'")

        if index_key is None:
            raise Exception("Unspecified 'index_key'")

        result = []

        for n in node.traverse(include_self=include_self):
            if n.__class__.__name__ in class_names:
                n[index_key] = len(result)
                result.append(n)

        return result

    # -- Project docutils setup -----------------------------------------------------
    docutils_text_visited_nodes = deque([], docutils_text_visited_nodes_size)
    docutils_old_dispatch_visit = getattr(NodeVisitor, 'dispatch_visit')

    def docutils_new_dispatch_visit(self, node):
        try:
            if node is not None and node.__class__.__name__ == 'Text':
                docutils_text_visited_nodes.append(node)
            return docutils_old_dispatch_visit(self, node)
        except TreePruningException as e:
            raise e
        except Exception as e:
            for n in docutils_text_visited_nodes:
                logger.error(f"-- {inspect.currentframe().f_code.co_name} (previous): {to_node_string(n)}")
            logger.error(f"-- {inspect.currentframe().f_code.co_name} (current): {to_node_string(node)}")
            logger.error(e, exc_info = True)
            raise e

    setattr(NodeVisitor, 'dispatch_visit', docutils_new_dispatch_visit)

    docutils_old_dispatch_departure = getattr(NodeVisitor, 'dispatch_departure')

    def docutils_new_dispatch_departure(self, node):
        try:
            return docutils_old_dispatch_departure(self, node)
        except TreePruningException as e:
            raise e
        except Exception as e:
            for n in docutils_text_visited_nodes:
                logger.error(f"-- {inspect.currentframe().f_code.co_name} (previous): '{to_node_string(n)}'")
            logger.error(f"-- {inspect.currentframe().f_code.co_name} (current): {to_node_string(node)}")
            logger.error(e, exc_info = True)
            raise e

    setattr(NodeVisitor, 'dispatch_departure', docutils_new_dispatch_departure)

    # -- Project breathe setup -----------------------------------------------------
    breathe_old_create_content_filter = getattr(FilterFactory, 'create_content_filter')

    def breathe_new_create_content_filter(self, kind, options):
        if not breathe_new_create_content_filter_apply:
            return breathe_old_create_content_filter(self, kind, options)

        if breathe_new_create_content_filter_log:
            logger.info(f"-- {inspect.currentframe().f_code.co_name} call")

        if kind not in ["group", "page", "namespace"]:
            raise UnrecognisedKindError(kind)

        node = Node()

        # Filter for public memberdefs
        node_is_memberdef = node.node_type == "memberdef"
        node_is_visible = OrFilter(
            AndFilter(
                OpenFilter() if 'members' in options else ClosedFilter(),
                node.prot == "public"
            ),
            AndFilter(
                OpenFilter() if 'protected-members' in options else ClosedFilter(),
                node.prot == "protected"
            ),
            AndFilter(
                OpenFilter() if 'private-members' in options else ClosedFilter(),
                node.prot == "private"
            )
        )

        visible_members = node_is_memberdef & node_is_visible

        # Filter for public innerclasses
        parent = Parent()
        parent_is_compounddef = parent.node_type == "compounddef"
        parent_is_class = parent.kind == kind

        node_is_innerclass = (node.node_type == "ref") & (node.node_name == "innerclass")
        node_is_visible = OrFilter(
            AndFilter(
                OpenFilter() if 'members' in options else ClosedFilter(),
                node.prot == "public"
            ),
            AndFilter(
                OpenFilter() if 'protected-members' in options else ClosedFilter(),
                node.prot == "protected"
            ),
            AndFilter(
                OpenFilter() if 'private-members' in options else ClosedFilter(),
                node.prot == "private"
            )
        )

        public_innerclass = (
            parent_is_compounddef & parent_is_class & node_is_innerclass & node_is_visible
        )

        return visible_members | public_innerclass

    setattr(FilterFactory, 'create_content_filter', breathe_new_create_content_filter)

    breathe_old_create_render_filter = getattr(FilterFactory, 'create_render_filter')

    def breathe_new_create_render_filter(self, kind, options):
        if not breathe_new_create_render_filter_apply:
            return breathe_old_create_render_filter(self, kind, options)

        if breathe_new_create_render_filter_log:
            logger.info(f"-- {inspect.currentframe().f_code.co_name} call")

        if kind not in ["group", "page", "namespace"]:
            raise UnrecognisedKindError(kind)

        # Generate new dictionary from defaults
        filter_options = dict((entry, "") for entry in self.app.config.breathe_default_members)

        # Update from the actual options
        filter_options.update(options)

        # Convert the doxygengroup members flag (which just stores None as the value) to an empty
        # string to allow the create_class_member_filter to process it properly
        if "members" in filter_options:
            filter_options["members"] = ""

        if "desc-only" in filter_options:
            return self._create_description_filter(True, "compounddef", options)

        node = Node()
        grandparent = Ancestor(2)
        has_grandparent = HasAncestorFilter(2)

        non_class_memberdef = (
            has_grandparent
            & (grandparent.node_type == "compounddef")
            & (grandparent.kind != "class")
            & (grandparent.kind != "struct")
            & (grandparent.kind != "interface")
            & (node.node_type == "memberdef")
        )

        non_class_filter = AndFilter(
            non_class_memberdef,
            OrFilter(
                AndFilter(
                    OpenFilter() if 'members' in options else ClosedFilter(),
                    node.prot == "public"
                ),
                AndFilter(
                    OpenFilter() if 'protected-members' in options else ClosedFilter(),
                    node.prot == "protected"
                ),
                AndFilter(
                    OpenFilter() if 'private-members' in options else ClosedFilter(),
                    node.prot == "private"
                )
            )
        )

        return (
            (self.create_class_member_filter(filter_options) | non_class_filter)
            & self.create_innerclass_filter(filter_options)
            & self.create_outline_filter(filter_options)
        )

    setattr(FilterFactory, 'create_render_filter', breathe_new_create_render_filter)

    # -- Project docxbuilder setup -----------------------------------------------------
    docxbuilder_old_assemble_doctree = getattr(DocxBuilder, 'assemble_doctree')

    def docxbuilder_unwrap(value, class_names=None):
        if class_names is None:
            raise Exception("Unspecified 'class_names'")

        value_nodes = []

        for node in value:
            value_nodes.append(node)

        result = value
        result.clear()

        for node in value_nodes:
            if node.__class__.__name__ == 'paragraph':
                paragraph = docutils.nodes.paragraph()
                for n in node:
                    if n.__class__.__name__ in class_names:
                        if len(paragraph) > 0:
                            result.append(paragraph)
                            paragraph = docutils.nodes.paragraph()
                        result.append(n)
                    else:
                        paragraph.append(n)
                if len(paragraph) > 0:
                    result.append(paragraph)
            else:
                result.append(node)

        return result

    def docxbuilder_fix_node(value):
        if value.__class__.__name__ == 'table':
            for table_node in value:
                if table_node.__class__.__name__ == 'tgroup':
                    for tgroup_node in table_node:
                        if tgroup_node.__class__.__name__ == 'colspec' and tgroup_node.get('colwidth') == 'auto':
                            tgroup_node['colwidth'] = 10000
            return value
        else:
            extract_from_paragraph = [
                'paragraph',
                'bullet_list',
                'enumerated_list',
                'definition_list',
                'table',
                'seealso',
                'desc',
                'math_block',
                'literal_block',
                'image'
            ]
            wrap_with_paragraph = [
                'emphasis'
            ]
            result = docxbuilder_unwrap(value, class_names=extract_from_paragraph)

            target_class_names = ['list_item', 'definition', 'note']
            for target_class_name in target_class_names:
                target_index_key = 'docxbuilder_fix_desc_content_' + target_class_name + '_index'
                target_nodes = find_nodes(result, class_names=[target_class_name], index_key=target_index_key)
                target_nodes.reverse()
                for node in target_nodes:
                    node_parent = node.parent
                    if node_parent is None:
                        raise Exception("'node_parent' is 'None'")
                    target_index = node[target_index_key]
                    for child_index, child in enumerate(node_parent):
                        if child.__class__.__name__ == target_class_name and child[target_index_key] == target_index:
                            old_node = node_parent[child_index]
                            new_node = docxbuilder_unwrap(old_node, class_names=extract_from_paragraph)
                            node_parent[child_index] = new_node

            target_class_name = 'enumerated_list'
            target_index_key = 'docxbuilder_fix_desc_content_' + target_class_name + '_index'
            target_nodes = find_nodes(result, class_names=[target_class_name], index_key=target_index_key)
            target_nodes.reverse()
            for node in target_nodes:
                node['enumtype'] = 'arabic'
                node['prefix'] = ''
                node['suffix'] = '.'
                node['start'] = 1

            target_class_name = 'container'
            target_index_key = 'docxbuilder_fix_desc_content_' + target_class_name + '_index'
            target_nodes = find_nodes(result, class_names=[target_class_name], index_key=target_index_key)
            target_nodes.reverse()
            for node in target_nodes:
                for child_index, child in enumerate(node):
                    if child.__class__.__name__ in wrap_with_paragraph:
                        paragraph = docutils.nodes.paragraph()
                        paragraph.append(child)
                        node[child_index] = paragraph

            return result

    def docxbuilder_new_assemble_doctree(self, master, toctree_only):
        if docxbuilder_new_assemble_doctree_log:
            logger.info(f"-- {inspect.currentframe().f_code.co_name}")

        tree = docxbuilder_old_assemble_doctree(self, master, toctree_only)

        if docxbuilder_new_assemble_doctree_log and docxbuilder_new_assemble_doctree_log_node_before:
            logger.info(f"-- {inspect.currentframe().f_code.co_name} log node before")
            log_node(tree)

        if not docxbuilder_new_assemble_doctree_apply:
            return tree

        if docxbuilder_new_assemble_doctree_log:
            logger.info(f"-- {inspect.currentframe().f_code.co_name} find 'desc_content' nodes")

        class_names = ['section', 'desc_content', 'table']
        index_key = 'docxbuilder_new_assemble_doctree_index'
        nodes = find_nodes(tree, class_names=class_names, index_key=index_key)
        nodes.reverse()

        if docxbuilder_new_assemble_doctree_log:
            logger.info(f"-- {inspect.currentframe().f_code.co_name} found nodes len: '{len(nodes)}'")

        if docxbuilder_new_assemble_doctree_log:
            logger.info(f"-- {inspect.currentframe().f_code.co_name} process")

        for node_index, node in enumerate(nodes):
            if docxbuilder_new_assemble_doctree_log:
                logger.info(f"-- {inspect.currentframe().f_code.co_name} process node {node_index + 1} of {len(nodes)}")

            node_parent = node.parent

            if node_parent is None:
                raise Exception(f"node_parent is None")

            index_value = node[index_key]

            for child_index, child in enumerate(node_parent):
                if (
                        child.__class__.__name__ in class_names
                        and child[index_key] == index_value
                ):
                    old_node = node_parent[child_index]
                    new_node = docxbuilder_fix_node(old_node)
                    node_parent[child_index] = new_node

        if docxbuilder_new_assemble_doctree_log and docxbuilder_new_assemble_doctree_log_node_after:
            logger.info(f"-- {inspect.currentframe().f_code.co_name} log node after")
            log_node(tree)

        return tree

    setattr(DocxBuilder, 'assemble_doctree', docxbuilder_new_assemble_doctree)
