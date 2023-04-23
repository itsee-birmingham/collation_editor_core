# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Collation Editor'
copyright = '2023, ITSEE, University of Birmingham'
author = 'Catherine Smith'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinxcontrib.spelling',
              'sphinx_inline_tabs'
              ]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
# html_theme_options = {'collapse_navigation': False,
#                       'navigation_depth': -1}

spelling_lang = 'en_GB'


# Extensions to theme docs (adapted from the readthedocs own documentation conf.py file)
def setup(app):
    from sphinx.domains.python import PyField
    from sphinx.util.docfields import Field

    app.add_object_type(
        'confval',
        'confval',
        objname='configuration value',
        indextemplate='pair: %s; configuration value',
        doc_field_types=[
            PyField(
                'type',
                label=('Type'),
                has_arg=False,
                names=('type',),
                bodyrolename='class'
            ),
            PyField(
                'param',
                label=('Param'),
                has_arg=False,
                names=('param',),
                bodyrolename='class'
            ),
            PyField(
                'returns',
                label=('Returns'),
                has_arg=False,
                names=('returns',),
                bodyrolename='class'
            ),
            Field(
                'default',
                label=('Default'),
                has_arg=False,
                names=('default',),
            ),
        ]
    )