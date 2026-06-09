# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'FerdoNAN'
copyright = '2026, Fernando'
author = 'Fernando'
release = '2.3.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
exclude_patterns = []

language = 'es'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']

# Extensiones adicionales
extensions.append('sphinx.ext.napoleon')
extensions.append('myst_parser')

# Rutas de los módulos a documentar
import sys
import os
sys.path.insert(0, os.path.abspath('../..'))

# Mock de módulos problemáticos (evita errores de importación)
autodoc_mock_imports = [
    'chromadb',
    'sentence_transformers',
    'transformers',
    'groq',
    'google.generativeai',
    'pythonjsonlogger',
    'psutil',
    'pandas',
    'docx',
]

# Variable para evitar inicialización de logs durante la documentación
os.environ['SPHINX_BUILD'] = '1'

# Tema
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Excluir directorios
exclude_patterns = ['venv', 'backups', 'logs', 'data', 'patches', 'tests', 'scripts', 'tools/native', 'web/templates', 'mcp_servers']
