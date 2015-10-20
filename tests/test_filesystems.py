#
# Project Ginger
#
# Copyright IBM, Corp. 2015
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

import crypt
import spwd
import unittest

import models.filesystem as filesystem

from wok.exception import OperationFailed
from wok.rollbackcontext import RollbackContext


class FileSystemTests(unittest.TestCase):

    def test_get_fs_list(self):
        fs = filesystem.FileSystemsModel()
        fs_list = fs.get_list()
        self.assertGreaterEqual(len(fs_list), 0)

    def test_mount_fs(self):
        fs = filesystem.FileSystemsModel()
        fsd = filesystem.FileSystemModel()
        blkdev = '/testfile'
        mntpt = '/test'
        persistent = False

        fs_list = fs.get_list()
        with RollbackContext() as rollback:
            fs.create({'blk_dev':blkdev, 'mount_point':mntpt, 'persistent':persistent})
            rollback.prependDefer(fsd.delete, mntpt)

            new_fs_list = fs.get_list()
            self.assertEqual(len(new_fs_list), len(fs_list) + 1)


    def test_mount_existing_fs_fails(self):
        fs = filesystem.FileSystemsModel()
        fsd = filesystem.FileSystemModel()
        blkdev = '/testfile'
        mntpt = '/test'
        persistent = False

        with RollbackContext() as rollback:
            fs.create({'blk_dev':blkdev, 'mount_point':mntpt, 'persistent':persistent})
            rollback.prependDefer(fsd.delete, mntpt)

            with self.assertRaises(OperationFailed):
                fs.create({'blk_dev':blkdev, 'mount_point':mntpt, 'persistent':persistent})


