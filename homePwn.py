from os import _exit
from os import system, name, walk
from os.path import join
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
        self.command_parser = CommandParser()
        self.shell_options = ShellOptions.get_instance()
        self.color_selected = ColorSelected(colors_terminal["dark"])

    def console(self):
        """Runs the console
        """
        banner()
        while True:
            module_name = self.command_parser.get_module_name()
            options = self.shell_options.get_shell_options()
            user_input = prompt(options, module_name).strip(" ")
            self.command_parser.parser(user_input)

if __name__ == "__main__":
    try:
        system('cls' if name=='nt' else 'clear')
        Shell().console()
    except KeyboardInterrupt:
        print_info("... Killing tasks")
        Task().get_instance().kill_all_tasks()
        print_info("Bye")
        _exit(0)

