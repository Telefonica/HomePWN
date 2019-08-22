import pytest
from os import walk
from os.path import join
from utils.dynamic_load import load_module


@pytest.fixture
def load():
    def load_mod(module=""):
        try:
            print(module)
            return load_module(module)
        except:
            return None
    return load_mod

# Check all modules
def test_load_all_modules(load):
    pwd = "./modules"
    for (p, _, files) in walk(pwd):
        for f in files:
            if ("_" not in f) and ("_" not in p):
                home_module = load(module=join(p.replace("./modules/", ""), f.replace(".py", "")))
                assert (home_module is not None) and ("HomeModule" in str(home_module.__class__())), f"{f} failed!!"