# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import os
import json
import inspect
from pathlib import Path
from datetime import datetime

import sphinx.util
import mlx.traceability
import docutils.nodes
import docxbuilder


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
generate_include(str(Path(__file__).parent.joinpath('generated', 'designs-1-include.rst')))

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
    docxbuilder_old_assemble_doctree = getattr(docxbuilder.DocxBuilder, 'assemble_doctree')

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
                'math_block',
                'image'
            ]
            wrap_with_paragraph = [
                'emphasis'
            ]
            result = docxbuilder_unwrap(value, class_names=extract_from_paragraph)

            target_class_name = 'list_item'
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

            target_class_name = 'definition'
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

    setattr(docxbuilder.DocxBuilder, 'assemble_doctree', docxbuilder_new_assemble_doctree)
