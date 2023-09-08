# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sphinx.util
import json
import inspect
import mlx.traceability
import docutils.nodes
import docxbuilder
from pathlib import Path
from datetime import datetime

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

logger = sphinx.util.logging.getLogger(__name__)
confJson = json.loads(Path(__file__).parent.joinpath('conf.json').read_text())
projectDir = confJson['PROJECT_DIR']
logger.info(f"projectDir: '{projectDir}'")
project = Path(projectDir).joinpath('name-version.txt').read_text().split(':')[0].strip()
logger.info(f"project: '{project}'")
copyright = '2023, exqudens'
author = 'exqudens'
release = Path(projectDir).joinpath('name-version.txt').read_text().split(':')[1].strip()
logger.info(f"release: '{release}'")
rst_prolog = '.. |project| replace:: ' + project + '\n\n'
rst_prolog += '.. |release| replace:: ' + release + '\n\n'

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
breathe_default_project = "main"

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
docx_style = '' if 'PROJECT_STYLE_DOCX' not in confJson.keys() or confJson['PROJECT_STYLE_DOCX'] == 'None' else confJson['PROJECT_STYLE_DOCX']
#docx_pagebreak_before_section = 1
docxbuilder_new_assemble_doctree_apply = True
docxbuilder_new_assemble_doctree_log = True
docxbuilder_new_assemble_doctree_log_node_before = True
docxbuilder_new_assemble_doctree_log_node_after = True

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
        logger.info(f"{inspect.currentframe().f_code.co_name} start")
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
            logger.info(f"{entry}")
        logger.info(f"{inspect.currentframe().f_code.co_name} end")

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
                        if n.__class__.__name__ == 'table':
                            for table_node in n:
                                if table_node.__class__.__name__ == 'tgroup':
                                    for tgroup_node in table_node:
                                        if tgroup_node.__class__.__name__ == 'colspec' and tgroup_node.get('colwidth') == 'auto':
                                            tgroup_node['colwidth'] = 10000
                        result.append(n)
                    else:
                        paragraph.append(n)
                if len(paragraph) > 0:
                    result.append(paragraph)
            else:
                result.append(node)

        return result

    def docxbuilder_fix_desc_content(value):
        extract_from_paragraph = [
            'bullet_list',
            'enumerated_list',
            'table',
            'math_block'
        ]
        result = docxbuilder_unwrap(value, class_names=extract_from_paragraph)

        target_index_key = 'docxbuilder_fix_desc_content_list_item_index'
        target_class_name = 'list_item'
        target_nodes = find_nodes(result, class_names = [target_class_name], index_key = target_index_key)
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

        return result

    def docxbuilder_new_assemble_doctree(self, master, toctree_only):
        if docxbuilder_new_assemble_doctree_log:
            logger.info(f"{inspect.currentframe().f_code.co_name}")
        tree = docxbuilder_old_assemble_doctree(self, master, toctree_only)

        if docxbuilder_new_assemble_doctree_log and docxbuilder_new_assemble_doctree_log_node_before:
            logger.info(f"{inspect.currentframe().f_code.co_name} log node before")
            log_node(tree)

        if not docxbuilder_new_assemble_doctree_apply:
            return tree

        if docxbuilder_new_assemble_doctree_log:
            logger.info(f"{inspect.currentframe().f_code.co_name} find 'desc_content' nodes")
        desc_content_nodes = []
        for node in tree.traverse():
            if node.__class__.__name__ == 'desc_content':
                node['docxbuilder_new_assemble_doctree_index'] = len(desc_content_nodes)
                desc_content_nodes.append(node)
        desc_content_nodes.reverse()
        if docxbuilder_new_assemble_doctree_log:
            logger.info(f"{inspect.currentframe().f_code.co_name} found 'desc_content' nodes len: '{len(desc_content_nodes)}'")

        if docxbuilder_new_assemble_doctree_log:
            logger.info(f"{inspect.currentframe().f_code.co_name} process")
        for desc_content_node_index, desc_content_node in enumerate(desc_content_nodes):
            if docxbuilder_new_assemble_doctree_log:
                logger.info(f"{inspect.currentframe().f_code.co_name} process 'desc_content' node {desc_content_node_index + 1} of {len(desc_content_nodes)}")
            desc_content_node_parent = desc_content_node.parent
            if desc_content_node_parent is None:
                raise Exception(f"desc_content_node_parent is None")
            docxbuilder_new_assemble_doctree_index = desc_content_node['docxbuilder_new_assemble_doctree_index']
            for child_index, child in enumerate(desc_content_node_parent):
                if (
                        child.__class__.__name__ == 'desc_content'
                        and child['docxbuilder_new_assemble_doctree_index'] == docxbuilder_new_assemble_doctree_index
                ):
                    old_node = desc_content_node_parent[child_index]
                    new_node = docxbuilder_fix_desc_content(old_node)
                    desc_content_node_parent[child_index] = new_node

        if docxbuilder_new_assemble_doctree_log and docxbuilder_new_assemble_doctree_log_node_after:
            logger.info(f"{inspect.currentframe().f_code.co_name} log node after")
            log_node(tree)

        return tree

    setattr(docxbuilder.DocxBuilder, 'assemble_doctree', docxbuilder_new_assemble_doctree)
