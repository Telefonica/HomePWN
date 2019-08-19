from abc import ABC, abstractmethod
from prompt_toolkit import print_formatted_text, HTML
from utils.custom_print import  print_info, print_error
from utils.custom_exception import exception
from utils.global_list import Global
from utils.color_palette import ColorSelected

class Module(ABC):
    """Class from which all usable modules of the tool have to inherit
        
        Args:
            info (dict, required): Information about the module (Name, Description, Author, ...).
            options (dict, required): Module options  {name: [default_value, description, required?]}.
    """
    
    def __init__(self, info, options):
        self.options = options
        self.info = info
        self.name = ""
        self.args = {}
        self.init_args()
        self.update_global()
        self.update_options()

    def set_name(self, name):
        self.name = name
    
    def get_module_name(self):
        return self.name
    
    def get_options(self):
        return self.options

    def get_options_names(self):
        return list(self.options.keys())
    
    def get_info(self):
        return self.info

    def init_args(self):
        for key, opts in self.options.items():
            self.args[key] = opts.value

    def update_global(self):
        global_aux = Global.get_instance()
        variables = global_aux.get_variables()
        for key, value in self.options.items():
            try:
                if variables[key]:
                    continue
            except:
                global_aux.add_value(key, None)
    
    def update_options(self):
        variables = Global.get_instance().get_variables()
        for key, value in self.options.items():
            try:
                value = variables[key]
                if value:
                    self.options[key].value = value
                    self.args[key] = value
            except:
                pass

    @exception("Error when assigning value")
    def set_value(self, data):
        key = data[0]
        value = None
        if data[1]:
            value = ' '.join([str(x) for x in data[1:]])
        self.args[key] = value
        check = self.options[key].set_value(value)
        if not check:
            print_error("No pattern mach with this option")
            return False
        if not value:
            value = "Null"
        msg = key + " >> " + value
        print_info(msg)
        return True

    def unset(self, name=[""]):
        data = [name[0], None]
        self.set_value(data)
    
    def show(self, option = [""]):
        op = option[0]
        if op == "options":
            self._print_options()
        elif op == "info":
            self._print_info()
        else:
            self._print_info()
            self._print_options()

    def _print_options(self):
        print_formatted_text(HTML(f"<{ColorSelected().theme.accent}> Options (Field = Value)</{ColorSelected().theme.accent}>"))
        print (" -----------------------")
        flag = True
        options_aux = self.get_options()
        if not len(options_aux):
            print_info(" No options to configure")
            return
        for key, option in options_aux.items():
            if flag:
                print (" |")
                flag = False
            # Parameter is mandataroy
            if option.required:
                self._print_mandatory_option(key, option)
            # Parameter is optional
            else:
                self._print_optional_option(key, option)

        print ("\n")

    def _print_mandatory_option(self, key, option):
        if str(option.value) == "None":
            print_formatted_text(HTML(f''' |_[<{ColorSelected().theme.warn}>REQUIRED</{ColorSelected().theme.warn}>] \
{key}  = <{ColorSelected().theme.confirm}>{option.value}</{ColorSelected().theme.confirm}> ({option.description})'''))     
        else:
            print_formatted_text(HTML(f''' |_{key} = <{ColorSelected().theme.confirm}>{option.value} </{ColorSelected().theme.confirm}> ({option.description})'''))

    def _print_optional_option(self, key, option):
        if str(option.value) == "None":
            print_formatted_text(HTML(f" |_[OPTIONAL] {key} = <{ColorSelected().theme.confirm}>{option.value}</{ColorSelected().theme.confirm}> ({option.description})"))
        else:
            print_formatted_text(HTML(f" |_{key} = <{ColorSelected().theme.confirm}>{option.value}</{ColorSelected().theme.confirm}> ({option.description})"))

    def _print_info(self): 
        print_formatted_text(HTML(f"<{ColorSelected().theme.accent}>Module Info</{ColorSelected().theme.accent}>"))
        print("===========")
        for key, value in self.get_info().items():
            print_formatted_text(HTML(f"<{ColorSelected().theme.accent}> {key}</{ColorSelected().theme.accent}>"))
            print (' ' + '-' * len(key))
            print (f" |_{value}\n")

    def check_arguments(self):
        for key, option in self.options.items():
            if option.required is True and str(option.value) == "None":
                return False
        return True

    # Implement in specific classic if it's necessary to add some values to the 'set' autocomplete
    def update_complete_set(self):
        pass

    @abstractmethod
    def run(self):
        pass