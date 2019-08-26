from os import _exit, walk
from os.path import join
from subprocess import Popen, PIPE
from utils.shell_options import ShellOptions
from utils.dynamic_load import load_module
from utils.custom_exception import exception
from utils.custom_print import  print_info, print_error, print_ok
from utils.banner import banner
from utils.global_list import Global
from utils.help import show_help
from utils.find import Find
from utils.tasks import Task
from utils.color_palette import ColorSelected, colors_terminal


class CommandParser:
    def __init__(self):
        self.module = None
        self.module_commands = ["set", "unset", "back", "show", "run", "global"]
        # Our switcher
        self.commands = {
            "load": self._load,
            "help": self._help,
            "banner": self._banner,
            "find": self._find,
            "import": self._fill,
            "export": self._save,
            "modules": self._list_modules,
            "theme": self._load_theme,
            "tasks": self._task,
            "exit": self._exit,
            "quit": self._exit,
        }
        self.shell_options = ShellOptions.get_instance()
    
    # 'command' is the user input
    @exception("Error parsing input")
    def parser(self, command):
        if not command:
            return

        if command.startswith("#"):
            self._execute_command(command[1:])
        else:
            u_input = command.split()
            if len(u_input) >=  2:
                self.commands.get(u_input[0])(u_input[1:])
            else:
                self.commands.get(u_input[0])()
    
    def update_module(self, value):
        self.module = value

    def get_module_name(self):
        name = ""
        if self.module:
            name = self.module.get_module_name()
        return name
    
    def _exit(self, param=None):
        print_info("Killing tasks... ")
        Task().get_instance().kill_all_tasks()
        print_info("Bye...")
        _exit(0)

    # Execute a system command
    @exception("Error Executing OS Command")
    def _execute_command(self, command):
        data = Popen(command, shell=True, stdout=PIPE).stdout.read()
        print("")
        print(data.decode(errors="ignore"))

    def _load_theme(self, theme):
        theme = colors_terminal.get(theme[0], None)
        if theme is not None:
            ColorSelected(theme)
            print_ok("Theme changed!")
        else:
            print_error("Theme not available")


    def _load(self, name):
        try:
            loaded = load_module(name[0])
        except Exception as e:
            print(e)
        if loaded:
            self._unload()
            self.module = loaded
            self.module.set_name(name[0])
            new_functions = self.module.get_new_functions()
            self.shell_options.add_module_options(self.module.get_options_names(), new_functions)
            # Add new commands to autocomplete
            module_new_commands = {
                "set": self.module.set_value,
                "global": self._setglobal,
                "unset": self.module.unset,
                "back": self._unload,
                "show": self.module.show,
                "run": self._run
            }

            for f in new_functions:
                if f not in list(module_new_commands.keys()):
                    module_new_commands[f] = getattr(self.module, f)
                    self.module_commands.append(f)

            self.commands.update(module_new_commands) 
            self.module.update_complete_set()
            
    @exception("")    
    def _unload(self):
        self.module = None
        # Remove commands that cannot be used without a module
        self.shell_options.del_module_options()
        for c in self.module_commands:
            try:
                del self.commands[c]
            except:
                 self.module_commands.remove(c)
        for f in self.module.get_new_functions():
            del self.commands[f]
    
    @exception("Error setting global option")
    def _setglobal(self, user_input=[]):
        if user_input and self.module:
            success = self.module.set_value(user_input)
            if success:
                Global.get_instance().add_value(user_input[0], ' '.join([str(x) for x in user_input[1:]]))
            
    @exception("There are required options without value")  
    def _run(self):
        if not self.module.check_arguments():
            raise("")
        try:
            self.module.run()  
        except Exception as e:
            print(e) 
    
    def _fill(self, param=None):
        Global.get_instance().load_configuration()
    
    def _save(self, param=None):
        Global.get_instance().save_configuration()

    def _banner(self, param=None):
        banner(animation=False)     
        
    def _help(self, param=None):
        data = None
        if self.module:
            data = self.module.get_extra_help()
        show_help(data)

    def _list_modules(self, category=None):
        pwd = "./modules"
        if category != None:
            pwd += "/" + category[0]
        print("")
        msg = "Modules list                     "
        print(msg)
        print("-"*len(msg))
        total = 0
        for (p, d, files) in walk(pwd):
            for f in files:
                 if ("_" not in f) and ("_" not in p):
                     print_info(join(p.replace("./modules/", ""), f.replace(".py", "")))
                     total += 1
        print("-"*len(msg))
        print_info(f"Modules count: <b>{total}</b>")
        print("")

    def _find(self, word=""):
        word = ' '.join(word).lower()
        data = f"Searching: {word}"
        print_info(data)
        print("-"*len(data))
        modules = Find().search(word)
        if not modules:
            print_info("No found")
            return
        for module in modules:
            print_info(module)
        print("-"*len(data))
        print_info(f"Modules count: <b>{len(modules)}</b>")
    
    def _task(self, params):
        if "list" in params:
            Task().get_instance().show_tasks()
        elif "kill" in params and len(params) >= 2:
            Task().get_instance().kill_task(params[1])