#!/usr/bin/python3

from __future__ import absolute_import, print_function, unicode_literals
import dbus
import dbus.service
import dbus.mainloop.glib
try: 
    from gi.repository import GObject
except ImportError:
    try:
        import gobject as GObject
    except:
        GObject = None


BUS_NAME = 'org.bluez'
AGENT_INTERFACE = 'org.bluez.Agent1'

bus = None
device_obj = None
dev_path = None

def ask(prompt):
    try:
        return raw_input(prompt)
    except:
        return input(prompt)

def set_trusted(path):
    props = dbus.Interface(bus.get_object(BUS_NAME, path),
                           "org.freedesktop.DBus.Properties")
    props.Set("org.bluez.Device1", "Trusted", True)

def dev_connect(path):
    dev = dbus.Interface(bus.get_object(BUS_NAME, path),
                         "org.bluez.Device1")
    dev.Connect()

class Rejected(dbus.DBusException):
    _dbus_error_name = "org.bluez.Error.Rejected"

class Agent(dbus.service.Object):
    exit_on_release = True

    def set_exit_on_release(self, exit_on_release):
        self.exit_on_release = exit_on_release

    @dbus.service.method(AGENT_INTERFACE, in_signature="", out_signature="")
    def Release(self):
        print("Release")
        if self.exit_on_release:
            mainloop.quit()

    @dbus.service.method(AGENT_INTERFACE, in_signature="os", out_signature="")
    def AuthorizeService(self, device, uuid):
        authorize = "yes"
        if (authorize == "yes"):
            mac = get_mac(device)
            print("\nDevice Authorized {}".format(mac))
            return
        raise Rejected("Connection rejected by user")

    @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="s")
    def RequestPinCode(self, device):
        #print("RequestPinCode (%s)" % (device))
        set_trusted(device)
        mac = get_mac(device)
        print("\nDevice pairing {}".format(mac))
        # return ask("Enter PIN Code: ")
        return "0000"

    @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="u")
    def RequestPasskey(self, device):
        print("RequestPasskey (%s)" % (device))
        set_trusted(device)
        passkey = ask("Enter passkey: ")
        return dbus.UInt32(passkey)

    @dbus.service.method(AGENT_INTERFACE, in_signature="ouq", out_signature="")
    def DisplayPasskey(self, device, passkey, entered):
        print("DisplayPasskey (%s, %06u entered %u)" %
              (device, passkey, entered))

    @dbus.service.method(AGENT_INTERFACE, in_signature="os", out_signature="")
    def DisplayPinCode(self, device, pincode):
        print("DisplayPinCode (%s, %s)" % (device, pincode))

    @dbus.service.method(AGENT_INTERFACE, in_signature="ou", out_signature="")
    def RequestConfirmation(self, device, passkey):
        print("RequestConfirmation (%s, %06d)" % (device, passkey))
        confirm = ask("Confirm passkey (yes/no): ")
        if (confirm == "yes"):
            set_trusted(device)
            return
        raise Rejected("Passkey doesn't match")

    @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="")
    def RequestAuthorization(self, device):
        print("RequestAuthorization (%s)" % (device))
        auth = ask("Authorize? (yes/no): ")
            # auth = "yes"
        if (auth == "yes"):
            return
        raise Rejected("Pairing rejected")

    @dbus.service.method(AGENT_INTERFACE, in_signature="", out_signature="")
    def Cancel(self):
        print("Cancel")


def get_mac(device):
    mac = device.split(" ")[-1]
    mac = mac.split("_")[1:]
    mac = ":".join(mac)
    return mac

def pair_reply():
    print("Device paired")
    set_trusted(dev_path)
    dev_connect(dev_path)
    mainloop.quit()


def pair_error(error):
    err_name = error.get_dbus_name()
    if err_name == "org.freedesktop.DBus.Error.NoReply" and device_obj:
        print("Timed out. Cancelling pairing")
        device_obj.CancelPairing()
    else:
        print("Creating device failed: %s" % (error))

    mainloop.quit()

def run_agent():
    if GObject:
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus = dbus.SystemBus()
        capability = "NoInputNoOutput"

        path = "/test/agent"
        agent = Agent(bus, path)

        mainloop = GObject.MainLoop()

        obj = bus.get_object(BUS_NAME, "/org/bluez")
        manager = dbus.Interface(obj, "org.bluez.AgentManager1")
        manager.RegisterAgent(path, capability)

        print("\n\n[+] Agent registered in background ")

        manager.RequestDefaultAgent(path)
        try:
            mainloop.run()
        except:
            print("\n[-] The agent has finished ")
    else:
        print("No agent running...")


if __name__ == '__main__':
    run_agent()