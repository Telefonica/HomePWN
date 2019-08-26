import paho.mqtt.client as mqtt
from modules._module import Module
from utils.custom_print import print_ok, print_info, print_error
from utildata.dataset_options import Option
from utils.custom_thread import new_process_function



class HomeModule(Module):

    def __init__(self):
        self.connected = False
        self.file_to_save = None
        information = {"Name": "MQTT Subscribe",
                       "Description": "Launch this module to try get information through MQTT (Mosquitto)",
                       "Author": "@josueencinar"}

        # -----------name-----default_value--description--required?
        options = {"rhost": Option.create(name="rhost", required=True),
            "file": Option.create(name="file", value="./files/mqtt.txt", required=True),
            "verbose": Option.create(name="verbose", value="True", description="Show if connection is established")}

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This function must be always implemented, it is called by the run option
    def run(self):
        try:
            self.file_to_save = open(self.args["file"], "w+")
        except Exception as e:
            print_error(e)
            print_error("Module has not been launched")
            return
        print_info(f'Trying to get information from {self.args["rhost"]}. The data is saved in {self.args["file"]}d')
        new_process_function(self.__start, name="mqtt_subscribe", seconds_to_wait=1)

    def __start(self):
        client = mqtt.Client(client_id = "MqttClient")
        client.on_connect = self.__on_connect
        client.on_message = self.__on_message
        try:
            client.connect(self.args["rhost"])
            client.loop_forever()
        except:
            if self.file_to_save:
                self.file_to_save.close()

    def __on_connect(self, client, userdata, flags, rc):
        if str(self.args["verbose"]).lower() == "true" and not self.connected:
            print_ok("Connection successful!", start="\n", end="\n")
        client.subscribe("#", qos=1)
        client.subscribe("$SYS/#")
        self.connected = True

    def __on_message(self, client, userdata, msg):
        self.file_to_save.write(f"Topic: {msg.topic} - Message: {msg.payload}\n")