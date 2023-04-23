********************************************
Getting Started: Standalone Collation Editor
********************************************

Requirements
============

The collation editor requires Python3.

The version of collateX packaged with this code requires Java Runtime Environment (JRE) version 8 or higher.

The collation editor has primarily been tested in Firefox but should also work in Chrome and Microsoft edge.

Installation and start up
=========================

.. tab:: On Mac and Linux

    To start the collation editor download the code from github and navigate to the collation_editor directory. 
    From here run the start up script `startup.sh`. This script should start both collateX and the server that runs 
    the collation editor.

    If collate has started successfully you should be able to see it at:
    :code:`localhost:7369`

    If the script has been successful you should be able to see the collation editor when you visit:
    :code:`localhost:8080/collation`


.. tab:: On Windows

    To start the collation editor download the code from github  and navigate to the collation_editor directory. 
    From here run the start up script `startup.bat`. This script should start both collateX and the server that runs 
    the collation editor.

    If collate has started successfully you should be able to see it at:
    :code:`localhost:7369`

    If the collation editor has started successfully you should be able to see the collation editor when you visit:
    :code:`localhost:8080/collation`

Running the example data
========================

Currently there is one example available in the collation editor download, it is in Greek and uses some 
Greek specific configurations rather than the default ones. To run this example start the collation editor following 
the instructions above. Then visit:

:code:`localhost:8080/collation`

In the text box type 'B04K6V23' and hit run collation.

This should provide a collation of all Greek minuscule manuscripts of John 6:23.

Next steps
==========