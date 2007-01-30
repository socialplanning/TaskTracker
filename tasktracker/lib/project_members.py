import httplib2
import elementtree.ElementTree as ET

def get_users_for_project(project, server):

    h = httplib2.Http()
    resp, content = h.request(server + "projects/%s/members.xml" % project, "GET")
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
