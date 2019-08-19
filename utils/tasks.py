from prompt_toolkit import print_formatted_text, HTML
from utils.custom_print import print_info, print_error
from os import kill
import signal
from time import sleep


class Task:
    __instance = None

    @staticmethod
    def get_instance():
        if Task.__instance == None:
            Task()
        return Task.__instance

    def __init__(self):
        if Task.__instance == None:
            Task.__instance = self
            self.tasks = {}
            self.count = 1
    
    def add_task(self, th, pid=None, seconds_wait=0):
        self.tasks[self.count] = {
            "thread":th,
            "pid": pid,
            "wait": seconds_wait # If we need to wait x second
        }
        self.count += 1

    def get_tasks(self):
        return self.tasks

    def kill_all_tasks(self):
        index =  []
        for i in self.tasks.keys():
            index.append(i)
        for task in index:
            self.kill_task(task)
        
    def exist_task(self, name):
        for k, v in self.tasks.items():
            th = v["thread"]
            if th.name == name and th.is_alive():
                return True
        return False
    
    def kill_task(self, index):
        try:
            i = int(index)
            th = self.tasks.get(i, None)
            if th:
                thread = th["thread"]
                pid = th["pid"] 
                name = thread.name
                try:
                    if pid:
                        kill(pid, signal.SIGINT)
                    # some task needs some time to stop
                    sleep(th["wait"])
                    thread.terminate()
                    thread.join()
                except:
                    pass
                del self.tasks[i]
                print_info(f"Task {index} - {name} has been killed")
            else:
                print_info("Task not found")
        except Exception as e:
            print(e)
            print_error("It has not been possible to kill the task")
        
    def show_tasks(self):
        if not len(self.tasks):
            print_info("There are no running tasks at this time")
            return
        print_formatted_text(HTML(f'''
<ansiyellow> Index (Thread)</ansiyellow>
-------------------------'''))
        flag = 0
        for key, value in self.tasks.items():
            pid = value.get("pid", "")
            if not pid:
                pid = ""
            flag += 1
            alive = "Alive" if value['thread'].is_alive() else "Death"
            if flag > 1:
                print (" |")
            print(f" |_ {key} = {value['thread'].name} {pid} ({alive})")
        print("")