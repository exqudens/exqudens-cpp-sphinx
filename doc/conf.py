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

    def docxbuilder_desc_to_container_node(value):
        logger.info(f"{inspect.currentframe().f_code.co_name}")

        if len(value) != 2:
            raise Exception(f"Unexpected value len: {len(value)}")

        if value[0].__class__.__name__ != 'desc_signature':
            raise Exception(f"Unexpected value[0].__class__.__name__: {value[0].__class__.__name__}")

        if value[1].__class__.__name__ != 'desc_content':
            raise Exception(f"Unexpected value[1].__class__.__name__: {value[1].__class__.__name__}")

        if len(value[0]) != 1:
            raise Exception(f"Unexpected value[0].len: {len(value[0])}")

        if value[0][0].__class__.__name__ != 'desc_signature_line':
            raise Exception(f"Unexpected value[0][0].__class__.__name__: {value[0][0].__class__.__name__}")

        for child in value[0][0]:
            if child.__class__.__name__ not in ['target', 'inline', 'desc_name', 'desc_parameterlist']:
                raise Exception(f"Unexpected value[0][0].child.__class__.__name__: {child.__class__.__name__}")

        if len(value[1]) > 2:
            raise Exception(f"Unexpected value[1].len: {len(value[1])}")

        if value[1][0].__class__.__name__ != 'paragraph':
            raise Exception(f"Unexpected value[1][0].__class__.__name__: {value[1][0].__class__.__name__}")

        result = docutils.nodes.container()

        paragraph_desc_signature = docutils.nodes.paragraph()

        for node in value[0][0]:
            if node.__class__.__name__ == 'target':
                pass
            elif node.__class__.__name__ == 'inline':
                paragraph_desc_signature.append(node)
            elif node.__class__.__name__ == 'desc_name':
                for n in node:
                    paragraph_desc_signature.append(n)
            elif node.__class__.__name__ == 'desc_parameterlist':
                for n_i, n in enumerate(node):
                    if n.__class__.__name__ == 'desc_parameter':
                        for i, inline in enumerate(n):
                            if i == 0:
                                inline.insert(0, docutils.nodes.Text('('))
                            if i == len(n) - 1:
                                inline.append(docutils.nodes.Text(')'))
                            paragraph_desc_signature.append(inline)
                    else:
                        raise Exception(f"Unexpected value[0][0][{n_i}].__class__.__name__: '{n.__class__.__name__}'")

        result.append(paragraph_desc_signature)

        for node in value[1]:
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

        logger.info(f"{inspect.currentframe().f_code.co_name} find 'desc' nodes")
        desc_nodes = []
        for node in tree.traverse():
            if node.__class__.__name__ == 'desc':
                node['docxbuilder_new_assemble_doctree_index'] = len(desc_nodes)
                desc_nodes.append(node)
        desc_nodes.reverse()
        logger.info(f"{inspect.currentframe().f_code.co_name} found 'desc' nodes len: '{len(desc_nodes)}'")

        logger.info(f"{inspect.currentframe().f_code.co_name} process")
        for desc_node_index, desc_node in enumerate(desc_nodes):
            logger.info(f"{inspect.currentframe().f_code.co_name} process 'desc' node {desc_node_index + 1} of {len(desc_nodes)}")
            desc_node_parent = desc_node.parent
            if desc_node_parent is None:
                raise Exception(f"desc_node_parent is None")
            docxbuilder_new_assemble_doctree_index = desc_node['docxbuilder_new_assemble_doctree_index']
            for desc_node_parent_child_index, child in enumerate(desc_node_parent):
                if child.__class__.__name__ == 'desc' and child['docxbuilder_new_assemble_doctree_index'] == docxbuilder_new_assemble_doctree_index:
                    old_node = desc_node_parent[desc_node_parent_child_index]
                    new_node = docxbuilder_desc_to_container_node(old_node)
                    desc_node_parent[desc_node_parent_child_index] = new_node

        if docxbuilder_new_assemble_doctree_log_node_after:
            logger.info(f"{inspect.currentframe().f_code.co_name} log node after")
            log_node(tree)

        return tree

    setattr(docxbuilder.DocxBuilder, 'assemble_doctree', docxbuilder_new_assemble_doctree)
