=====
Tasks
=====

FrePPLe provides a list of commands that perform actions on the 
database, the input data and/or the output data.

The commands can be accessed in three different ways:

* From the execution screen: :doc:`/user-interface/execute`
* From the command line: :doc:`/integration-guide/batch-commands`
* Through a web-based API: :doc:`/integration-guide/remote-commands` 

This section provides an overview of the available actions:

* Planning workflows

  * :ref:`runplan`
  * :ref:`scheduletasks`
  * :ref:`exportworkbook`
  * :ref:`importworkbook`
  * :ref:`exporttofolder`
  * :ref:`emailreport`
  * :ref:`importfromfolder`
  * :ref:`runwebservice`
  * :ref:`scenario_copy`
  * :ref:`backup`
  * :ref:`empty`

* Administrator commands

  * :ref:`loaddata`
  * :ref:`createbuckets`
  * :ref:`createdatabase`
  * :ref:`migrate`
  * :ref:`restore`
  * :ref:`createsuperuser`
  * :ref:`changepassword`
  * :ref:`flush`
  
* Developer commands

  * :ref:`shell`
  * :ref:`dbshell`
  * :ref:`runserver`
  * :ref:`runwebserver`
  * :ref:`test`
  * :ref:`dumpdata`
  * :ref:`createmodel`
  * :ref:`forecast_simulation`
  * :ref:`simulation`

The list can be extended with custom commands from extension modules.


Planning workflows
~~~~~~~~~~~~~~~~~~

.. _runplan:

Generate a plan
---------------

This option runs the frePPLe planning engine with the input data from the
database. The planning results are exported back into the database.

Two main plan types can be distinguished, based on whether you want to
see demand OR material, lead time and capacity problems to be shown.

* A **constrained plan** respects all enabled constraints. In case of shortages
  the demand is planned late or short. No any material or capacity shortages
  are present in the plan.

* An **unconstrained plan** shows material, capacity and operation problems
  that prevent the demand from being planned in time. The demand is always met
  completely and on time.

In both the constrained and unconstrained plans you can select which constraints
are considered during plan creation.

This command is available in the user interface, the command line and the web API:

* Execution screen:  
  
  .. image:: /user-interface/_images/execution-plan.png
     :alt: Execution screen - Plan generation

* Command line::

    frepplectl runplan --constraints=15 --plantype=1 --env=fcst,invplan,balancing,supply

* Web API::

    POST /execute/api/runplan/?constraint=15&plantype=1&env=fcst,invplan,balancing,supply

.. _scheduletasks:

Group and schedule tasks
------------------------

With this option a user can execute a sequence of steps together as a group.

The execution of the task group can be triggered manually. Or it can be scheduled automatically
based on a predefined schedule.

Optionally, a email can be sent out upon failure or success of the execution. 

For this task to be available some configuration may be required. On Windows this task
is a front-end for the Windows Task Scheduler, and you need to assure the user running
the web server has access to use it. On Linux this task is a front-end for the at-command,
and you need to edit the /etc/at.allow or /etc/at.deny file to grant access for the user
running the apache web server.

* Execution screen:  
  
  .. image:: /user-interface/_images/execution-scheduletasks.png
     :alt: Execution screen - Group and schedule tasks

* Command line::

    frepplectl scheduletasks --schedule=my_task_sequence

* Web API::

    POST /execute/api/scheduletasks/?schedule=my_task_sequence

.. _exportworkbook:

Export a spreadsheet
--------------------

This task allows you to download the complete model as a single spreadsheet
file. The spreadsheet can be opened with Excel or Open Office.

A separate sheet in the workbook is used for each selected entity.

The exported file can be imported back with the task described just below.

Optionally, you can make your dataset anonymous during the export to hide
sensitive company data. All entities then get a new name during the export. It remains
ABSOLUTELY NECESSARY to carefully review the generated spreadsheet and to remove 
any sensitive data that is still left, such as descriptions, categories, custom
attributes, cost information.

This command is available only in the user interface:

