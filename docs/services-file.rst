*************
Services File
*************

.. role:: py(code)
   :language: python

.. role:: js(code)
   :language: JavaScript


To connect the collation editor to your own database or platform a services file must be provided. Some variables and
functions are required, others are optional and additional configuration can also be added. The first two types are
described in this section and the configuration additions are explained in the configuration section.

On loading the services file must call :js:`CL.setServiceProvider()` passing a reference to the service file object as
the argument.

Example services files can be found in the contrib directory.

Project configuration files should not contains JavaScript functions directly but should include references to
functions available in the static files on the server and imported using the :js:`localJavaScript` variable.


Required Service File Variables
===============================


.. confval:: supportedRuleScopes

    :type: JSON

    The collation editor supports four different rules scopes.

    * once - this place in this specified witness
    * verse - everywhere in every witness for this verse/collation unit
    * manuscript - everywhere in this specified witness
    * always - everywhere in every witness

    You can decide which of these you want your system to support and must ensure that the selected scopes can be stored
    and retrieved through the services file. The file based system offered in the standalone collation editor only supports
    two scopes (once and always) due to the storage and retrieval limitations.

    This variables is a JSON object in which the supported rule scopes as a string are each a key, the string must match
    the one in the list above. The value of the key is what is used in the drop down box when users select the scope for
    the rule they are creating. This can be any string that will adequately describe the scope for your users.

    In future releases it may be possible for projects to limit the supported rules scopes to a subset of those provided by
    the services and also to change the value of the string displayed to users. Some of the key names may also be changed
    in future versions to be more generic (verse and manuscript in particular).

    An example for a system that supports once and always rule scopes is as follows:

    .. code-block:: JavaScript

        supportedRuleScopes = {
            "once": "This place, these wits",
            "always": "Everywhere, all wits"
        };

    

Required Service File Functions
===============================


.. confval:: initialiseEditor()

    :param: project (JSON) - *[optional]* The JSON of the project object.

    This function is called as part of the initialisation sequence.

    The only requirement for this function is that it set :js:`CL.managingEditor` to either :js:`true` or :js:`false` 
    depending on whether the current user is the managing editor of the current project.

    If the index page is to be set up with JavaScript using the settings provided in the :js:`contextInput` variable in 
    the services file then the function should call :js:`CL.loadIndexPage()` with the current project as the only argument. 
    If the index page is to be provided in an alternative way they this function must show the index page and set any other 
    platform requirements for its use.

    If :js:`CL.loadIndexPage()` is not used as part of the index page setup then this function also needs to add a button 
    with the id **switch_project_button** and one with the id **project_summary** if those functions are required on the 
    platform. In addition, if you want users to be able to change the collation algorithm settings then a button with 
    the id **collation_settings** should also be added. Details of how to activate the buttons can be found in the relevant 
    entries in the Optional Service File Functions section.


.. confval:: getUserInfo()

    :param: callback (function) - The function to be called on the user data retrieved.

    This function must get the current user details as a JSON object and call :js:`callback()` with the result. The user 
    object itself must contain an **id** key. Any other data can be included in the object returned for use in your other 
    service functions for example :js:`showLoginStatus()` might want to show the username.

.. confval:: getUserInfoByIds()

    :param: ids (array) - A list of user ids.
    :param: callback (function) - The function to be called on the user data.

    This function must resolve a list of user ids into basic user objects and run the callback on the data. The user 
    data should be a JSON object with each provided id as the key to another JSON object which must at a minimum 
    contain an **id** key which should match the top level key and ideally a **name** key to provide the name of the 
    user.

    Given the ids :js:`["JS", "RS"]` the JSON object should be as follows (where name keys are technically optional):

    .. code-block:: json

        {
          "JS": {"id": "JS", "name": "Jane Smith"},
          "RS": {"id": "RS", "name": "Rob Smith"}
        }

.. confval:: applySettings()

    :param: data (JSON) - An object contains a list of tokens in the key **tokens** and the display settings object
            in the key **options**.
    :param: callback (function) - The function to be called on the returned data.

    The function should pass the data object to a Python service and run the callback on the data returned.

    The Python service required is described in the Python services section.
..
    TODO add link to section of python services file


.. confval:: getCurrentEditingProject()

    :param: callback (function) - The function to be called on the project data.

    This function must get the current project details as a JSON object and run the callback data returned. 
    The structure of the project JSON is discussed in the project configuration section.
..
    TODO add link to project configuration


.. confval:: getUnitData()

    :param: context(string) - The reference for the unit required.
    :param: documentIds (array) - The list of ids for the documents required.
    :param: callback (function) - The function to be called on the data returned.


    This function must find all of the JSON data for this context in each of the documents requested. The function 
    should return a dictionary which in its minimal form needs to have a single key **results** which should contain 
    an array of JSON objects. The JSON structure provided for each unit in each document should match the unit 
    structure as described in the data structures section. Pay particular attention to the treatment of lacunose and 
    omitted units which need to be handled in different ways depending on the result required in the collation editor.

    * Any documents that are lacunose for this unit and do not need a special label should be omitted from the data 
      set entirely.

    * Special category lac readings for which the special category can be determined from the input format of the 
      transcription, such as TEI XML, can be sent in the results data using the following structure outlined in the 
      data structures section.

    * If any special lac labels are required for data that cannot be determined from the input format then a second 
      key can be added to the main data structure with the name **special_categories**. This should contain an array 
      of JSON objects where each object is structured as follows:

      * **label** The string to use as the label in the interface for this special category of lac.
      * **witnesses** An array of sigla for the witnesses that need to be given this label.

    The witnesses listed in the special_categories array structure should not appear elsewhere in the data returned.

    When all of the data has been retrieved the callback should be run on the resulting object.

    **NB:** Until version 2.0.0 this function was called :js:`getVerseData()`, had a boolean :js:`private` as the 
    third argument before the callback and returned a list (which is now the list in the **results** key).


