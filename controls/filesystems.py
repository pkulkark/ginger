#
# Project Kimchi
#
# Copyright IBM, Corp. 2013-2014
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA

from kimchi.control.base import Collection, Resource
from kimchi.control.utils import UrlSubNode


@UrlSubNode('filesystems', True)
class FileSystems(Collection):
    def __init__(self, model):
        super(FileSystems, self).__init__(model)
        self.role_key = 'host'
        self.admin_methods = ['GET', 'POST', 'DELETE']
        self.resource = FileSystem


class FileSystem(Resource):
    def __init__(self, model, ident):
        super(FileSystem, self).__init__(model, ident)
        self.role_key = 'host'
        self.admin_methods = ['GET', 'POST', 'DELETE']
        self.uri_fmt = "/filesystems/%s"
        # self.umount = self.generate_action_handler('umount')
        self.format = self.generate_action_handler_task('format', ['disk'])

    @property
    def data(self):
        return {'filesystem': self.info['filesystem'],
                'type': self.info['type'],
                'size': self.info['size'],
                'used': self.info['used'],
                'avail': self.info['avail'],
                'use%': self.info['use%'],
                'mounted_on': self.info['mounted_on']}


