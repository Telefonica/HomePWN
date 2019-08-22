from os import system, name, walk, _exit, getcwd, chdir
from os.path import join, dirname, abspath
from subprocess import Popen, PIPE
from utils.banner import banner
from utils.prompt import prompt
from utils.shell_options import ShellOptions
from utils.command_parser import CommandParser
from utils.custom_print import print_info
from utils.tasks import Task
from utils.color_palette import ColorSelected, colors_terminal


class Shell():
    
    def __init__(self):
        """Shell class that runs the HomePwn tool
        """
        # Check directory, we need to be in HomePwn directory
        home = dirname(abspath(__file__))
        if home != getcwd():
            chdir(home)
        self.command_parser = CommandParser()
        self.shell_options = ShellOptions.get_instance()
        self.color_selected = ColorSelected(colors_terminal["dark"])

    def console(self):
        """Runs the console
        """
        banner()
        while True:
            try:
                module_name = self.command_parser.get_module_name()
                options = self.shell_options.get_shell_options()
                user_input = prompt(options, module_name).strip(" ")
                self.command_parser.parser(user_input)
            except KeyboardInterrupt:
                print("CTRL^C")

if __name__ == "__main__":
    system('cls' if name=='nt' else 'clear')
    Shell().console()
