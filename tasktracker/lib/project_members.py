import httplib2
import elementtree.ElementTree as ET

def get_users_for_project(project, server):
    h = httplib2.Http()
    resp, content = h.request("%s/projects/%s/members.xml" % (server, project), "GET")
    if resp['status'] != '200':
        raise ValueError("Error retrieving project %s: status %s" % (project, resp['status']))
    tree = ET.fromstring(content)
    members = []
    for member in tree:
        m = {}
        m['username'] = member.find('id').text
        m['roles'] = []
        for role in member.findall('role'):
            m['roles'].append(role.text)
        members.append(m)
    return members

def get_info_for_project(project, server):
    h = httplib2.Http()
    resp, content = h.request("%s/projects/%s/info.xml" % (server, project), "GET")
    if resp['status'] != '200':
        raise ValueError("Error retrieving project %s: status %s" % (project, resp['status']))
    tree = ET.fromstring(content)
    policy = tree[0]
    assert policy.tag == "policy"
    info = dict(policy=policy.text)
    return info
