
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
    version="",
    #description="",
    #author="",
    #author_email="",
    #url="",
    install_requires=[
      "Myghty",
      "Pylons==0.9.4.1",
      "Routes==1.6.2.1",
      "SQLObject===0.9", 
      "decorator", 
      "httplib2", 
      "elementtree", 
      "python-dateutil",
      "uuid",
      "topp.utils>0.1"],
    packages=find_packages(),
    include_package_data=True,
    test_suite = 'nose.collector',
    package_data={'tasktracker': ['i18n/*/LC_MESSAGES/*.mo']},
    dependency_links = [
      "http://pythonpaste.org/package_index.html",
      "http://cheeseshop.python.org/pypi/Pylons/0.9.4",
      "http://routes.groovie.org/svn/tags/1.6.2.1#egg=Routes-1.6.2.1",
      "http://zesty.ca/python/uuid.py#egg=uuid-dev",
      "http://labix.org/python-dateutil",
      "http://www.openplans.org/projects/opencore/dependencies"
      ],
    entry_points="""
    [paste.app_factory]
    main=tasktracker:make_app
    [paste.app_install]
    main=paste.script.appinstall:Installer
    """,
)