.. confval:: doCollation()

    :param: context (string) - The reference for the unit being collated.
    :param: options (JSON) - A JSON object containing all of the data and settings needed for collation.
    :param: resultCallback (function) - The function called when the collation is complete which displays the data in 
            the collation editor.

    This function should send the options JSON to a python service for collation, the url used for collation can be 
    used to determine whether a project uses the current version of the regularisation system or the legacy version. 
    The options JSON object will contain all the options required for the collation process on the server.

    The python service required for the collation process is explained in the Python/Server functions section.

    When the collation process has completed the JSON response from the Python collation system should be passed to 
    resultCallback.

..
    TODO add link to python server section


.. confval:: saveCollation()

    :param: context (string) - The reference for the unit required.
    :param: collation (JSON) - The collation object to be saved.
    :param: confirm_message (string) - The message to display if the user is required to confirm the save.
    :param: overwrite_allowed (boolean) - A boolean to indicate if the settings say a user can or cannot overwrite an 
            existing saved version.
    :param: no_overwrite_message (string) - The message to display if there is already a saved version and 
            overwrite_allowed is false.
    :param: callback (function) - The function to be called when the save is complete. It should be called with 
            :js:`true` if the save was sucessful and :js:`false` if it was not.

    This function needs to save the collation object in the database. It must be stored in such a way that the 
    :js:`getSavedCollations()` and :js:`loadSavedCollation()` functions can retrieve it.

.. confval:: getSavedCollations()

    :param: context (string) - The reference for the unit required.
    :param: userId (string/int) - *[optional]* the id of the user whose collations are required.
    :param: callback (function) - The function to be called on the retrieved data.

    This should return all of the saved collations of the requested unit restricted by the current project and, if 
    supplied, the provided user id.

    In future versions this function may include an optional projectId parameter rather than using the current project.


.. confval:: loadSavedCollation()

    :param: id (string/int) - The id of the collation object required.
    :param: callback (function) - The function to be called on the retrieved data.

    This should retrieve the collation with the given id and run the callback on the result, if no collation object is 
    found the callback should be run with :js:`null`. The id here is the unique identifier used by the database to 
    refer to this collation.


Optional Service File Variables
===============================

.. confval:: localJavaScript

    :type: array

    This variable should be an array of strings giving the full url of any additional JavaScript you need the 
    collation editor to load. These might be required run the services for your framework (an internal api file 
    for example) or you might want to use additional files to store configuration functions that you call in the 
    services. These files will be loaded as part of the collation editor initialisation functions called after the 
    services have been set.


.. confval:: localCollationFunction

    :type: JSON

    **This variable can be overwritten in individual project settings (but this may not be advisable)**

    **There is a default provided in core code which uses the collateX Java microservices**

    This variable can be used to configure an alternative method of interacting with collateX, or, assuming the output 
    format is the same as the JSON output provided by collateX replacing it with a different collation service. By 
    default the collation editor will use the collateX java microservices running at the default port (7369) at 
    localhost.

    the configuration should be provided as a JSON object with the following keys:

    * **python_file** *[string]* - The import path for the python file containing the class.
    * **class_name** *[string]* - The name of the class containing the methods.
    * **function** *[string]* - The name of the method of the python class to run for this function.

    The method will be provided with the data to collate in the JSON format required by collateX and an optional 
    dictionary of collateX settings requested by the user such as what algorithm to use and whether or not to use 
    the Levenshtein distance matching.

    The reference python function should return the JSON output from collateX or equivalent.


.. confval:: collatexHost

    :type: url

    **There is a default in the core code which is explained below**

    This variable should be used if the system uses the collateX Java microservices and they are not running at the 
    default location of :code:`http://localhost:7369/collate`. The variable should provide the full url at which the 
    collateX microservices can be found. If the :js:`localCollationFunction` has been set then that function will 
    be used rather than the microservices and this variable will not be used.


.. confval:: collationAlgorithmSettings

    :type: JSON

    **This variable can be overwritten in individual project settings**

    **There is a default in the core code which is explained below**

    This variable is used to set the starting point for the algorithm settings to be used for collateX. The data 
    should be provided in a JSON object with the following keys:

    * **algorithm** *[string]* - The name of the algorithm to use for collateX. This can be any algorithm supported 
      by the version of collateX you are running. You can also use the string 'auto' which will allow the collation 
      preprocessor to make a decision for you. This is probably not optimised for any projects other than the Greek 
      New Testament and should be avoided outside this field.
    * **fuzzy_match** *[boolean]* - A boolean to tell collateX whether or not to use fuzzy matching
    * **distance** *[integer]* - The value to be used for the fuzzy match distance (this will only be used if the 
      fuzzy match boolean is also true).

    The default setting in the code will use the Dekker algorithm with fuzzy matching turned on and a distance of 2.

    If :js:`CL.loadIndexPage()` or a button with the id *collation_settings* was provided on the index page then the 
    user can override these settings on a unit by unit basis.

    **NB:** this setting is new in version 2.0.0 and the default settings have changed from previous versions.


