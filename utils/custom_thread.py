from subprocess import Popen
import multiprocessing
from utils.custom_print import print_info
from utils.tasks import Task
 

# Custom Process (For the moment without customizing)
class CustomProcess(multiprocessing.Process): 
    def __init__(self, *args, **keywords): 
        """Parent name to execute the process
        
        Args:
            multiprocessing (multiprocessing.Process): Process to run
        """
        multiprocessing.Process.__init__(self, *args, **keywords) 
     

def new_process_command(command, name="Unknown"):
    """Runs a system command and saves it in Tasks
    
    Args:
        command (list/str): command to run
        name (str, optional): Name of the process. Defaults to "Unknown".
    """
    if not (type(command) == type([])):
        command = command.split(" ")
    q = multiprocessing.Queue()
    th = CustomProcess(name=name, target=_popen_run, args=(q, command))
    th.start()
    #th.join()
    pid = q.get()
    Task().get_instance().add_task(th, pid)
    print_info("Task running in background... use 'tasks list' to check")


def new_process_function(func, args=None, name="Unknown", seconds_to_wait=0):
    """Runs a python function and saves it in Task
    
    Args:
        func (func): Function type
        args (list, optional): List of args of the funcion. Defaults to None.
        name (str, optional): Name of the process. Defaults to "Unknown".
        seconds_to_wait (int, optional): Seconds to wait to execute the function. Defaults to 0.
    """
    try:
        if args:
            th = CustomProcess(name=name, target=func, args=(args,))
        else:
            th = CustomProcess(name=name, target=func)
        th.start()
        Task().get_instance().add_task(th, th.pid, seconds_to_wait)
        print_info("Task running in background... use 'tasks list' to check")
    except:
        pass
    
def _popen_run(q, command):
    p = Popen(command)
    #Get PID
    q.put(p.pid)