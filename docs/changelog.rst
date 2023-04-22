Changelog
=========

.. role:: python(code)
   :language: python

.. role:: js(code)
   :language: JavaScript

2.x release
-----------

2.0.1
#####

* Bug fixed in the function which combines all lac and/or all om readings in the code to approve a unit. This bug was 
  caused by the introduction of the the settings applier as a service which added an asynchronous call into a sequence 
  of actions which had to be run in a specific order. As the settings are never relevant to lac and om readings the 
  settings applier is now skipped when combining lac and/or om readings.
* The default behaviour of :js:`getApparatusForContext()` has been changed to use the approved version of the data 
  which has been saved rather than the version currently loaded into the interface. This is because the added ability 
  to show the non-edition subreadings on the approved screen changes the data structure in the interface in a way that 
  makes it unsuitable for export if certain conditions exist in the data. There is no problem with always using the 
  saved version as there is no way to save approved data except in the approval process itself. If the services file 
  provides :js:`getApparatusForContext()` this should also be amended to use the saved version of the data.