.. confval:: lacUnitLabel

    :type: string

    **This variable can be overwritten in individual project settings**

    This variable should be a string and should be the text the collation editor needs to display for any witnesses 
    which are lacunose for the entire collation unit. The default, which will be used if this variable is not present, 
    is 'lac unit'. Until version 2.0.0 the default text was 'lac verse'.


.. confval:: omUnitLabel

    :type: string

    **This variable can be overwritten in individual project settings**

    This variable should be a string and should be the text the collation editor needs to display for any witnesses 
    which omit the entire collation unit. The default, which will be used if this variable is not present, is 
    'om unit'. Until version 2.0.0 the default text was 'om verse'.


.. confval:: showCollapseAllUnitsButton

    :type: boolean

    **This variable can be overwritten in individual project settings**

    This variable is a boolean which determines whether or not to show the button in the footer of all stages of the 
    collation editor which allows all the units to be collapsed to show only the a reading. The default is false. 
    Until version 2.0.0  this button was included by default.

.. confval:: showGetApparatusButton

    :type: boolean

    **This variable can be overwritten in individual project settings**

    This variable is a boolean which determines whether or not to show the button in the footer of the approved stage 
    of the collation editor. When present the button allows the user to download an export of the current unit 
    apparatus based on the settings provided in the :js:`exporterSettings` variable. If this variable is set to 
    true (or the default is being used) then either :js:`getApparatusForContext()` or :js:`apparatusServiceUrl`
    must also be provided in the services file. If neither of these items are available then the get apparatus 
    button will not be shown.

    The default is true which maintains the behaviour of earlier releases.

.. confval:: extraFooterButtons

    :type: JSON

    **This variable can be overwritten in individual project settings on a stage by stage basis but 
    addExtraFooterFunctions() in the services file must provide all the functions added in the projects**

    This variable can be used to add your own custom buttons to the footer of the display in the four stages of the 
    collation editor. Each stage is treated separately. The data should be structured as a JSON object with the 
    stage/s to be modified as the top level key/s using the following values: regularised, set, ordered, approved. 
    The value for each key should be an array of objects where each object has the following two keys:

    * **id** *[string]* - the string to be used in the id attribute of the button
    * **label** *[string]* - the string visible to the user on the created button

    This variable is used just to add the buttons to the GUI in order to make the buttons work the functions must be 
    added in the :js:`addExtraFooterFunctions()` function in the services file using the id provided in this variable 
    to add the function.

    An example of how to add a button to the set variants stage is below:

    .. code-block:: javascript

        extraFooterButtons = {
        "set": [
            {
            "id": "overlap_om_verse",
            "label": "Overlap om verse"
            }
          ]
        };


.. confval:: preStageChecks

    :type: JSON

    **This variable can be overwritten in individual project settings on a stage by stage basis**

    This variable can be used to add additional checks before moving to the next stage of the collation editor. It can 
    be used to enforce particular editorial rules for example.

    The data should be structured as a JSON object with the stage/s to be modified as the top level key/s using the 
    following values: set_variants, order_readings, approve. The key refers to the stage being moved to; so the checks 
    in the key *set_variants* will be run when the *move to set variants* button is clicked in the regularisation screen.

    The value of this key should be an array of JSON objects each with the following three keys:

    * **function** *[string]* - the function to run. The can either be the function itself (in the services file only) 
      or, as in the example below a reference to a function elsewhere such as the JavaScript files listed in the 
      :js:`localJavaScript` variable.
    * **pass_condition** *[boolean]* - the boolean returned from the function if the test has passed and the user may 
      continue to the next stage.
    * **fail_message** *[string]* - the string displayed to the user if a test condition fails and they are prevented 
      from moving to the next stage.

    Functions will be run in the order they are provided in the array.

    If a project wishes to ignore the checks set in the services file for a particular stage without adding any of its 
    own an empty array should be given as the value to the key for that stage.

    The example below shows two checks added between set variants and order readings and a single check between order 
    readings and approved.

    .. code-block:: javascript

        preStageChecks = {
            "order_readings": [
                {
                "function": "LOCAL.are_no_duplicate_statuses",
                "pass_condition": true,
                "fail_message": "You cannot move to order readings while there are duplicate overlapped readings"
                },
                {
                "function": "LOCAL.check_om_overlap_problems",
                "pass_condition": false,
                "fail_message": "You cannot move to order readings because there is a overlapped reading with the status 'overlapped' that has text in the overlapped unit"
                }
            ],
            "approve": [
                {
                    "function": "LOCAL.are_no_disallowed_overlaps",
                    "pass_condition": true,
                    "fail_message": "You cannot approve this verse because it has an overlapped reading which is identical in word range to a main apparatus unit."
                }
            ]
        };