* Execution screen:
  
  .. image:: /user-interface/_images/execution-export.png
     :alt: Execution screen - Spreadsheet export

.. _importworkbook:

Import a spreadsheet
--------------------

This task allows you to import an Excel spreadsheet.

A separate sheet in the workbook is used for each selected entity.

The sheet must have the right names - in English or your language. The first row
in each sheet must contain the column names.

This command is available only in the user interface:

* Execution screen:

  .. image:: /user-interface/_images/execution-import.png
     :alt: Execution screen - Spreadsheet import

.. _exporttofolder:

Export plan result to folder
----------------------------

This task allows exporting data to a set of files in CSV or Excel format.
The purpose of this task is to help the exchange of information with other systems.

The command can easily by customized to export the results you need.

The files are all placed in a folder UPLOADFILEFOLDER/export/, which can be configured
per scenario with the UPLOADFILEFOLDER value in the djangosettings.py file.

The exported files can be accessed from the user interface, or through over a
HTTP(S) web interface.

This command is available in the user interface, the command line and the web API:

* Execution screen:

  .. image:: /user-interface/_images/execution-exportplantofolder.png
     :alt: Execution screen - Export plan data to folder

* Command line::

    frepplectl exporttofolder

* Web API::
    
    Export the planning result files:
    POST /execute/api/exporttofolder/

    Retrieve one of the exported files:
    GET /execute/downloadfromfolder/1/<filename>/
    
.. _emailreport:

Email exported reports
----------------------

Reports that have been exported using *Export plan result to folder* command can be 
emailed to one or more recipients.

Recipients have to be separated by a comma in the *Emails* field.

Selected reports are zipped into a *reports.zip* file that is attached to the email.

In order to have this command working, the EMAIL parameters in the djangosettings.py 
file must be properly configured.

This command is available in the user interface, the command line and the web API:

* Execution screen:

  .. image:: /user-interface/_images/execution-emailreport.png
     :alt: Execution screen - Email exported reports

* Command line::

    frepplectl emailreport [--sender] --recipient --report
    

* Web API::
    
    Email exported reports:
    POST /execute/api/emailreport/?recipient=recipient1,recipient2...&report=report1,report2,report3...


.. _importfromfolder:

Import data files from folder
-----------------------------

This task allows importing data from a set of CSV-formatted files (eventually GZ-compressed).
The purpose of this task is to help the exchange of information with other systems.

The files are all placed in a folder that is configurable per scenario with the
UPLOADFILEFOLDER in the djangosettings.py configuration file. The log file records
all data imports, in addition to any data errors identified during their processing.

The data files to be imported must meet the following criteria:

* | The name must match the data object they store: eg demand.csv, item.csv, item.xlsx, item.csv.gz
  | This is important for frePPLe to understand the correct processing order of the files.
  
* | Multiple files for the same entity can be provided. They will be processed in alphabetical order:
    eg "demand (1).xlsx", "demand (2).csv", "demand.1.csv", "demand.2.csv", "demand.extra.xlsx", "demand.postprocessing.sql" 

* | The first line of the file should contain the field names. The field name can be in English
    or the default language configured with the LANGUAGE_CODE setting.

The following file formats are accepted:

  * | **Excel**:   
    | The file name must end with .xlsx

  * | **CSV**:     
    | The file name must end with .csv (or .csv.gz when compressed with gzip).
    | Some specific notes on the CSV format:

    * The separator in your CSV-files varies with the chosen language: If in your
      language a comma is used as a decimal separator for numbers, the CSV file
      will use a semicolon (;) as delimiter. Otherwise a comma (,) is used.
      See http://en.wikipedia.org/wiki/Decimal_mark

    * The date format expected by frePPLe is 'YYYY-MM-DD HH\:MM\:SS'.

    * The data file is expected to be encoded in the character encoding defined by
      the setting CSV_CHARSET (default UTF-8).
      
  * | **PostgreSQL copy files**:  
    | The file name must end with .cpy (or .cpy.gz when compressed with gzip).
    | Uploading in this format goes MUCH quicker than the other formats. It has some
      limitations however: a) the validation of the input data is not as extensive
      as the other formats, b) a single faulty record will abort the upload and c)
      it only supports adding new records and not updating existing records. 
    | This method is therefore only recommended for loading very large data files
      with clean data.
    
  * | **SQL**:
    | The file name must end with .sql (or .sql.gz when compressed with gzip).
    | For security reasons a database role with a minimal set of permissions must be
      define. The setting DATABASES / SQL_ROLE needs to refer to this role.

