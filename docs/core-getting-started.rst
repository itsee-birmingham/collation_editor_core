**************************************
Getting Started: Collation Editor Core
**************************************

.. role:: python(code)
   :language: python

.. role:: js(code)
   :language: JavaScript


Requirements
=============

The following are required to run the collation editor code but are not provided in the repository.

* Python3
* JQuery 3 (tested with 3.6.0)
* Pure css
* collateX (by default the Java web services are used but this is configurable)

Other dependencies are provided in the repository.

Installation
============
For the python import statements to work this repository must be a subdirectory of a folder with the name 
:code:`collation`.

Initialising the collation editor
=================================

The HTML file which will contain the collation editor must load in all of the JavaScript and css dependencies listed
above and the :code:`static/CE_core/js/collation_editor.js` file.

The variable :js:`staticUrl` must be set to the full path to the static files on the system.

You will also need a services file as described below to make the connections to your own platform. The path from
staticUrl to the services file must be specified in a :js:`servicesFile` variable.

Once these two variables have been set you need to call :js:`collation_editor.init()`. This will load in all of the
other JavaScript and css files required for the collation editor to work. You may also supply a callback function which
will be run on the completion of the file loading.

Once the services file has loaded it must call :js:`CL.setServiceProvider()` providing itself as the argument. Setting
this will trigger the initialisation of the editor.

An example of the initialisation code.

.. code-block:: html

    <link rel=stylesheet href="collation/pure-release-1.0.0/pure-min.css" type="text/css"/>
    <script type="text/JavaScript" src="collation/js/jquery-3.6.0.min.js"></script>
    <script type="text/JavaScript" src="collation/CE_core/js/collation_editor.js"></script>
    <script type="text/JavaScript">
        const staticUrl = 'http://localhost:8080/collation/';
        const servicesFile = 'js/local_services.js';
        collation_editor.init();
    </script>

Next steps
==========