.. confval:: combineAllLacsInOR

    :type: boolean

    **This variable can be overwritten in individual project settings**

    This variable is a boolean. If it is set to true then in the move to order readings any lac readings, whatever 
    their text value on the screen, will be automatically regularised to '<lac>' in every unit. For example 
    '<ill 4 char>' and '<lac 4 char>' would both be regularised to '<lac>'. These regularised readings work as 
    subreadings and can be viewed like all other subreadings in the interface.

    The default is false.

    If you are using special category lac readings and you want these to appear in your final edition then this 
    setting should not be false.


.. confval:: combineAllOmsInOR

    :type: boolean

    **This variable can be overwritten in individual project settings**

    This is a boolean variable. It works in the same was as :js:`combineAllLacsInOR` but with om readings.

    The default is false.


.. confval:: combineAllLacsInApproved

    :type: boolean

    **This variable can be overwritten in individual project settings**

    This is a boolean variable. It works in the same was as :js:`combineAllLacsInOR` but is applied in the approval 
    process. If this change has already been applied in the move to order readings then this boolean, regardless of 
    its settings, has no influence.

    The default is false.

    If you are using special category lac readings and you want these to appear in your final edition then this 
    setting should not be used.


.. confval:: combineAllOmsInApproved

    :type: boolean

    **This variable can be overwritten in individual project settings**

    This is a boolean variable. It works in the same was as :js:`combineAllLacsInApproved` but with om readings. If 
    this change has already been applied in the move to order readings then this boolean, regardless of its settings, 
    has no influence.

    The default is false.


.. confval:: approvalSettings

    :type: JSON

    **This variable can be overwritten in individual project settings**

    The approval settings determine whether or not an approved version of a unit collation can be overwritten. The 
    default setting is that it can be so this only needs to be added if you want to set it to false as default for all 
    projects in the environment. Individual projects can override this explicitly in their own configurations.

    The approvalSettings variable should be a JSON object with the following keys:

    * **allow_approval_overwrite** *[boolean]* - false if overwriting is not allowed, true if it is.
    * **no_overwrite_message** *[string]* - the string displayed to the user if an overwrite is requested but 
      prevented by the settings, ideally it should give the user a suggestion as to how to proceed.

    An example is below:

    .. code-block:: javascript

        approval_settings = {
          "allow_approval_overwrite": false,
          "no_overwrite_message": "This project already has an approved version of this verse. You cannot overwrite this. \nInstead you must recall the approved version using the administration interface."
        };


.. confval:: apparatusServiceUrl

    :type: url

    This variable specifies the location of the apparatus export service on this platform. If the 
    :js:`showGetApparatusButton` is set to true (or the default is used) and :js:`getApparatusForContext()` is not 
    used, then this url must be provided as it is used in the default code used to generate and export the apparatus. 
    It should provide the full path to the apparatus export services as described in the Python services section.


.. confval:: overlappedOptions

    :type: JSON array

    **This variable can be overwritten in individual project settings**

    **There is a default in the core code which just gives the option to treat the reading as a main reading** (this option is always shown even if this variable is provided in services or project)

    This variables controls the additional options that are available for the reading in the top line which it has been made into an overlapped reading. The default, and always present, option 'Make main reading' allows the words used in the overlapping reading to be used as evidence for the top line. The rearranging of these words is permitted out of transcription order as the order of words is often something which leads to overlapping readings being created. Any number of additional options can be added to the menu. This option cannot be overridden by settings and is always present.

    The data for any additional options should be structured as an array of JSON objects. Each object represents an entry in the menu. The object should have the following keys (the final one is optional):

    * **id** *[string]* - The string to be used as the id in the menu item (only used for HTML)
    * **label** *[string]* - The string to display to the user in the menu to explain what this option does.
    * **reading_flag** *[string]* - The string to be used in the data structure to describe the status of this reading 
      (must not contain spaces).
    * **reading_label** *[string]* - The label to use for the reading in the data structure - if the display label 
      needs to be different it can be provided in the reading_label_display key.
    * **reading_label_display** *[string]* - If the display of the label in the collation editor should be different 
      from the reading_label value then it should be provided here.

    An example is below:

    .. code-block:: javascript

        overlappedOptions = [{
            "id": "show_as_overlapped",
            "label": "Show as overlapped",
            "reading_flag": "overlapped",
            "reading_label": "zu",
            "reading_label_display": "↑"
        },
        {
            "id": "delete_reading",
            "label": "Delete reading",
            "reading_flag": "deleted",
            "reading_label": "zu",
        }];


.. confval:: contextInput

    :type: JSON

    **This variable can be overwritten in individual project settings**

    **There is a default in the core code**

    This variable is used to control the way the collation unit is provided to and retrieved from the initial index page of
    the collation editor. There is a default in the core code which will use the form at 
    :code:`CE_core/html_fragments/default_index_input.html`
    and take the collation unit context from the value of the HTML element with the id 'context'.

    The data should be structured as a JSON object with any of the following option keys as required:

    * **form** *[string]* - The string representing the location of the html index file. This value will be appended 
      to the value of :js:`staticUrl`.
    * **result_provider** *[function]* - The function to use to construct the collation context required from the 
      form provided.
    * **onload_function** *[function]* - The function to run when the form loads (for example, this can be used to 
      populate menus from the database).

    An example is below:

    .. code-block:: javascript

        contextInput = {
            "form" : "html/index.html",
            "result_provider" : function () {
                let book, chapter, verse, ref;
                book = document.getElementById('book').value;
                chapter = document.getElementById('chapter').value;
                verse = document.getElementById('verse').value;
                if (book !== 'none' && !CL.isBlank(chapter) && !CL.isBlank(verse)) {
                    ref = book + '.' + chapter + '.' + verse;
                }
                return ref;
            }
        };


