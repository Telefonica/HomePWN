from time import sleep
import sys
import pytest
from io import StringIO
import os
from utils.dynamic_load import load_module
from utils.command_parser import CommandParser
from utils.shell_options import ShellOptions
import utils.custom_print as custom_print
from utils.customcompleter import CustomCompleter
from utils.custom_thread import new_process_function
from utils.tasks import Task
from utils.find import Find


@pytest.fixture
def load():
    def load_mod(module=""):
        try:
            print(module)
            return load_module(module)
        except:
            return None
    return load_mod

@pytest.fixture
def load_get_command_parser():
    def load_command_parser(module=""):
        cp = CommandParser()
        cp.parser(module)
        return cp
    return load_command_parser

### Check dynamic_load
# Check load module
def test_load_ok(load):
    home_module = load(module="discovery/mdns")

    assert (home_module is not None) and ("HomeModule" in str(home_module.__class__()))

def test_load_exception(load):
    assert load(module="noexist/hack") is None

# Check set action
def test_set_ok(load):
    home_module = load(module="discovery/mdns")
    assert home_module.set_value(["service", "_http._tcp.local."]) is True

def test_set_ko(load):
    home_module = load(module="discovery/mdns")
    try:
        home_module.set_value(["noexist", "_http._tcp.local."])
    except Exception as e:
        assert "Error when assigning value" == str(e)

### Check CommandParser
def test_load_and_unload(load_get_command_parser):
    cp = load_get_command_parser(module="load discovery/ble")
    assert cp.get_module_name() == "discovery/ble"
    cp.parser("back")
    assert cp.module is None

def test_bad_load(load_get_command_parser):
    cp = load_get_command_parser(module="load discovery/ideaslocas")
    assert cp.module is None

### Check shell_options
def test_shell_options(load_get_command_parser):
    so = ShellOptions.get_instance()
    general_opts = ["load",
                "help",
                "banner",
                "find",
                "import",
                "export",
                "modules",
                "tasks",
                "theme",
                "exit",
                "quit"]
                
    module_opts =  ["set", "unset", "global", "run", "back", "show"]
    s_o = so.get_shell_options()
    # before load module
    opts = list(s_o.keys())
    check_list(opts, general_opts)
    check_list(opts, module_opts, False)
    # Load module
    cp = load_get_command_parser(module="load discovery/ble")
    opts = list(s_o.keys())
    check_list(opts, general_opts)
    check_list(opts, module_opts, True)
    # Unload module
    cp.parser("back")
    opts = list(s_o.keys())
    check_list(opts, general_opts)
    check_list(opts, module_opts, False)

def check_list(opts, opts_list, in_list=True):
    for op in opts_list:
        if in_list:
            assert op in opts
        else:
            assert op not in opts

## Check completer
def test_autocomplete(load_get_command_parser):
    shell_options = ShellOptions.get_instance()
    options = shell_options.get_shell_options()
    completer = CustomCompleter(options)
    opts_list = list(options.keys())
    # First check that without text we can autocomplete all keys
    for opt in opts_list:
        assert completer._word_matches(opt, "") is True
    _ = load_get_command_parser(module="load discovery/ble")
    options = shell_options.get_shell_options()
    opts_list = list(options.keys())
    for opt in opts_list:
        assert completer._word_matches(opt, "") is True
    # Other check
    assert completer._word_matches("load", "lo") is True
    assert completer._word_matches("load", "h") is False

## Check custom_print
def test_custom_print_ok(capfdbinary):
    msg = "Done!"
    custom_print.print_ok(msg)
    cap = capfdbinary.readouterr()
    assert f"[+] {msg}" in cap.out.decode()

def test_custom_print_error(capfdbinary):
    msg = "Error..."
    custom_print.print_error(msg)
    cap = capfdbinary.readouterr()
    assert f"[!] {msg}" in cap.out.decode()

## Check tasks
def test_tasks():
    task = Task()
    assert task.count == 1
    assert len(task.get_tasks()) == 0
    new_process_function(to_test_th)
    assert task.count == 2
    assert len(task.get_tasks()) == 1
    task.kill_task(1)
    assert task.count == 2
    assert len(task.get_tasks()) == 0
    new_process_function(to_test_th)
    task.kill_task(1)
    assert task.count == 3
    assert len(task.get_tasks()) == 1
    task.kill_task(2)
    assert len(task.get_tasks()) == 0

def to_test_th():
    sleep(10)

## Check Finding
def test_find():
    find = Find()
    assert len(find.search("@josueencinar")) > 0
    assert len(find.search("@lucferbux")) > 0
    assert len(find.search("@pablogonzalezpe")) > 0
    assert len(find.search("@nooooexiiiissssstttthisssssteeeext!!!")) == 0