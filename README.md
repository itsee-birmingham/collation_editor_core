Introduction
---
This code is the core of the collation editor. The code in this repository is not designed to run as it is. It needs to
be embedded into a larger platform with a database or similar storage. The connections are made with a services file
written in JavaScript. Further configuration of settings and other options can also be provided if needed. Data input
is all in JSON.

Dependencies
---

The following are required to run the collation editor code but are not provided in the repository.

- Python3
- JQuery 3 (tested with 3.6.0)
- Pure css
- collateX (by default the Java web services are used but this is configurable)

Other dependencies are provided in the repository.

Documentation
---

Documentation is available at 


Referencing
---

To cite the collation editor core code please use the doi:   
[![DOI](https://zenodo.org/badge/142011800.svg)](https://zenodo.org/badge/latestdoi/142011800)

Acknowledgements
---

The software was created by Catherine Smith at the Institute for Textual Scholarship and Electronic Editing (ITSEE) in
the University of Birmingham. The restructuring required for the 1.0 release was completed by Catherine Smith and Troy
A. Griffitts.  The software was developed for and supported by the following research projects:

- The Workspace for Collaborative Editing (AHRC/DFG collaborative project 2010-2013)
- COMPAUL (funded by the European Union 7th Framework Programme under grant agreement 283302, 2011-2016)
- MUYA (funded by the European Union Horizon 2020 Research and Innovation Programme under grant agreement 694612, 2016-2022)
- CATENA (funded by the European Union Horizon 2020 Research and Innovation Programme under grant agreement 770816, 2018-2023)

The collation editor makes use of several third party libraries written and made available by other developers. Details
of sources and licenses are available in the headers of the relevant JavaScript files. The redips drag and drop library
(https://github.com/dbunic/REDIPS_drag) warrants special mention as it is used for all of the drag and drop interaction.