.. confval:: displaySettings

    :type: JSON

    **This variable can be overwritten in individual project settings**

    **There is a default provided in default_settings.js**

    The display settings allow the display of the collation editor to be changed. The display settings can only be 
    changed at the regularisation stage. They are applied in python and are supplied as python methods. It is 
    important that any data needed to apply these settings is present in the JSON for the tokens.

    The data should be structured as a JSON object. It should have three top level keys:

    * **python_file** *[string]* - The import path for the python file containing the class.
    * **class_name** *[string]* - The name of the class containing the methods.
    * **configs** *[array]* - A list of JSON objects which each specified the configs for a single condition.

    Each JSON object in the **configs** array should have the following keys:

    * **id** *[string]* - A unique identifier for this setting which should not contain spaces.
    * **label** *[string]* - A human readable name for this display setting.
    * **function** *[string]* - The name of the method of the python class to run for this setting. Requirements of 
      the python method are given below.
    * **apply_when** *[boolean]* - A boolean that states whether the method should be run if the setting is selected 
      (in which case the boolean should be true), or unselected (in which case the boolean should be false)
    * **check_by_default** *[boolean]* - A boolean to determine if this setting should be selected by default or not.
    * **menu_pos** *[integer]* - An integer to describe where in the list of settings this one should appear on the 
      settings menu (use :js:`null` if this is to run behind the scenes and therefore not appear on the menu).
    * **execution_pos** *[integer]* - An integer to determine the order in which settings functions are applied. 
      This can be important in some cases as the settings can interact in different ways depending on the order in 
      which they are applied.

    For an example of the JavaScript configuration see the 
    `default_settings.js <https://github.com/itsee-birmingham/standalone_collation_editor/blob/master/collation/core/static/CE_core/js/default_settings.js>`_ file.


    **Python requirements**

    The method is passed the JSON object for the token and must return the same token with the 'interface' key 
    modified as appropriate for the setting being applied. For example if a setting is provided which hides markers of 
    supplied text then these markers must be removed from the 'interface' key value before returning the token. If a 
    setting for showing expanded form of the word exists then an expanded form of the text should have been stored 
    in the JSON object and this can then be used to replace the interface version. More details of the JSON token 
    structure can be found in the documentation for the standalone collation editor on github. This type of setting 
    where the interface value is swapped for another in the JSON token data is an example of why the order of 
    execution is important. When swapping the interface value it is important that any already applied rules are 
    respected and therefore if an 'n' key is present in the token JSON it should be returned instead of any other 
    value. An example of this is given in the 'expand_abbreviations' method example in the python code below.

    All of the python methods required for the display settings must be supplied in a single class. That means if you 
    want to add to the defaults with your own functions you should copy the default code into your own python class.

    If a settings is required to run behind the scenes then :js:`null` can be provided as the menu_pos value and it 
    will not appear in the menu.

    An example of the python functions can be seen in the `default_implementations.py <https://github.com/itsee-birmingham/collation_editor_core/blob/master/default_implementations.py>`_ 
    file but  a sample of the two methods described above can also be seen below:

    .. code-block:: python

        class ApplySettings(object):

            def expand_abbreviations(self, token):
                if 'n' in token:  # applied rules override this setting
                    token['interface'] = token['n']
                elif 'expanded' in token:
                    token['interface'] = token['expanded']
                return token

            def hide_supplied_text(self, token):
                token['interface'] = re.sub('\[(?!\d)', '', re.sub('(?<!\d)\]', '', token['interface']))
                return token
    

