#
# Project Kimchi
#
# Copyright IBM, Corp. 2013-2015
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

import os.path
import re
import subprocess


from wok.exception import OperationFailed


def _parse_df_output(output):
    """
    This method parses the output of 'df -hT' command.
    :param output: Parsed output of the 'df -hT' command
    :return:list containing filesystems information
    """

    try:
        output = output.splitlines()
    except:
        raise OperationFailed("KCHDISKS00032", "Invalid df output provided")

    out_list = []

    try:
        for fs in output[1:]:
            fs_dict = {}
            fs_list = fs.split()
            fs_dict['filesystem'] = fs_list[0]
            fs_dict['type'] = fs_list[1]
            fs_dict['size'] = fs_list[2]
            fs_dict['used'] = fs_list[3]
            fs_dict['avail'] = fs_list[4]
            fs_dict['use%'] = fs_list[5]
            fs_dict['mounted_on'] = fs_list[6]

            out_list.append(fs_dict)
    except:
        raise OperationFailed("KCHDISKS00033", "Parsing the output failed.")

    return out_list


def _get_fs_names():
    """
    Fetches list of filesystems
    :return: list of filesystem names
    """
    fs_name_list = []
    try:
        outlist = _get_df_output()
        fs_name_list = [d['mounted_on'] for d in outlist]
        return fs_name_list
    except:
        raise OperationFailed("KCHDISKS00031", "error in fetching the list of filesystems")


def _get_fs_info(mnt_pt):
    """
    Fetches information about the given filesystem
    :param mnt_pt: mount point of the filesystem
    :return: dictionary containing filesystem info
    """
    fs_info = {}
    try:
        fs_search_list = _get_df_output()
        for i in fs_search_list:
            if mnt_pt == i['mounted_on']:
                fs_info['filesystem'] = i['filesystem']
                fs_info['type'] = i['type']
                fs_info['size'] = i['size']
                fs_info['used'] = i['used']
                fs_info['avail'] = i['avail']
                fs_info['use%'] = i['use%']
                fs_info['mounted_on'] = i['mounted_on']
    except:
        raise OperationFailed("KCHDISKS00030", {'device': mnt_pt})
    return fs_info

def _get_swapdev_list_parser(output):
    """
    This method parses the output of 'cat /proc/swaps' command
    :param output: output of 'cat /proc/swaps' command
    :return:list of swap devices
    """
    output = output.splitlines()
    output_list = []

    for swapdev in output[1:]:
        dev_name = swapdev.split()[0]
        output_list.append(dev_name)

    return output_list

