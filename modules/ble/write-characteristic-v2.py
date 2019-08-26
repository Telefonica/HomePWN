from utils.ble import BLE
from time import sleep
from modules._module import Module
from utils.custom_print import print_info, print_error, print_ok
from utils.check_root import is_root
from utils.shell_options import ShellOptions
from utildata.dataset_options import Option


class HomeModule(Module):

    def __init__(self):
        information = {"Name": "BLE write a characteristic",
                       "Description": "This module allows you to write content encoded in the feature specified by the UUID. The feature must be writable to proceed.",
                       "privileges": "root",
                       "OS": "Linux",
                       "Author": "@josueencinar"}

        # -----------name-----default_value--description--required?
        options = {"bmac": Option.create(name="bmac", required=True),
                   "uuid": Option.create(name="uuid",  required=True, description='Specific UUID for a characteristic'),
                   "type": Option.create(name="type", value="random", required=True, description='Device addr type'),
                   "data": Option.create(name="data", value="Pwned", required=True, description="Data to write"),
                   "encode": Option.create(name="encode",  required=True, description='Choose data encode'),
                   "wait": Option.create(name="wait", value=0, required=True, description='seconds to wait connected after writing')
                   }
        
        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)
        # Additional features
        self.register_new_function("upload")
        self.register_new_function("save")
        self.set_extra_help({"upload <file_name>": "Load the data from a file.",
                            "save <file_name> ": "Save the options to a file."})

    # Autocomplete set option with values    
    def update_complete_set(self):
        s_options = ShellOptions.get_instance()
        s_options.add_set_option_values("encode", ["ascii", "hex"])
        s_options.add_set_option_values("type", ["random", "public"])

    # To load the options
    def upload(self, data):
        file_path = "./utildata/ble/"+data[0]
        try:
            with open(file_path, 'r') as file_read:
                for line in file_read.readlines():
                    data = line.split(":")
                    data[1] = data[1].strip()
                    self.set_value(data)
        except:
            print_error("Error reading file")

    # To save the options
    def save(self, data):
        
        file_path = "./utildata/ble/"+data[0]
        data = [f"uuid:{self.args['uuid']}", f"type:{self.args['type']}", f"data:{self.args['data']}", 
                f"encode:{self.args['encode']}", f"wait:{self.args['wait']}"]
        try:
            with open(file_path, 'w') as file_save:
                for line in data:
                    file_save.write(line + "\n")
        except:
            print_error("Error writing file")

    # This function must be always implemented, it is called by the run option
    @is_root
    def run(self):
        bmac = self.args["bmac"]
        data = self._transform_data(self.args["encode"], self.args["data"])
        if not data:
            return

        attempt = 1
        success = False
        ble_device = BLE(bmac, self.args["type"])
        while attempt <= 5 and not success:
            print_info(f"Trying to connect {bmac}. (Attempt: {attempt})")
            try:
                ble_device.connect()
                success = True
            except KeyboardInterrupt:
                print_info("Interrupted... exit run")
                return 
            except:
                attempt += 1
        if not success:
            print_error("Failed to connect")
            return
        ble_device.write_data(data, self.args["uuid"])
        try:
            sleep(int(self.args["wait"]))
        except:
            sleep(2)
            
        ble_device.disconnect()

    def _transform_data(self, encode, data):
        if encode == "hex":
            try:
                data = bytes.fromhex(data.replace("0x",""))
            except:
                print_error("Bad Hexadecimal value check it")
                data = None 
        else:
            data = data.encode()
        return data
