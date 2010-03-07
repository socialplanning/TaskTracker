TaskTracker is an application for managing and organizing tasks
for groups of people.

It was written at The Open Planning Project for integration with
OpenCore, on the community action site http://coactivate.org

Installation and Setup
======================

Currently TaskTracker only runs on Python2.4

Install ``TaskTracker`` in a contained environment using easy_install::

    virtualenv --python=python2.4 /tmp/tt/ve
    source /tmp/tt/ve/bin/activate
    cd /tmp/tt
    easy_install -e -b . TaskTracker
    cd tasktracker
    python setup.py develop

Make a config file::

    cp development.example development.ini
    
Tweak the config file as appropriate. Things you may want to change:

 * sqlobject.dburi, database -- these are set to use a mysql db;
   you may want to change them to sqlite to try it out.

 * openplans_wrapper -- set this to tasktracker.lib.testing_env:TestingEnv
   unless you are integrating with an OpenCore instance.

   The TestingEnv will allow you to log in with any username/password
   combination using HTTP Basic Auth.  Log in as user `admin` to have
   all privileges (for creating new task lists, etc)

Then setup the application::

    paster setup-app development.ini#tasktracker
    
Then you are ready to go::

    paster serve development.ini