In this option you can see a list of files present in the specified folder, and download
each file by clicking on the arrow down button, or delete a file by clicking on the
red button.
The arrow up button will give the user the possibility of selecting multiple files
to upload to that folder.

This command is available in the user interface, the command line and the web API:

* Execution screen:  
  
  .. image:: /user-interface/_images/execution-importfilesfromfolder.png
     :alt: Execution screen - Import data files from folder

* Command line::

    frepplectl importfromfolder

* Web API::

    Upload a data file:
    POST /execute/uploadtofolder/0/ with data files in multipart/form-data format
    
    Import the data files:
    POST /execute/api/importfromfolder/
  
.. _runwebservice:

Web service
-----------

In the Enterprise Edition users have the option to start and stop the web service
which keeps the plan in memory.

.. image:: /user-interface/_images/execution-webservice.png
   :alt: Execution screen - Web service

.. _scenario_copy:

Scenario management
-------------------

This option allows a user to either create copies of a dataset into a
what-if scenario or promote the data from a scenario into *Production* database.

When the data is successfully copied, the status changes from 'Free'
to 'In use'. The access to the newly copied scenario is limited to 1) the
user who performed the copy plus 2) all superusers of the source scenario.

When the user doesn't need the what-if scenario any more, it can be released
again.

Releasing a scenario can be done from any scenario while copying and promoting
actions can only be performed from current scenario to destination scenario. 

The label of a scenario, which is displayed in the dropdown list in the 
upper right hand corner, can also be updated here.

This command is available in the user interface, the command line and the web API:

* Execution screen:  
  
  .. image:: /user-interface/_images/execution-scenarios.png
     :alt: Execution screen - what-if scenarios

* Command line::

    frepplectl scenario_copy [--force --promote] db1 db2

* Web API::

    To copy a scenario (including Production) into another scenario:
    * POST /execute/api/scenario_copy/?copy=1&source=db1&destination=db2&force=1
    
    To promote a scenario into Production (where db2 must be Production):
    * POST /execute/api/scenario_copy/?promote=1&source=db1&destination=db2

.. _backup:

Back up database
----------------

This task dumps the contents of the current database schema to a backup file.
The file is created in the log folder configured in the configuration files
djangosettings.py.

It also removes dumps older than a month to limit the disk space usage. If you
want to keep dumps for a longer period of time, you'll need to copy the backup files
to a different location.

This option is not active for cloud users. We automatically manage the
data backups for cloud users.

This command is available in the user interface, the command line and the web API:

* Execution screen:  

  .. image:: /user-interface/_images/execution-backup.png
     :alt: Execution screen - backup

* Command line::

    frepplectl backup

* Web API::
  
    POST /execute/api/backup/
   
.. _empty:

Empty the database
------------------

This will delete all data from the current scenario (except for some internal
tables for users, permissions, task log, etc...).

This command is available in the user interface, the command line and the web API:

* Execution screen:

  .. image:: /user-interface/_images/execution-erase.png
     :alt: Execution screen - erase

* Command line::

    frepplectl empty --models=input.demand,input.operationplan

* Web API::

    POST /execute/api/empty/?models=input.demand,input.operationplan

Administrator commands
~~~~~~~~~~~~~~~~~~~~~~
     
.. _loaddata:

Load a dataset in the database
------------------------------

A number of demo datasets are packaged with frePPLe. Using this action you can
load one of those in the database.

The dataset is loaded incrementally in the database, **without** erasing any
previous data. In most cases you'll want to erase the data before loading any
of these datasets.

