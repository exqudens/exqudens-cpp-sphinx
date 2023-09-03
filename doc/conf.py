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
            if isinstance(node, docutils.nodes.Text):
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

    def docxbuilder_fix_desc_content(value):
        logger.info(f"{inspect.currentframe().f_code.co_name}")

        value_nodes = []

        for node in value:
            value_nodes.append(node)

        result = value
        result.clear()

        for node in value_nodes:
            if node.__class__.__name__ == 'paragraph' or node.__class__.__name__ == 'container':
                for n in node:
                    if n.__class__.__name__ == 'Text':
                        paragraph = docutils.nodes.paragraph()
                        paragraph.append(n)
                        result.append(paragraph)
                    else:
                        result.append(n)
            else:
                raise Exception(f"Unexpected node.__class__.__name__: '{node.__class__.__name__}'")

        return result

    def docxbuilder_new_assemble_doctree(self, master, toctree_only):
        logger.info(f"{inspect.currentframe().f_code.co_name}")
        tree = docxbuilder_old_assemble_doctree(self, master, toctree_only)

        if docxbuilder_new_assemble_doctree_log_node_before:
            logger.info(f"{inspect.currentframe().f_code.co_name} log node before")
            log_node(tree)

        if not docxbuilder_new_assemble_doctree_apply:
            return tree

        logger.info(f"{inspect.currentframe().f_code.co_name} find 'desc_content' nodes")
        desc_content_nodes = []
        for node in tree.traverse():
            if node.__class__.__name__ == 'desc_content':
                node['docxbuilder_new_assemble_doctree_index'] = len(desc_content_nodes)
                desc_content_nodes.append(node)
        desc_content_nodes.reverse()
        logger.info(f"{inspect.currentframe().f_code.co_name} found 'desc' nodes len: '{len(desc_content_nodes)}'")

        logger.info(f"{inspect.currentframe().f_code.co_name} process")
        for desc_content_node_index, desc_content_node in enumerate(desc_content_nodes):
            logger.info(f"{inspect.currentframe().f_code.co_name} process 'desc' node {desc_content_node_index + 1} of {len(desc_content_nodes)}")
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

        if docxbuilder_new_assemble_doctree_log_node_after:
            logger.info(f"{inspect.currentframe().f_code.co_name} log node after")
            log_node(tree)

        return tree

    setattr(docxbuilder.DocxBuilder, 'assemble_doctree', docxbuilder_new_assemble_doctree)
