# Adapting script from https://nfcpy.readthedocs.io/en/latest/
# Thanks to nehpetsde
# Author: @lucferbux
from modules._module import Module
from utils.custom_print import print_info, print_ok_raw, print_error, print_body
from utils.check_root import is_root
from utildata.dataset_options import Option
import nfc
import nfc.clf.device
import nfc.clf.transport

import os
import errno
import logging
import argparse
import subprocess
import platform


class HomeModule(Module):

    def __init__(self):
        information = {"Name": "Setup NFC Reader",
                       "Description": "Launch this module to review information on how to configure the NFC reader.",
                       "privileges": "root",
                       "OS": "Linux",
                       "Reference" : "https://nfcpy.readthedocs.io/en/latest/",
                       "Author": "@lucferbux"}

        options = {
            'tty': Option.create(name="tty", value=False, description="search for serial devices on linux"),
        }

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This function must be always implemented, it is called by the run option
    @is_root
    def run(self):
        reader = self.args.get("reader", "usb")
        tty = str(self.args.get("tty", "False")).lower() == "true"
        self.setup(tty)        
        
    def setup(self, tty):
        print_info("Searching your system for contactless devices")
    
        found = 0
        for vid, pid, bus, dev in nfc.clf.transport.USB.find("usb"):
            if (vid, pid) in nfc.clf.device.usb_device_map:
                path = "usb:{0:03d}:{1:03d}".format(bus, dev)
                try:
                    clf = nfc.ContactlessFrontend(path)
                    print_ok_raw(f"** found {clf.device}")
                    clf.close()
                    found += 1
                except IOError as error:
                    if error.errno == errno.EACCES:
                        self.usb_device_access_denied(bus, dev, vid, pid, path)
                    elif error.errno == errno.EBUSY:
                        self.usb_device_found_is_busy(bus, dev, vid, pid, path)
    
        if tty:
            for dev in nfc.clf.transport.TTY.find("tty")[0]:
                path = f"tty:{dev[8:]}"
                try:
                    clf = nfc.ContactlessFrontend(path)
                    print_ok_raw(f"** found {clf.device}")
                    clf.close()
                    found += 1
                except IOError as error:
                    if error.errno == errno.EACCES:
                        print_error("access denied for device with path %s" % path)
                    elif error.errno == errno.EBUSY:
                        print_error("the device with path %s is busy" % path)
        else:
            print_info("I'm not trying serial devices because you haven't told me")
            print("-- turn the option 'tty' to True to have me looking")
            print("-- but beware that this may break other serial devs")
    
        if not found:
            print_error("Sorry, but I couldn't find any contactless device")
    
    
    def usb_device_access_denied(self, bus, dev, vid, pid, path):
        print_ok_raw(f"** found usb:{vid:04x}:{pid:04x} at {path} but access is denied")
        if platform.system().lower() == "linux":
            devnode = f"/dev/bus/usb/{bus:03d}/{dev:03d}"
            if not os.access(devnode, os.R_OK | os.W_OK):
                import pwd
                import grp
                usrname = pwd.getpwuid(os.getuid()).pw_name
                devinfo = os.stat(devnode)
                dev_usr = pwd.getpwuid(devinfo.st_uid).pw_name
                dev_grp = grp.getgrgid(devinfo.st_gid).gr_name
                try:
                    plugdev = grp.getgrnam("plugdev")
                except KeyError:
                    plugdev = None
    
                udev_rule = 'SUBSYSTEM==\\"usb\\", ACTION==\\"add\\", ' \
                            'ATTRS{{idVendor}}==\\"{vid:04x}\\", ' \
                            'ATTRS{{idProduct}}==\\"{pid:04x}\\", ' \
                            '{action}'
                udev_file = f"/etc/udev/rules.d/nfcdev.rules"
    
                print(f"-- the device is owned by '{dev_usr}' but you are '{usrname}'")
                print(f"-- also members of the '{dev_grp}' group would be permitted")
                print("-- you could use 'sudo' but this is not recommended")
    
                if plugdev is None:
                    print("-- it's better to adjust the device permissions")
                    action = 'MODE=\\"0666\\"'
                    udev_rule = udev_rule.format(vid=vid, pid=pid, action=action)
                    print_ok_raw("   sudo sh -c 'echo {udev_rule} >> {udev_file}'"
                            .format(udev_rule=udev_rule, udev_file=udev_file))
                    print("   sudo udevadm control -R # then re-attach device")
                elif dev_grp != "plugdev":
                    print("-- better assign the device to the 'plugdev' group")
                    action = 'GROUP=\\"plugdev\\"'
                    udev_rule = udev_rule.format(vid=vid, pid=pid, action=action)
                    print_ok_raw("   sudo sh -c 'echo {udev_rule} >> {udev_file}'"
                            .format(udev_rule=udev_rule, udev_file=udev_file))
                    print_ok_raw("   sudo udevadm control -R # then re-attach device")
                    if usrname not in plugdev.gr_mem:
                        print("-- and make yourself member of the 'plugdev' group")
                        print_ok_raw("   sudo adduser {0} plugdev".format(usrname))
                        print_ok_raw("   su - {0} # or logout once".format(usrname))
                elif usrname not in plugdev.gr_mem:
                    print("-- you should add yourself to the 'plugdev' group")
                    print_ok_raw("   sudo adduser {0} plugdev".format(usrname))
                    print_ok_raw("   su - {0} # or logout once".format(usrname))
                else:
                    print("-- but unfortunately I have no better idea than that")
    
    
    def usb_device_found_is_busy(self, bus, dev, vid, pid, path):
        print_ok_raw(f"** found usb:{vid:04x}:{pid:04x} at {path} but it's already used")
        if platform.system().lower() == "linux":
            sysfs = '/sys/bus/usb/devices/'
            for entry in os.listdir(sysfs):
                if not entry.startswith("usb") and ':' not in entry:
                    sysfs_device_entry = sysfs + entry + '/'
                    busnum = open(sysfs_device_entry + 'busnum').read().strip()
                    devnum = open(sysfs_device_entry + 'devnum').read().strip()
                    if int(busnum) == bus and int(devnum) == dev:
                        break
            else:
                print("-- impossible but nothing found in /sys/bus/usb/devices")
                return
    
            # We now have the sysfs entry for the device in question. All
            # supported contactless devices have a single configuration
            # that will be listed if the device is used by another driver.
    
            blf = "/etc/modprobe.d/blacklist-nfc.conf"
            sysfs_config_entry = sysfs_device_entry[:-1] + ":1.0/"
            print("-- scan sysfs entry at '%s'" % sysfs_config_entry)
            driver = os.readlink(sysfs_config_entry + "driver").split('/')[-1]
            print("-- the device is used by the '%s' kernel driver" % driver)
            if os.access(sysfs_config_entry + "nfc", os.F_OK):
                print("-- this kernel driver belongs to the linux nfc subsystem")
                print("-- you can remove it to free the device for this session")
                print_ok_raw("   sudo modprobe -r %s" % driver)
                print("-- and blacklist the driver to prevent loading next time")
                print_ok_raw("   sudo sh -c 'echo blacklist %s >> %s'" % (driver, blf))
            elif driver == "usbfs":
                print("-- this indicates a user mode driver with libusb")
                devnode = "/dev/bus/usb/{0:03d}/{1:03d}".format(bus, dev)
                print_ok_raw("-- find the process that uses " + devnode)
                try:
                    subprocess.check_output("which lsof".split())
                except subprocess.CalledProcessError:
                    print("-- there is no 'lsof' command, can't help further")
                else:
                    lsof = "lsof -t " + devnode
                    try:
                        test = subprocess.check_output(lsof.split()).decode("utf-8") 
                        pids = test.strip().split("\n")
                    except subprocess.CalledProcessError:
                        pid = None
                    for pid in pids:
                        ps = f"ps --no-headers -o cmd -p {pid}"
                        cmd = subprocess.check_output(ps.split()).strip()
                        cwd = os.readlink(f"/proc/{pid}/cwd")
                        print_ok_raw(f"-- found that process {pid} uses the device")
                        print(f"-- process {pid} is '{cmd}'")
                        print(f"-- in directory '{cwd}'")
                    # else:
                    #     print(f"   ps --no-headers -o cmd -p `sudo {lsof}`")
    
