import paho.mqtt.client as mqtt
from modules._module import Module
from utils.custom_print import print_ok, print_info, print_error
from utildata.dataset_options import Option
from utils.custom_thread import new_process_function



class HomeModule(Module):

    def __init__(self):
        information = {"Name": "MQTT publish",
                       "Description": "Launch this module publish data through MQTT (Mosquitto)",
                       "Author": "@josueencinar"}

        # -----------name-----default_value--description--required?
        options = {"rhost": Option.create(name="rhost", required=True),
            "sensor": Option.create(name="sensor", value="smarthouse/maindoor", required=True, description="Sensor to change data"),
            "data": Option.create(name="data", value="{'motion':'1'}", required=True, description="Data to be sent")
            }

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This function must be always implemented, it is called by the run option
    def run(self):
        client = mqtt.Client(client_id = "MqttClient")
        client.on_connect = self.__on_connect
        try:
            client.connect(self.args["rhost"], 1883, 60)
            client.publish(self.args["sensor"], self.args["data"])
        except Exception as e:
            print_error(e)

    def __on_connect(self, client, userdata, flags, rc):
        print_ok("Connection successful!")