def _create_file(size, file_loc):
   """
   This method creates a flat file
   :param size: size of the flat file to be created
   :param file_loc: location of the flat file
   :return:
   """
   crt_out = subprocess.Popen(["dd", "if=/dev/zero", "of=" + file_loc, "bs=" + size, "count=1"], stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
   out, err = crt_out.communicate()
   if crt_out.returncode != 0:
       raise OperationFailed("KCHDISKS0001E", {'err': err})
   return

def _make_swap(file_loc):
    """
    This method configures the given file/device as a swap file/device
    :param file_loc: path of the file/device
    :return:
    """
    os.chown(file_loc,0,0)
    os.chmod(file_loc, 0600)
    mkswp_out = subprocess.Popen(["mkswap", file_loc], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = mkswp_out.communicate()
    if mkswp_out.returncode != 0:
        raise OperationFailed("KCHDISKS0001E", {'err': err})
    return

def _activate_swap(file_loc):
    """
    This method activates the swap file/device
    :param file_loc: path of the file/device
    :return:
    """
    swp_out = subprocess.Popen(["swapon", file_loc], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = swp_out.communicate()
    if swp_out.returncode != 0:
        raise OperationFailed("KCHDISKS0001E", {'err': err})
    return

def _makefs(fstype, name):
    """
    This method formats the device with the specified file system type
    :param fstype: type of the filesystem
    :param name: path of the device/partition to be formatted
    :return:
    """
    fs_out = subprocess.Popen(["mkfs", "-t", fstype ,"-F", name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = fs_out.communicate()
    if fs_out.returncode != 0:
        raise OperationFailed("KCHDISKS0001E", {'err': err})
    return

def _parse_swapon_output(output):
    """
    This method parses the output of 'grep -w devname /proc/swaps'
    :param output: output of 'grep -w devname /proc/swaps' command
    :return: dictionary containing swap device info
    """
    output_dict = {}
    output_list = output.split()
    output_dict['filename'] = output_list[0]
    output_dict['type'] = output_list[1]
    output_dict['size'] = output_list[2]
    output_dict['used'] = output_list[3]
    output_dict['priority'] = output_list[4]

    return output_dict

def _get_swap_output(device_name):
    """
    This method executes the command 'grep -w devname /proc/swaps'
    :param device_name: name of the swap device
    :return:
    """
    swap_out = subprocess.Popen(
        ["grep", "-w", device_name, "/proc/swaps"] ,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = swap_out.communicate()
    if swap_out.returncode != 0:
        raise OperationFailed("KCHDISKS0001E", {'err': err})

    return _parse_swapon_output(out)

def _swapoff_device(device_name):
    """
    This method removes swap devices
    :param device_name: path of the swap device to be removed
    :return:
    """
    swapoff_out = subprocess.Popen(
        ["swapoff", device_name] ,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = swapoff_out.communicate()
    if swapoff_out.returncode != 0:
        raise OperationFailed("KCHDISKS0001E", {'err': err})
    else:
        os.remove(device_name) if os.path.exists(device_name) else None

def _is_mntd(partition_name):
    """
    This method checks if the partition is mounted
    :param partition_name: name of the partition
    :return:
    """
    is_mntd_out = subprocess.Popen(
        ["grep", "-w", "^/dev/"+partition_name+"\s", "/proc/mounts"] ,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = is_mntd_out.communicate()
    if is_mntd_out.returncode != 0:
        return False
    else:
        return True


def _get_df_output():
    """
    Executes 'df -hT' command and returns
    :return: output of 'df -hT' command
    """
    dfh_out = subprocess.Popen(["df", "-hT"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    fs_out, fs_err = dfh_out.communicate()

    if dfh_out.returncode != 0:
        raise OperationFailed("KCHDISKS0002F", {'err': fs_err})
    return _parse_df_output(fs_out)


def _mount_a_blk_device(blk_dev, mount_point):
    """
    Mounts the given block device on the given mount point
    :param blk_dev: path of the block device
    :param mount_point: mount point
    :return:
    """
    mount_out = subprocess.Popen(["/bin/mount", blk_dev, mount_point], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    std_out, std_err = mount_out.communicate()
    if mount_out.returncode != 0:
        raise OperationFailed("KCHDISKS00034", {'err': std_err})


def _umount_partition(mnt_pt):
    """
    Unmounts the given mount point (filesystem)
    :param mnt_pt: mount point
    :return:
    """
    umount_out = subprocess.Popen(["/bin/umount", mnt_pt], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    std_out, std_err = umount_out.communicate()
    if umount_out.returncode != 0:
        raise OperationFailed("KCHDISKS00035", {'err': std_err})
    return


def make_persist(dev, mntpt):
    """
    This method persists the mounted filesystem by making an entry in fstab
    :param dev: path of the device to be mounted
    :param mntpt: mount point
    :return:
    """
    fo = open("/etc/fstab", "a+")
    fo.write(dev + " " + mntpt + " " + "defaults 1 2")
    fo.close()

def remove_persist(mntpt):
    """
    This method removes the fstab entry
    :param mntpt: mount point
    :return:
    """
    fo = open("/etc/fstab", "r")
    lines = fo.readlines()
    output = []
    fo.close()
    fo = open("/etc/fstab", "w")
    for line in lines:
        if mntpt in line:
            continue
        else:
            output.append(line)
    fo.writelines(output)
    fo.close()
