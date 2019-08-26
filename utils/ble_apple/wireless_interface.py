from subprocess import Popen, PIPE
import os
import signal
from time import sleep

class BadInterfaceException(Exception):
    pass

class ModeMonitorException(Exception):
    pass

class OwlException(Exception):
    pass

def check_wifi_config(iwdev):
    """Restart the interface, change it to monitor mode and enable owl for airdrop
    
    Args:
        iwdev (str): Interface name
    
    Raises:
        Exception: Bad Interface Exception
        Exception: Mode monitor Exception
    """
    result = Popen(["iwconfig", iwdev], stdout=PIPE, stderr=PIPE)
    if(result.stderr.read()):
        # exception bad interface
        raise BadInterfaceException

    r = Popen(["rfkill", "list", "all"], stdout=PIPE, stderr=PIPE)
    r = Popen(["ifconfig", iwdev, "down"], stdout=PIPE, stderr=PIPE)
    result = Popen(["iwconfig", iwdev, "mode", "monitor"], stdout=PIPE, stderr=PIPE)
    if(result.stderr.read()):
        # exception mode montiro
        raise ModeMonitorException
    
    r = Popen(["ifconfig", iwdev, "up"], stdout=PIPE, stderr=PIPE)

    r = Popen(["ip", "link", "set", iwdev, "up"], stdout=PIPE, stderr=PIPE)

    owl_result = check_owl_process()

    if(owl_result):
        process_id = owl_result.lstrip(' ').split(" ")[0]
        os.kill(int(process_id), signal.SIGTERM)

    result = Popen(["owl", "-i", iwdev, "-N", "-D"], stdout=PIPE, stderr=PIPE)
    if(result.stderr.read()):
        raise OwlException


def check_owl_process():
    ps = Popen(["ps", "-A"], stdout=PIPE)
    grep = Popen(["grep", "owl"], stdin=ps.stdout, stdout=PIPE)
    return grep.stdout.read().decode()