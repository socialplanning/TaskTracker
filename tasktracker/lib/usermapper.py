
# Copyright (C) 2007 The Open Planning Project

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

class UserMapper(object):
    def project_member_roles(self, name):
        return [u.get("roles") for u in self.project_members() if name == u.get("username")]

    def project_member_names(self, role = None):
        if role:
            return [u.get("username") for u in self.project_members() if role in u.get("roles")]
        return [u.get('username') for u in self.project_members()]

    def project_members(self):
        pass