.. confval:: ruleClasses

    :type: JSON

    **This variable can be overwritten in individual project settings**

    **There is a default provided in default_settings.js**

    This variable provides details of the rule classes/categories that will be available for regularising the data. 
    The data should be structured as an array of JSON objects. The JSON object for each rule class should have the 
    keys described below except any that are described as optional which are only required should that particular 
    feature be needed.  

    * **value** *[string]* - The name of the class/category to be used internally to identify it. This must be unique 
      among your specified classes and should not contain spaces.
    * **name** *[string]* - The human readable name for this class of rule.
    * **create_in_RG** *[boolean]* - Set to true if you want this classification to be available in the regularisation 
      screen, false if not.
    * **create_in_SV** *[boolean]* - Set to true if you want this classification to be available in the set variants 
      screen, false if not.
    * **create_in_OR** *[boolean]* - Set to true if you want this classification to be available in the order readings 
      screen, false if not.
    * **identifier** *[string]* - Optional unless any of the three following settings are true. This should be the 
      string which you want to use to identifiy any readings that have been regularised using this type of rule.
    * **suffixed_sigla** *[boolean]* - Set to true if you want the regularisation to be marked by appending the rule 
      classification identifier to the witness siglum.
    * **suffixed_label** *[boolean]* - Set to true if you want the regularisation to be marked by appending the rule 
      classification identifier to the reading label.
    * **suffixed_reading** *[boolean]* - Set to true if you want the regularisation to be marked by appending the rule 
      classification identifier to the reading text.
    * **subreading** *[boolean]* - Set to true if you want readings regularised using this rule to appear as 
      subreadings in the final edition rather than merged with the parent reading, false if not.
    * **keep_as_main_reading** *[boolean]* - Set to true if you want readings regularised with this rule to continue 
      to appear as main readings. This is mostly used when you want to mark readings in some way to explain why they 
      are different from the others rather than for genuine regularisations.

    Not all of the features make sense when combined and not all combinations will work, for example it does not make 
    sense to mark a regularisation with a suffix to the label if you do not want to have it appear as a subreading in 
    the final edition. For clarity when viewing subreadings in set variants or viewing non-edition subreadings in 
    order reading all regularisation classes applied will appear suffixed to the reading label, any labels for 
    categories that do not have 'suffixed_reading' set to true in the settings will appear in parentheses.

    For an example of the JavaScript configuration see the 
    `default_settings.js <https://github.com/itsee-birmingham/standalone_collation_editor/blob/master/collation/core/static/CE_core/js/default_settings.js>`_ file.


