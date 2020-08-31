# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
from glob import glob
import shutil
import re
from pathlib import Path
sys.path.insert(0, os.path.abspath('./../software'))


# -- Project information -----------------------------------------------------

project = 'ChipWhisperer'
copyright = "2020, NewAE Technology Inc."
author = "NewAE Technology Inc."

# The full version, including alpha/beta/rc tags
release = '5.3.1'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
	'sphinx.ext.napoleon',
	'sphinx.ext.autodoc',
	'sphinx.ext.todo',
    'sphinxcontrib.images'
]

# explicitly set the master document to index.rst
master_doc = 'index'

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

html_theme_options = {
    'description': 'Side-Channel analysis tool-chain.',
    'fixed_sidebar': 'true',
    'logo': 'logo.png',
    'logo_name': 'true',
    'github_user': 'newaetech',
    'github_repo': 'chipwhisperer',
    'github_banner': 'true',
    'github_button': 'true',
    'github_type': 'watch',
    'extra_nav_links': {
        'Hardware Docs': 'https://rtfm.newae.com',
        'Our Source Code': 'https://github.com/newaetech/chipwhisperer',
    },
    'sidebar_width': '265px',
    'page_width': '1000px',
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# configuration for todo extension
todo_include_todos = True

# remove module names
add_module_names = False

# side bar customization
html_sidebars = {
    'index': ['about.html', 'navigation.html', 'searchbox.html'],
    '**': ['about_short.html', 'localtoc.html', 'searchbox.html']
}


def create_tutorial_files(app, config):
    """Callback that creates stub ReST files for the tutorials.

    These files will contain the correct links and will always be
    rebuilt.
    """
    print('Generating tutorial stubs with links...')
    tutorials_src_dir = os.path.abspath(os.path.join(app.srcdir, '..', 'tutorials'))
    tutorials_output_dir = os.path.abspath(os.path.join(app.srcdir, 'tutorials'))
    input_image_dir = os.path.join(tutorials_src_dir, 'img')
    output_image_dir = os.path.join(tutorials_output_dir, 'img')

    # remove everything that is autogenerated
    if os.path.isdir(output_image_dir):
        shutil.rmtree(output_image_dir)
    for old_file in glob(os.path.join(tutorials_output_dir, '*.rst')):
        os.remove(old_file)


    # move images over for linking
    if not os.path.isdir(output_image_dir):
        os.mkdir(output_image_dir)

    for image_file in glob(os.path.join(input_image_dir, '*')):
        _, image_name = os.path.split(image_file)
        shutil.copyfile(image_file, os.path.join(output_image_dir, image_name))

    # for tutorial identifier (pa_cpa_1), scope and target
    #p = re.compile(r'([A-Za-z_\d]*)-.*-([^-]*)-([^-]*)\.rst')
    p = re.compile(r'([A-Za-z_ \d]*)-.*-([^-]*)-([^-]*)\.rst')

    generated_files = []
    for file in glob(os.path.join(tutorials_src_dir, "*.rst")):
        filename = os.path.basename(file)
        match = p.match(filename)

        if not match:
            print('Error when using regex on file:', file)
            continue

        tutorial_id, scope, target = match.groups()
        tutorial_name = '{}-{}-{}'.format(tutorial_id, scope, target).lower()
        tutorial_output_name = tutorial_name + '.rst'
        tutorial_output_path = os.path.join(tutorials_output_dir, tutorial_output_name)

        with open(file, 'r', encoding='utf-8') as in_rstfile:
            with open(tutorial_output_path, 'w', encoding='utf-8') as out_rstfile:
                tutorial_link = 'tutorial-' + tutorial_name
                out_rstfile.write('.. role:: raw-latex(raw)\n    :format: latex\n\n')
                out_rstfile.write('.. _{}:\n\n'.format(tutorial_link))
                # ..todo:: get linking to work instead of copying.
                #out_rstfile.write('.. include:: {}'.format(tutorial_input_path))
                out_rstfile.write(in_rstfile.read())

        generated_files.append(tutorial_output_path)

    print('Generated {} tutorial stub files.'.format(len(generated_files)))

    # invalidate the tutorials.rst file
    tutorials_overview_file = os.path.join(app.srcdir, 'tutorials.rst')
    Path(tutorials_overview_file).touch()
    generated_files.append(tutorials_overview_file)


def setup(app):
    app.connect('config-inited', create_tutorial_files)
