from pathlib import Path

from hat.doit import common
from hat.doit.docs import build_sphinx


build_dir = Path('build')
build_docs_dir = build_dir / 'docs'


def task_clean_all():
    """Clean all"""
    return {'actions': [(common.rm_rf, [build_dir])]}


def task_docs():
    """Build documentation"""
    return {'actions': [(build_sphinx,
                         [Path('docs'), build_docs_dir, 'ATTEST'],
                         {'conf': {'copyright': '2021-2022, Koncar-KOD',
                                   'html_theme': 'furo',
                                   'html_static_path': ['static'],
                                   'html_css_files': ['custom.css'],
                                   'html_use_index': False,
                                   'html_show_sourcelink': False,
                                   'html_show_sphinx': False,
                                   'html_sidebars': {'**': [
                                       "sidebar/brand.html",
                                       "sidebar/scroll-start.html",
                                       "sidebar/navigation.html",
                                       "sidebar/scroll-end.html"]},
                                   'autoclass_content': 'both',
                                   'autodoc_default_options': {
                                       'members': True,
                                       'member-order': 'bysource',
                                       'undoc-members': True,
                                       'show-inheritance': True},
                                   'extensions': [
                                        'sphinx.ext.autodoc',
                                        'sphinx.ext.autosummary',
                                        'sphinx.ext.mathjax',
                                        'sphinx.ext.napoleon',
                                        'sphinxcontrib.programoutput',
                                        'sphinx_mdinclude']}})]}


def task_build_server():
    """Build server additional files"""
    return {'actions': [
        'rst2html docs/server.rst src_py/attest/server/index.html']}
