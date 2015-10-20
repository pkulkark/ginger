#
# Project Kimchi
#
# Copyright IBM, Corp. 2014
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

from wok.exception import OperationFailed, NotFoundError
import libvirt
from controls import fs_utils


class FileSystemsModel(object):
    def __init__(self, **kargs):
        pass

    def create(self, params):
        try:
            blk_dev = params['blk_dev']
            mount_point = params['mount_point']
            fs_utils._mount_a_blk_device(blk_dev, mount_point)
        except libvirt.libvirtError as e:
            raise OperationFailed("KCHFS00000",
                                  {'mount point': mount_point, 'err': e.get_error_message()})
        return mount_point

    def get_list(self):
        try:
            fs_names = fs_utils._get_fs_names()

        # for idx, val in enumerate(fs_names):
        #     fs_names[idx] = fs_names[idx][1:]
        except libvirt.libvirtError as e:
            raise OperationFailed("KCHFS00001",
                                  {'err': e.get_error_message()})

        return fs_names



class FileSystemModel(object):
    def __init__(self, **kargs):
        pass


    def lookup(self, name):
        try:
            return fs_utils._get_fs_info(name)

        except ValueError:
            raise NotFoundError("KCHFS00002", {'name': name})

    def delete(self, name):
        print "inside delete method"
        try:
            fs_utils._umount_partition(name)
        except libvirt.libvirtError as e:
            raise OperationFailed("KCHFS00003",
                                  {'err': e.get_error_message()})