.. confval:: ruleConditions

    :type: JSON

    **This variable can be overwritten in individual project settings**

    **There is a default provided in default_settings.js**

    Rule conditions are used to give users the option to specify additional conditions in the application of rules. 
    These rules are applied in python and are supplied as python methods. Examples of when this might be useful are 
    to ignore supplied or unclear markers when applying rules. These are provided in the defaults and are linked to 
    the settings so that if the settings are hiding supplied markers the markers are automatically ignored when making 
    rules. Another circumstance in which they are useful for the New Testament is to restrict the application of a 
    rule only to tokens which have been marked as nomen sacrum in the transcriptions.

    The data should be structured as a JSON object. It should have three top level keys:

    * **python_file** *[string]* - The import path for the python file containing the class
    * **class_name** *[string]* - The name of the class containing the methods
    * **configs** *[array]* - A list of JSON objects which each specified the configs for a single condition

    Each JSON object in the **configs** array should have the following keys (optional keys are marked):

    * **id** *[string]* - a unique identifier for this condition which should not contain spaces
    * **label** *[string]* - a human readable name for this condition
    * **function** *[string]* - the name of the method of the python class to run for this condition.
    * **apply_when** *[boolean]* - a boolean that states whether the method should be run if the condition is selected 
      (in which case the boolean should be true), or unselected (in which case the boolean should be false)
    * **check_by_default** *[boolean]* - a boolean to determine if this condition should be selected by default or not
    * **type** *[string]* - This should contain one of two values depending on what is returned by the function. If 
      the function returns a boolean the string should be 'boolean', if the function modifies the data such as 
      removing supplied markers then this should read 'string_application'.
    * **linked_to_settings** *[boolean]* optional - set to true if this condition should be linked to the display settings.
    * **setting_id** *[string]* optional - the id of the setting to which this condition should be linked. Required 
      if linked_to_settings is true.

    The 'linked_to_settings' key gives you the option to ensure that conditions are selected depending on the value of 
    the setting at the point the rule is made. For example, if you have a setting which hides all the supplied text 
    markers and that is active at the time a rule is made then the ignore supplied makers condition should also be 
    selected since the user has no idea what supplied markers are in the text they are regularising. If the display 
    setting value is the same as the 'apply_when' value of that setting then the condition will be automatically 
    selected and disabled so the user cannot override that selection. it is important that the setting linked to and 
    the condition do the same thing.

    For an example of the JavaScript configuration see the [default_settings.js](https://github.com/itsee-birmingham/standalone_collation_editor/blob/master/collation/core/static/CE_core/js/default_settings.js) file.

    **Python requirements**

    If you specify new rule conditions in the JavaScript they need to be supported by appropriate python code since 
    the rule conditions are applied on the server side.

    The data provided to, and the data returned from, the method differ depending on the method type specified in the config.

    If the method is a boolean type it will be provided with two pieces of data: the JSON for the token and the JSON 
    for the rule. The method should return :py:`True` if the given rule should be applied to the given token and 
    :py:`False` if it should not. For example if a rule has a condition that says it should only be applied to 
    nomena sacra and this token does not have a flag to say that it is one then false would be returned.

    If the method is a string_application type then it will be provided with two pieces of data: the string match for 
    the rule and an array of all the possible matches for the token. (**NB:** please note that the data is provided in 
    reverse order in this type of method than with the boolean type. This may be rectified in future releases.) 
    This type of method must return a tuple of the modified data having applied the condition. The rule match must 
    come first followed by the array of token words. For example if the condition is to ignore supplied markers when 
    applying this rule and the supplied text in your project is indicated by [] then all instances of [ and ] must 
    be removed from the rule match string and all of the token match strings before they are returned.


    The function in the 'function' key in the rule settings will only be called if there is a possibility of the rule 
    being applied. The function is not responsible for the application of the rule itself just applying the single 
    condition it is responsible for.

    All of the python methods required for the rule conditions must be supplied in a single class. That means if you 
    want to add to the defaults with your own functions you should copy the default code into your own python class.


    An example of the python functions can be seen in the `default_implementations.py <https://github.com/itsee-birmingham/collation_editor_core/blob/master/default_implementations.py>`_ 
    file but  a sample of the two methods described above can also be seen below:

    .. code-block:: python

        class RuleConditions(object):

            def match_nomsac(self, token, decision):
                if 'only_nomsac' in decision['conditions'].keys() and decision['conditions']['only_nomsac'] == True \
                    and ('nomSac' not in token.keys() or token['nomSac'] == False):
                    return False
                return True

            def ignore_supplied(self, decision_word, token_words):
                decision_word = re.sub('\[(?!\d)', '', re.sub('(?<!\d)\]', '', decision_word))
                token_words = [re.sub('\[(?!\d)', '', re.sub('(?<!\d)\]', '', w)) for w in token_words]
                return(decision_word, token_words)


.. confval:: exporterSettings

    :type: JSON

    **This variable can be overwritten in individual project settings**

    **There is a default provided in the core exporter factory code**

    The exporter settings are used to control the export of data from the approved collation screen when the 
    'Get Apparatus' button is present. If the function is not required then the button can be hidden by setting 
    the :js:`showGetApparatusButton` variable to :js:`false`. This export is simply intended to be a check point for 
    editors and should be set to provide the best export format for this task. The project summary page or a similar 
    page in the overall platform should also provide options to export much larger units of text and more options 
    can be provided to users in these export functions.

    If this variable is used then the following keys must be provided.

    * **python_file** *[string]* - The import path for the python file containing the exporter class
    * **class_name** *[string]* - The name of the exporter class to use
    * **function** *[string]* - The name of the exporter function to call to start the process.

    In addition to these keys an **options** key can be provided which should contain a JSON object. The contents of 
    this object will be passed into the exporter constructor as keyword arguments. The example below shows all of the 
    options supported by the default exporter provided with the collation editor code along with the default values. 
    This object can contain any keys that are accepted as keyword arguments by the function and python class in the 
    exporterSettings. If you want to pass options to the core function then you must also supply the three required 
    keys above. In the example below the default exporter class details are used so can be copied into your code if needed.

    .. code-block:: json

        "exporterSettings": {
            "python_file": "collation.core.exporter",
            "class_name": "Exporter",
            "function": "export_data",
            "options": {
            "format":"positive_xml",
            "negative_apparatus": false,
            "ignore_basetext": false,
            "overlap_status_to_ignore": ["overlapped", "deleted"],
            "consolidate_om_verse": true,
            "consolidate_lac_verse": true,
            "include_lemma_when_no_variants": false
            }
        }



Optional Service File Functions
===============================

.. confval:: showLoginStatus()

    :param: callback (function) - *[optional]* The function to be called when this function completes.

    This function can be used to display the currently logged in user. It is called when pages are displayed. It should 
    get the current user and display the required details in the preferred way for the platform. There is a <div> element 
    on each page that calls this function which has the id 'login_status' which should be used to display the user details. 
    When this is done the function should run the callback if one was provided.


.. confval:: getSavedStageIds()

    :param: context (string) - The reference for the unit required.
    :param: callback (function) - The function to be called on the returned data.

    This function populates the links to saved collations in the footer of the page. This function must get the saved 
    collations for the context belonging to this user and the approved collation from the project even if it does not 
    belong to this user. The callback must be run with the saved objects from the four collation stages as parameters 
    in order of the stages (regularised, set variants, order readings, approved). If there are no saved objects for 
    any of the stages this position in the parameters should be null.


.. confval:: addExtraFooterFunctions()

    This is required if any extra footer buttons are specified in the services file variable :js:`extraFooterButtons`. 
    It must attach onclick listeners to all of the buttons specified in the variable. This function must cover all 
    buttons added in the services file and in any projects hosted on the system.


.. confval:: getAdjoiningUnit()

    :param: context (string) - The unit reference for the current unit.
    :param: isPrevious (boolean) - This should be true when looking for the previous unit, false when looking for the next unit.
    :param: callback (function) - The function to be called on the unit identifier string for the next or previous unit.

    This function is used to provide the data needed move through the data by collation unit using the arrows at the 
    beginning and end of the overtext. It should return either the next (if isPrevious is false) or previous unit 
    based on the provided context. The callback should be run on the string that represents the context string for 
    the next/previous unit. Context here and in the parameters refers to the string used to identify the collation 
    unit. i.e. what the user would type into the index page to run a collation for that unit. If no unit is found the 
    callback should be run with :js:`null`.

    **NB** Prior to release 2.0.0 this function was named :js:`getAdjoiningVerse()`


.. confval:: switchProject()

    If this function is present in the services file and :js:`CL.loadIndexPage()` is called by the services as part of 
    the :js:`initialiseEditor()` function in the services then a *switch project* button will be added to the footer 
    of the index page and this function will be attached as an on click event. The function itself should redirect 
    the user to a page that allows them to select a project from the projects they are authorised to access and then 
    return the user to the page they were viewing when they clicked the button.


.. confval:: `viewProjectSummary()

    If this function is present in the services file and :js:`CL.loadIndexPage()` is called by the services as part of 
    the :js:`initialiseEditor()` function in the services then a *view project summary* button will be added to the 
    footer of the index page and this function will be attached as an onclick event. The function itself should 
    redirect the user to a page that shows a summary of the work on the project. This might, for example, include how 
    many of the collation units have been saved at each stage and how many have been approved.


.. confval:: witnessSort()

    :param: witnesses (array) - The list of witness sigla to be sorted.

    | Param  | Type                | Description  |
    | ------ | ------------------- | ------------ |
    | witnesses | <code>array</code> |  |

    **This function can be overridden in individual project settings**

    **There is a default in the core code which just sorts the witnesses as strings**

    This function is used to sort the witness sigla into the desired order. It is used for the hover overs on the 
    readings and to sort menus that list sigla (such as the highlight witness menu). The function should return the 
    sorted list of sigla.


.. confval:: getWitnessesFromInputForm()

    **There is a default in the core code which is explained below**

    This function tells the collation editor how to extract the list of witnesses from the index page. If there is an 
    element on the page with the id *preselected_witnesses* the default code will take that value and split on commas. 
    If there is no such element the default will assume that there is a form with the id *collation_form* which has a 
    series of checkboxes for the witnesses and it will use any values that are selected.

    This default behaviour can be overridden by providing this function in the services. It cannot be overwritten in 
    the project settings so the function must work for all projects you host. The function must return an array 
    containing the ids of the documents selected for collation.


.. confval:: getApparatusForContext()

    :param: callback (function) - *[optional]* A function to be called when this function completes.

    **There is a default in the core code which is explained below**

    This function can be used to override the default export function in the collation editor core code. If this 
    function is not provided and the default code used then the :js:`apparatusServiceUrl` variable must be set so that 
    the default code can find the python service. The default function will probably be good enough for many use cases 
    as it generates the file download based on the settings specified in the :js:`exporterSettings` variable in the 
    services file. It can be useful to override the function if a CSRF token is required by the platform to download 
    the output or to control other aspects of the export.

    *NB* If you do implement this function, the data exported should not be taken from the :js:`CL.data` value. 
    Instead the unit should be retrieved from the database and the 'structure' value from the collation object should 
    be used for the data. This is because, in some circumstances, the data stored in the JavaScript variable 
    :js:`CL.data` is not suitable for export if the 'show non-edition subreadings' button has been used. The version 
    of the data in the database is always correct as the approved version cannot be saved other than in the approval 
    process itself.

    *NB* If you do implement this function there is a pre 2.0 version bug you need to be aware of should any of your 
    user's projects make use of regularisation rules which have the 'keep_as_main_reading' option set to 'true'.
    If this is the case, then the rule configurations must be provided in the 'options' key in the exporterSettings 
    as the display settings for these rules are added in the exporter. The rules are available in the 
    :js:`CL.ruleClasses` variable in the JavaScript. In collations approved using the 2.0 release this is no longer 
    necessary as the required presentation data is stored in the collation data structure during the approval process 
    for each unit. If you provide functions to export larger volumes of data you also need to be aware of 
    this and ensure that the rule configurations are provided to the exporter in this case.

    The function has an optional success callback argument which should be run when the function is complete.


.. confval:: extractWordsForHeader()

    :param: data (array) - The list of token objects from the base text.

    **This function can be overwritten in individual project settings**

    **There is a default in the core code which is explained below**

    This function is used to extract the words that appear in the collation editor at the very top of each unit above 
    the numbers. It can be used to both change the visible text and to add css class values to be added to the html so 
    that the presentation can be changed in the html.

    The function is given the token list of the base text. It should return a list of lists where the first item in 
    the inner list is the string to display for the token and the second item in the inner list is a string 
    representing the class values that should be added to the html. If multiple classes need to applied they can be 
    put in a single string value separated by spaces. If not classes need to be added then the second item in the 
    inner list should be an empty string. Any punctuation or other data which should be displayed on the screen should 
    be combined into the display string for the token.

    The default does not add any extra text or classes and maintains the behaviour of previous releases. It extracts 
    the words from the data in the selected base text using the 'original' key if that is present or 't' if it is not. 
    It also adds any punctuation to the words based on the 'pc_before' and 'pc_after' keys.


.. confval:: prepareDisplayString()

    :param: string (string) - The text of the reading.

    **This function should not be used unless there is a very good reason to do so**

    **This function can be overwritten in individual project settings**

    **The default is to leave the provided string untouched**

    This function is called every time a reading is displayed in the collation editor (not including the full text of 
    the highlighted witness that appears at the bottom of the screen). It is given the string from the data structure 
    and must return the string with any required changes.

    There are probably very few, if any, good reasons to use this. It is present to support some very early 
    implementations while the system was being developed.


.. confval:: prepareNormalisedString()

    :param: string (string) - The display string of the reading.


    **This function must be provided if prepareDisplayString() is used**

    **This variable can be overwritten in individual project settings**

    **The default is to leave the provided string untouched**

    This function is required if :js:`prepareDisplayString()` is used. It must exactly reverse the changes made to the 
    string by that function. It is used when making regularisation rules to ensure the stored strings are what is 
    expected and can be transformed by :js:`prepareNormalisedString()` correctly in the display.