You can use the dumpdata command to export a model to the appropriate format
and create your own predefined datasets.

This command is available in the user interface, the command line and the web API:

* Execution screen:

  .. image:: /user-interface/_images/execution-fixture.png
     :alt: Execution screen - load a dataset

* Command line::

    frepplectl loaddata manufacturing_demo

* Web API::

    POST /execute/api/loaddata/?fixture=manufacturing_demo
    
.. _createbuckets:

Generate time buckets
---------------------

Many output reports are displaying the plan results aggregated into time
buckets. These time buckets are defined with the tables dates and bucket dates.

This tasks allows you to populate these tables in an easy way with buckets
with daily, weekly, monthly, quarterly and yearly granularity. Existing bucket
definitions for these granularities will be overwritten.

The following arguments are used:

* | Start date, end date:
  | Definition of the horizon to generate buckets for.

* Week start: Defines the first date of a week.

* | Day name, week name, month name, quarter name, year name:
  | Template used to generate a name for the buckets.  
  
  Any character can be used in the names and the following format codes can be used:
  
  - %a: Weekday as locale's abbreviated name. Eg: Sun, Mon, ...
  
  - %A: Weekday as locale's full name. Eg: Sunday, Monday, ...
  
  - %w: Weekday as a decimal number, where 0 is Sunday and 6 is Saturday.
  
  - %d: Day of the month as a zero-padded decimal number. Eg: 01, 02, ..., 31
  
  - %b: Month as locale's abbreviated name. Eg: Jan, Feb, ...
  
  - %B: Month as locale's full name. Eg: January, February, ...
  
  - %m: Month as a zero-padded decimal number. Eg: 01, 02, ..., 12   

  - %q: Quarter as a decimal number. Eg: 1, 2, 3, 4

  - %y: Year without century as a zero-padded decimal number. Eg: 00, 01, ..., 99
     
  - %Y: Year with century as a decimal number. Eg: 2018, 2019, ...
  
  - %j: Day of the year as a zero-padded decimal number. Eg: 001, 002, ..., 366
     
  - %U: Week number of the year as a zero padded decimal number. Eg: 00, 01, ...

  - %W: Week number of the year as a decimal number. Eg: 0, 1, ...

  - %%: A literal '%' character.  

This command is available in the user interface, the command line and the web API:

* Execution screen:

  .. image:: /user-interface/_images/execution-buckets.png
     :alt: Execution screen - generate time buckets
   
* Command line::

    frepplectl createbuckets --start=2012-01-01 --end=2020-01-01 --weekstart=1

* Web API::
   
    POST /execute/api/createbuckets/?start=2012-01-01&end=2020-01-01&weekstart=1
    

.. _createdatabase:

Create the PostgreSQL database(s)
---------------------------------

This command will create the PostgreSQl databases for frePPLe.

If the database already exists you will be prompted to confirm whether you 
really to loose all data in the existing database. When confirmed that database
will dropped and recreated.

This command is available on the command line only:

::

    # Create all scenario databases
    frepplectl createdatabase
    
    # Recreate only a single database 
    frepplectl createdatabase --database=scenario3

.. _migrate:

Create or migrate the database schema
-------------------------------------

Update the database structure to the latest release

This command is available on the command line only:

::

    # Migrate the main database
    frepplectl migrate

    # Migrate a scenario database
    frepplectl migrate --database=scenario1
    
.. _restore: 

Restore a database backup
-------------------------

This command is available on the command line only:

::

    frepplectl restore database_dump_file

.. _createsuperuser: 

Create a new superuser
----------------------

This command creates a new user with full access rights.

This action is possible in the user interface and the command line:

* User interface:

  See :doc:`/user-interface/getting-around/user-permissions-and-roles`
   
* Command line::

    frepplectl createsuperuser new_user_name


.. _changepassword: 

Change a user's password
------------------------

This command changes the password of a certain user.

This action is possible in the user interface and the command line:

* User interface:

  See :doc:`/user-interface/getting-around/changing-password` and 
  :doc:`/user-interface/getting-around/user-permissions-and-roles`.
   
