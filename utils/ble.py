from bluepy.btle import UUID, Peripheral, Scanner, DefaultDelegate, BTLEDisconnectError
from utils.custom_print import print_info, print_ok, print_error
from utildata.ble_manufacturer import manufacturer


class BLE:

    def __init__(self, bmac, t):
        self.device = None
        self.bmac = bmac
        self.type = t

    def get_peripheral_device(self):
        return self.device

    ## CONNECTION BEGIN

    def connect(self):
       self.device = Peripheral(self.bmac, self.type)
       print_ok("connected")

    def disconnect(self):
        if self.device:
            self.device.disconnect()
            self.device = None
            print_info("\nDisconnected")

    ## CONNECTION END

    ## CHARACTERISTICS BEGIN
            
    def get_characteristics(self):
        try:
            return self.device.getCharacteristics()
        except:
            return self._get_characteristics_aux()
    
    def _get_characteristics_aux(self):
        try:
            characteristics = []
            for service in self.device.services:
                for ch in service.getCharacteristics():
                    characteristics.append(ch)
            return characteristics
        except:
            return None
    
    def get_characteristic_by_uuid(self, uuid):
        try:
            return self.device.getCharacteristics(uuid=uuid)[0]
        except:
            return self._get_characteristic_by_uuid_aux(uuid)

    def _get_characteristic_by_uuid_aux(self, uuid):
        try:
            for ch in self._get_characteristics_aux():
                if ch.uuid == uuid:
                    return ch
        except:
            return None

    ## CHARACTERISTICS END
        
    ## READ BEGIN

    def read_specific_characteristic(self, uuid):
        ch = self.get_characteristic_by_uuid(uuid)
        if ch:
            self._print_char(ch)

    def read_all_characteristics(self):
        characts = self.get_characteristics()
        if characts:
            self._print_characteristics(characts)

    
    def _print_characteristics(self, characteristics, uuid=None):
        for ch in characteristics:
            try:
                self._print_char(ch)
            except:
                pass

    def _print_char(self, ch):
        print_info(f"<b>{ch.uuid.getCommonName()}</b>")
        print_info(f"|_ uuid: {str(ch.uuid).split('-')[0]}")
        handle = ch.handle
        print_info(f"|_ handle: {hex(handle)} ({handle})")
        if (ch.supportsRead()):
            try:
                data = ch.read()
                data_decode = data.decode(errors="ignore")
                if data_decode:
                    data = f"{data_decode}"
                print_info(f"|_ value: {data}")
            except:
                try:
                    print_info(f"|_ value: {data}")
                except:
                    print_info("|_ value: <ansired>Couldn't read</ansired>")
        print_info(f"|_ properties: {ch.propertiesToString()}")

    ## READ END

    ## WRITE BEGIN

    def write_data(self, data, uuid):
        try:
            characteristics = self.get_characteristics()
            for ch in characteristics:
                if ch.uuid == uuid:
                    if self._is_writable(ch.propertiesToString()):
                        print_ok("Good! It's writable!")
                        try:
                            ch.write(data)
                            print_ok("Done!")
                        except:
                            print_error("It has not been written")
                    else:
                        print_error("It is not writable")
        except:
            pass

    def _is_writable(self, properties):
        return "WRITE" in properties

    ## WRITE END
    

    ## SUBSCRIBE BEGIN

    def subscribe(self):
        while True:
            try:
                self.device.waitForNotifications(1.0)
            except KeyboardInterrupt:
                print("Module Interrupted")
                return True
            except BTLEDisconnectError:
                print_error("Device disconnected...")
            except:
                self.disconnect()

    def set_delegate(self, delegate):
        self.device.setDelegate(delegate())

    ## SUBSCRIBE END



## Scan class
class Scan:
    def scan_devices(self, delegate=DefaultDelegate, timeout=5):
        devices = Scanner().withDelegate(delegate()).scan(timeout=timeout) 
        return self._package_data_devices(devices)

  
    def _package_data_devices(self, devices):
        all_dev = {}
        for dev in devices:
            db = dev.rssi
            complete_name = dev.getValueText(9)
            if complete_name is None:
                complete_name = "unknown"

            try:
                m = dev.getValueText(255)
                key = "0x" + m[:4].upper()
                vendor = manufacturer.get(key, "unknown")
            except:
                vendor = "unknown"

            data = {
                "mac": dev.addr,
                "name": str(complete_name).strip().replace("\x00", ""),
                "connectable": dev.connectable,
                "manufacturer": vendor,
                "addrType": dev.addrType
            }
            res = all_dev.get(db, None)
            if res:
                all_dev[db].append(data)
            else:
                all_dev[db] = [data]

        return all_dev 

    def show_devices(self, devices, rssi):
        try:
            rssi = int(rssi)
        except:
            rssi = None
        if not devices:
            print_info("Not devices found")
        header = "  RSSI          Addr               Manufacter            Name         Connectable     AddrType  "
        print("")
        print(header)
        print("-"*len(header))
        for db in sorted(devices.keys(), reverse=True):
            db = int(db)
            try:
                if str(rssi) != "None" and db < rssi: 
                    return

                for dev in devices[db]:
                    self._print_device(dev, db)
            except:
                pass

    def _print_device(self, dev, db):
        color = "brightgreen"
        if db < -72:
            color = "brightred"
        elif db < -60:
            color = "brightyellow"

        if str(dev['connectable']) == "True":
            conn = "      <ansigreen>✔</ansigreen>        " 
        else:
            conn = "      <ansired>X</ansired>        "

        manufacturer =  self._fill_spaces(dev["manufacturer"], 20)
        name = self._fill_spaces(dev["name"], 14)
        
        print_info(f"[<ansi{color}>{db} dB</ansi{color}>]  {dev['mac']}   {manufacturer}   {name}  {conn}   {dev['addrType']}")
        print("")
   
    # To keep the format (Fill with white spaces)
    def _fill_spaces(self, data, total_len):
        aux_len = len(data)
        if total_len <= aux_len:
            return data[:total_len]
        length = int( (total_len - aux_len) / 2)
        to_return = " "*length + data + " "*length
        if aux_len % 2:
            to_return += " "
        return to_return       