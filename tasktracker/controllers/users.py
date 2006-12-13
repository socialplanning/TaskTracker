
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

from tasktracker.lib.base import *
from tasktracker.models import *

import formencode
from formencode.validators import *

class EncodedPassword(FancyValidator):
    def _to_python(self, value, state):
        return value.encode("base64")

class UniqueName(FancyValidator):
    messages = {'not_unique' : 'A user of this name already exists!',
                'empty' : 'Please input a value'}

    def __init__(self, kind, *args, **kwargs):
        self.kind = kind
        FancyValidator.__init__(self, strip=True, not_empty=True, *args, **kwargs)
        
    def _to_python(self, value, state):
        return str(value)

    def validate_python(self, value, state):
        if list(self.kind.selectBy(username=value)):
            raise formencode.Invalid(self.message("not_unique", state), value, state)

class UserSchema(formencode.Schema):
    allow_extra_fields = True
    filter_extra_fields = True
    username = UniqueName(User)
    password = EncodedPassword()
    password_again = EncodedPassword()
    chained_validators = [FieldsMatch('password', 'password_again')]

class UsersController(BaseController):
    @attrs(action="open")
    def add(self):
        return render_response('zpt', "useradd")

    @attrs(action="open")
    @validate(schema=UserSchema, form="add")
    def create(self, *args, **kwargs):
        del self.form_result['password_again']
        user = User(**self.form_result)
        return redirect_to(controller="tasklist")