* Command line::

    frepplectl changepassword user_name


.. _flush: 

Remove all database objects
---------------------------

This command completely empties all tables in the database, including all log, users,
user preferences, permissions, etc... 

A complete reset of the database is not very common. In most situations the command
described above to empty the database is sufficient. It empties the data tables,
but leaves the important configuration information intact.

This command is available on the command line only:

::

    frepplectl flush


Developer commands
~~~~~~~~~~~~~~~~~~

.. _dbshell:

Database shell prompt
--------------------- 

This command runs an interactive SQL session on the PostgreSQL database.

::

    frepplectl dbshell --database=default


.. _shell:

Python command prompt
---------------------

This command runs an interactive Python interpreter session.

::

    frepplectl shell


.. _dumpdata:  

Dump a frozen dataset
---------------------

Outputs to standard output all data in the database (or a part of it).

When the output file of this command is placed in a fixtures subfolder
it can be used by the loaddata command described above. We recommend you
review and cleanse the output carefully, to avoid that the frozen dataset
contains unnecessary data.

::

    frepplectl dumpdata --database=scenario1 


.. _test:

Run the test suite
------------------

Run the test suite for the user interface.

::

    frepplectl test freppledb


.. _runwebserver:

Run the Python web server
-------------------------

Runs a production web server for environments with very few users.
For a more scalable solution, deploying frePPLe on Apache with mod_wsgi is required.

::

    frepplectl runwebserver


.. _runserver:

Run the development web server
------------------------------

Run a development web server, which automatically reloads when code is changed.

For production use this web server doesn't scale enough.

::

    frepplectl runserver


.. _createmodel:

Generate a sample model
-----------------------

Populate the database with a configurable dataset. Command line arguments control
the depth and complexity of the bill of material, the number of resources and their
average load, the average lead times, the number of demands.

The command thus allows to quickly generate a sample model, and to verify its
scalability with varying size and complexity.

This command is intended for academic and research purposes. The script can 
easily be updated to create sample models in the structure you wish.

::

    frepplectl createmodel --level=3 --cluster=100 --demand=10 


.. _forecast_simulation:

Estimate historical forecast accuracy
-------------------------------------

This command estimates the forecast accuracy over the past periods.

This is achieved by turning back the clock a number of buckets ago. We compute
the forecast with the demand history we would have had available at that time.
Comparing the actual sales and the forecasted sales in that period allows us
to measure the forecast accuracy. This calculation is then repeated for each
bucket to follow. 

This command is intended for academic and research purposes. The script can 
easily be updated to perform more advanced forecast accuracy studies.

::

    frepplectl forecast_simulation


.. _simulation:

Simulate the execution of the plan
----------------------------------

This command simulates the execution of the plan. The command allows
detailed studies of the stability and robustness of the plan in the
presence of various disturbances.

The command iterates over a number of time periods and performs the following
steps in each period:

1. Advance the current date
2.  Call a custom function "start_bucket"
3. | Open new sales orders from customers
   | Custom code can be added here to represent the typical ordering pattern
     of customers, and the occasional rush orders.
4. Generate a constrained frePPLe plan
5. Confirm new purchase orders from the frePPLe plan
6. Confirm new production orders from the frePPLe plan
7. Confirm new distribution orders from the frePPLe plan
8. | Receive material from purchase orders
   | Custom code can be added here to simulate late or early deliveries
     from your suppliers.
9. | Finish production from manufacturing orders
   | Custom code can be added here to simulate production delays, machine breakdowns,
     rework and other production disturbances. 
10. | Receive material from distribution orders
    | Custom code can be added here to simulate late or early deliveries between
      locations in the warehouse.
11. Ship open sales orders to customers
12. | Call a custom function "end_bucket"
    | This function will typically be used to collect performance statistics
      of the period just simulated.

This command is intended for academic and research purposes. The script needs to
be tailored carefully to model a realistic level of disturbances in your model
and collect the performance metrics that are relevant.

::

    frepplectl simulation
  