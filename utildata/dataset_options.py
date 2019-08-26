import re


class Option:
    @staticmethod
    def create(name, value=None, description=None, required=False, pattern=None):
        ALL_OPTIONS = {
                    "rhost": RHOST,
                    "lhost": LHOST,
                    "timeout": Timeout,
                    "rport": RPORT,
                    "rports": RPORTS,
                    "verbose": Verbose,
                    "iface": Iface,
                    "file": File,
                    "uri": URI,
                    "channel": Channel,
                    "mac": MAC,
                    "bssid": MAC,
                    "bmac": MAC,
                    "apishodan": SHODAN
                } 
        cl = ALL_OPTIONS.get(name, None)
        if cl:
            if description:
                return cl(value, required, description)
            else:
                return cl(value, required)
        else:
            return GenericOption(name, value, required, description, pattern)

# Generic Option Class
class GenericOption:
    def __init__(self, key=None, value=None, required=False, description=None, match_pattern=None):
        self.key = key
        self.value = value
        self.required = required
        self.description = description
        self.match_pattern = match_pattern
    
    def _check_pattern(self, v):
        if self.match_pattern is None  or v is None:
            return True
        success = False
        if v:
            m = re.match(self.match_pattern, str(v))
            if m:
                success = True
        return success
    
    def set_value(self, v):
        success = self._check_pattern(v)
        if self._check_pattern(v):
            self.value = v
        return  success
    
    def get_option(self):
        return {self.key:[self.value, self.description, self.required]}

# Specific Options Classes

class RHOST(GenericOption):
    def __init__(self, value=None, required=False, description="Remote host IP", 
                match_pattern=r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$|^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\\\d+$"):
        key="rhost"
        super(RHOST, self).__init__(key, value, required, description, match_pattern)

class LHOST(GenericOption):
    def __init__(self, value=None, required=False, description="Local host IP", 
                match_pattern=r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$|^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\\\d+$"):
        key="rhost"
        super(LHOST, self).__init__(key, value, required, description, match_pattern)

class RPORT(GenericOption):
    def __init__(self, value=None, required=False, 
                description="Remote port (Example: 80)", match_pattern=r"^\d+$"):
        key="rport"
        super(RPORT, self).__init__(key, value, required, description, match_pattern)
    
class LPORT(GenericOption):
    def __init__(self, value=None, required=False, 
                description="Local port (Example: 8080)", match_pattern=r"^\d+$"):
        key="lport"
        
        super(LPORT, self).__init__(key, value, required, description, match_pattern)

class RPORTS(GenericOption):
    def __init__(self, value=None, required=False, 
                description="Remote ports (Example: 100-500)", match_pattern=r"^\d+-\d+$"):
        key="rports"
        super(RPORTS, self).__init__(key, value, required, description, match_pattern)

class Timeout(GenericOption):
    def __init__(self, value=None, required=False, 
                description="Timeout to wait for search responses. (In seconds)", match_pattern=r"^\d+$"):
        key="timeout"
        super(Timeout, self).__init__(key, value, required, description, match_pattern)

class Verbose(GenericOption):
    def __init__(self, value=False, required=False, description="Show extra info while running module",
                match_pattern = r"^True|False|true|false|TRUE|FALSE$"):
        key="verbose"
        super(Verbose, self).__init__(key, value, required, description, match_pattern)

class Iface(GenericOption):
    def __init__(self, value=None, required=False, description="Network/Bluetooth interface", match_pattern=None): 
        key="iface"
        super(Iface, self).__init__(key, value, required, description, match_pattern)

class File(GenericOption):
    def __init__(self, value=None, required=False, description="File to dump or read the data", match_pattern=None):
        key="file"
        super(File, self).__init__(key, value, required, description, match_pattern)

class URI(GenericOption):
    def __init__(self, value=None, required=False, description="URI", 
                match_pattern = r"^http://|^https://|rtsp://|ftp://"):
        key="uri"
        super(URI, self).__init__(key, value, required, description, match_pattern)

class Channel(GenericOption):
    def __init__(self,value=None, required=False, description="Network channel. Configure this option if you want to fix it and not 'make jumps'", match_pattern=r"^\d{1,2}$"):
        key="channel"
        super(Channel, self).__init__(key, value, required, description, match_pattern)

class MAC(GenericOption):
    def __init__(self, value=None, required=False, description="Mac address", match_pattern=r"^(?:[0-9a-fA-F]:?){12}$"):
        key="mac"
        super(MAC, self).__init__(key, value, required, description, match_pattern)

class SHODAN(GenericOption):
    def __init__(self, value=None, required=False, description="Shodan API Key"):
        key="shodan"
        super(SHODAN, self).__init__(key, value, required, description)