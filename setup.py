
# Copyright (C) 2006 The Open Planning Project

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the 
# Free Software Foundation, Inc., 
# 51 Franklin Street, Fifth Floor, 
# Boston, MA  02110-1301
# USA

# Make sure we can import from *this* tasktracker package
import sys, os
#sys.path.insert(0, os.path.dirname(__file__))  # @@ what is this supposed to do? -egj
from setuptools import setup, find_packages

setup(
    name='TaskTracker',
    version="0.1",
    #description="",
    author="The Open Planning Project",
    author_email="ejucovy@openplans.org",
    url="http://www.openplans.org/projects/tasktracker",
    install_requires=[
      "Myghty",
      "Pylons==0.9.6.1",
      "Routes>=1.7",
      "SQLObject",
      "decorator>=2.1.0", 
      "httplib2", 
      "elementtree", 
      "python-dateutil",
      "uuid",
      "topp.utils>=0.5",
      "FormEncode==dev,>=0.7.2dev-r2661",
      "CabochonClient",
      "CabochonServer",
      "restclient",
      "signedheaders",
      "SupervisorErrorMiddleware",
      "wsseauth>=0.1.1",
      "WebHelpers>=0.3.2,<0.6dev",
      ],
    packages=find_packages(),
    include_package_data=True,
    test_suite = 'nose.collector',
    package_data={'tasktracker': ['i18n/*/LC_MESSAGES/*.mo']},
    dependency_links = [
      "https://svn.openplans.org/eggs/",
      "http://pythonpaste.org/package_index.html",
      "http://labix.org/python-dateutil",
      "http://svn.colorstudy.com/SQLObject/trunk#egg=SQLObject-dev",
      "https://svn.openplans.org/svn/signedheaders#egg=signedheaders",
      "https://svn.openplans.org/svn/SupervisorErrorMiddleware/trunk#egg=SupervisorErrorMiddleware-dev",
      ],
    entry_points="""
    [paste.app_factory]
    main=tasktracker:make_app
    [paste.app_install]
    main=paste.script.appinstall:Installer
    """,
)
