from modules._module import Module
from utils.custom_print import print_info, print_error, print_msg
from utildata.dataset_options import Option
from utils.shell_options import ShellOptions
import qrcode


class HomeModule(Module):

    def __init__(self):
        information = {"Name": "Generate QR Wifi",
                       "Description": "Generate QR Image with wifi access point",
                       "OS": "Linux",
                       "Author": "@lucferbux"}

        # -----------name-----default_value--description--required?
        options = {
            'ssid': Option.create(name="ssid", required=True, description="Network name (Ex. MY_SSID)"),
            'authentication-type': Option.create(name="authentication-type", required=True, description="Network authentication type (Ex. WPA2)"),
            'network-key': Option.create(name="network-key", required=True, description="Network name (Ex. mypassword)"),
            'version': Option.create(name="version", value=1, required=False, description="version of qr generated"),
            'box_size': Option.create(name="data", value=10, required=False, description="size of the box of the qr"),
            'border': Option.create(name="data", value=1, required=False, description="width of the border"),
            'fill_color': Option.create(name="fill_color", value="black", required=False, description="collor of the pattern"),
            'back_color': Option.create(name="back_color", value="white", required=False, description="background color"),
            'append': Option.create(name="append", value=False, description="overwrite the records of a tag"),
            'file': Option.create(name="file", value="qr.png", description="destination file"),
            'save': Option.create(name="save", value=False, description="Wether if we save the file in the path written in file or not")
        
        }

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # Autocomplete set option with values    
    def update_complete_set(self):
        s_options = ShellOptions.get_instance()
        s_options.add_set_option_values("authentication-type", ["WPA", "WEP", "nopass"])

    def run(self):
        ssid = self.args.get('ssid', "")
        authentication_type = self.args.get('authentication-type', "")
        network_key = self.args.get('network-key', "")
        version = int(self.args.get("version", 1))
        box_size = int(self.args.get("box_size", 10))
        border = int(self.args.get("border", 1))
        fill_color = self.args.get("fill_color", "black")
        back_color = self.args.get("back_color", "white")
        save = str(self.args.get("save", "False")).lower() == "true"
        path = self.args.get("file", "qr.png")
        if("/" not in path):
            path = f"./files/{path}"
        
        try:
            data = self.create_wifi_code(ssid, authentication_type, network_key)
        except Exception as e:
            print(e)
            return


        self.create_qr(data, version, box_size, border, fill_color, back_color, save, path)

    def create_wifi_code(self, ssid, authentication_type, password):
        if authentication_type == 'nopass':
            return f'WIFI:T:{authentication_type};S:{ssid};'
        elif authentication_type in ('WPA', 'WEP'):
            return f'WIFI:T:{authentication_type};S:{ssid};P:{password};'
        raise ValueError("Incompatible authentication_type")

    def create_qr(self, data, version, box_size, border, fill_color, back_color, save, path):
        qr = qrcode.QRCode(
            version=version,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=box_size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color=fill_color, back_color=back_color)
        img.show()

        if(save):
            img.save(path)