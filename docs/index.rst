.. Collation Editor Core documentation master file, created by
   sphinx-quickstart on Fri Apr 21 13:55:15 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

******************************
Collation Editor Documentation
******************************

.. role:: python(code)
   :language: python

.. role:: js(code)
   :language: JavaScript

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Getting Started:

   Standalone Collation Editor <standalone-getting-started.rst>
   Collation Editor Core <core-getting-started.rst>


.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Preparing Your Own Data:

   installation.rst


.. toctree::
   :maxdepth: 3
   :hidden:
   :caption: Reference:

   upgrade.rst
   changelog.rst


The collation editor is a GUI wrapper around `collateX <https://collatex.net/>`_. It is designed to assist in the 
production of critical editions. The collation editor can be configured to work with different languages and 
different editorial approaches. All data input is in JSON.

This documentation covers two different versions of the collation editor:

* **Collation Editor Core** is the core code. This code needs to be embedded into a larger platform with a database or
  similar storage. The connections to the larger platform are made with a services file written in JavaScript.

* The **Standalone Collation Editor** provides a file storage wrapper for the core code and can be downloaded and run
  locally without the need for a database. 

Terminology
===========
For the purposes of this documentation the Documents/Works/Texts model will be used.
(See D.C. Parker, *Textual Scholarship and the making of the New Testament* Oxford: OUP (2011), pp. 10-14,29)

- **Document** - The physical artefact on which the text of a work is preserved
- **Work** - The work which is distilled from the texts that exist of it
- **Text** - The version or versions of a work preserved in document

Acknowledgements
================

The software was created by Catherine Smith at the Institute for Textual Scholarship and Electronic Editing (ITSEE) in
the University of Birmingham. The restructuring required for the 1.0 release was completed by Catherine Smith and Troy
A. Griffitts.  The software was developed for and supported by the following research projects:

* The Workspace for Collaborative Editing (AHRC/DFG collaborative project 2010-2013)
* COMPAUL (funded by the European Union 7th Framework Programme under grant agreement 283302, 2011-2016)
* MUYA (funded by the European Union Horizon 2020 Research and Innovation Programme under grant agreement 694612, 2016-2022)
* CATENA (funded by the European Union Horizon 2020 Research and Innovation Programme under grant agreement 770816, 2018-2023)

The collation editor makes use of several third party libraries written and made available by other developers. Details
of sources and licenses are available in the headers of the relevant JavaScript files. The `redips drag and drop library
<https://github.com/dbunic/REDIPS_drag>`_ warrants special mention as it is used for all of the drag and drop interaction.

Citation
========

To cite the collation editor core code please use the doi:   
[![DOI](https://zenodo.org/badge/142011800.svg)](https://zenodo.org/badge/latestdoi/142011800)

To cite the standalone collation editor please use the doi:
[![DOI](https://zenodo.org/badge/142014378.svg)](https://zenodo.org/badge/latestdoi/142014378)


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
