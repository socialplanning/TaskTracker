Installation and Setup
======================

Install ``TaskTracker`` using easy_install::

    easy_install TaskTracker

You need to manually install MySQLdb, since there is no easy_install for it.  

Make a config file as follows::

     cp development.example config.ini
    
Tweak the config file as appropriate and then setup the applicaiton::

    paster setup-app config.ini
    
Then you are ready to go.
