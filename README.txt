TaskTracker is an application for managing and organizing tasks
for groups of people.

It was written at The Open Planning Project for integration with
OpenCore, on the community action site http://coactivate.org

Installation and Setup
======================

Install ``TaskTracker`` using easy_install::

    easy_install TaskTracker

You need to manually install MySQLdb, since there is no easy_install for it.  

Make a config file as follows::

     cp development.example development.ini
    
Tweak the config file as appropriate and then setup the applicaiton::

    paster setup-app development.ini#tasktracker
    
Then you are ready to go.
