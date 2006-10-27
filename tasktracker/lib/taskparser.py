
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

class TaskParser:
    @classmethod
    def parse(cls, stuff):
        """
        Determine the format of the input to parse and
        pass it on to the appropriate parser to be parsed
        """
        return PlainTextTaskParser()._parse(stuff)

    def _parse(self, stuff):
        """
        Parse the input
        """
        pass

class PlainTextTaskParser:
    def __init__(self, field_splitter=':', task_splitter='\n'):
        self.field_splitter = field_splitter
        self.task_splitter = task_splitter
        self.ordered_params = ('title', 'owner')

    def _parse(self, stuff):
        tasks = list()
        for line in stuff.split(self.task_splitter):
            tasks.append(dict(zip(self.ordered_params, [p.strip() for p in line.split(self.field_splitter)])))
        return tasks
