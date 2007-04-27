#!/usr/bin/python

# Copyright (C) 2006-2007 The Open Planning Project

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

#IMPORTANT NOTE: you need to add the following line to your autobench config file:
#httperf_add-header="Authorization: Basic YWRtaW46YWRtaW4"

from os import system
import random 
import httplib2
import urllib
import re

# From http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/146306
def encode_multipart_formdata(fields=[], files=[]):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
    CRLF = '\r\n'
    L = []
    # if it's dict like then use the items method to get the fields
    if hasattr(fields, "items"):
        fields = fields.items()
    for (key, value) in fields:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    for (key, filename, value) in files:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        L.append('Content-Type: %s' % get_content_type(filename))
        L.append('')
        L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(map(str,L))
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body


http = httplib2.Http()
cookie = ''
authenticator = ''
def benchmark(path, id):
    print "benchmarking %s" % path
    filename = "bench.%s.%s" % (id, path.replace("/","_"))
    system("autobench --single_host --host1 localhost --uri1 %s --port1 5000 --low_rate 3 --high_rate 10 --rate_step 2 --num_call 1 --num_conn 10 --timeout 30 --output_fmt csv --file %s.csv" % (path, filename))
    print "done benchmark"

def init_site():
    global cookie, authenticator
    system("paster setup-app development.ini")

    http.add_credentials('admin', 'admin')
    headers, body = http.request('http://localhost:5000/project/initialize', method='POST')

    headers, body = http.request('http://localhost:5000/tasklist/show_create')
    cookie = headers['set-cookie']
    result = re.search('<input id="authenticator" name="authenticator" type="hidden" value="(\w+)" />', body)
    authenticator = result.group(1)

def random_letter():
    return chr(ord("a") + random.randint(0, 25))

def post_request(url, vars):
    global cookie, authenticator, http
    fields = dict(authenticator=authenticator)
    fields.update(vars)
    content_type, content = encode_multipart_formdata(fields=fields)
    headers={
            "Content-type": content_type,
            "Cookie": cookie
        }

    return http.request(url, method="POST", body=content, headers=headers)


def create_tasklist():
    task_list_name = "".join(random_letter() for i in range (20))
    vars = dict(
            text = 'tl body',
            title = "TL_" + task_list_name,
            member_level = 0,
            other_level = 0, 
            initial_assign = 0,
            managers='',
            )
    headers, body = post_request('http://localhost:5000/tasklist/create', vars)
    result = re.search('<a href="/tasklist/index/(\d+)">', body)
    id = result.group(1)
    return id

def create_task(task_list_id):
    global cookie, authenticator, http
    task_name = "".join(random_letter() for i in range (20))
    vars = dict(
            text = 'task body',
            title = "TASK_" + task_name,
            task_listID = task_list_id,
            parendID = 0,
            siblingID = 0,
            )
    headers, body = post_request('http://localhost:5000/task/create', vars)

init_site()
print "with nothing, project page"
benchmark("/", "nothing")

create_tasklist()
tasklists = [create_tasklist() for i in range(10)]
print "ten empty tasklists, project page"
benchmark("/","empty_tasklists")


print "ten empty tasklists, a tasklist page"
benchmark("/tasklist/show/1","empty_tasklists")

for tasklist in tasklists:
    for i in range(10):
        create_task(tasklist)
print "ten tasklists of ten tasks, project page"
benchmark("/","ten_tasks")

print "ten tasklists of ten tasks, a tasklist page"
benchmark("/tasklist/show/1","ten_tasks")

print "ten tasklists of ten tasks, a task page"
benchmark("/task/show/1","ten_tasks")

for tasklist in tasklists:
    for i in range(90):
        create_task(tasklist)
print "ten tasklists of one hundred tasks, a tasklist page"
benchmark("/tasklist/show/1","hundred_tasks")

print "ten tasklists of one hundred tasks, a task page"
benchmark("/task/show/1","hundred_tasks")

print "creating a hundred tasklists"
tasklists += [create_tasklist() for i in range(90)]

print "creating ten kilotasks"
for tasklist in tasklists[10:]:
    print "Creating tasks"
    for i in range(100):
        create_task(tasklist)

print "one hundred tasklists of one hundred tasks, a tasklist page"
benchmark("/tasklist/show/1","tenk_tasks")

print "one hundred tasklists of one hundred tasks, a task page"
benchmark("/task/show/1","tenk_tasks")
