from subprocess import Popen, PIPE
from os import system, kill, environ
from modules._module import Module
from utils.custom_print import print_ok, print_info, print_error
from utils.custom_thread import new_process_command, new_process_function
from utils.check_root import is_root
from utils.dirtytooth.dirtyagent import run_agent
from utils.tasks import Task
from utildata.dataset_options import Option


class HomeModule(Module):

    def __init__(self):
        information = {"Name": "Launch Bluetooth Service",
                       "Description": "Use this module if you want to create a Bluetooth service that users can connect to. It is necessary to specify the bluetooth interface to use and the profile you want to generate.",
                       "Author": "@josueencinar",
                       "privileges": "root",}

        # -----------name-----default_value--description--required?
        options = {"name": Option.create(name="name", description="Device name"),
                   "iface": Option.create(name="iface", value="hci0", required=True),
                   "class": Option.create(name="class", value="0x240418", required=True, description='Bluetooth class (Profile)')
                   }


        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This function must be always implemented, it is called by the run option
    @is_root
    def run(self):
        hci = self.args["iface"]
        name = "DirtytoothSpeaker"
        if self.args['name']:
            name = self.args['name']
        if Task.get_instance().exist_task("dirtyagent"):
            print_info("A dirtyagent is running... Kill it first")
            return
        tool = "hciconfig"
        options =  [f"{hci} name {name}", f"{hci} reset", f"{hci} class {self.args['class']}",f"{hci} noauth", f"{hci} piscan"]

        for op in options:
            system(tool + " " +  op)
        new_process_function(run_agent, name="dirtyagent")
        #new_process_command("./utils/dirtytooth/dirtyagent", name="dirtyagent")
        