from os import chdir, getcwd
from os.path import dirname, abspath

to_junmp = dirname(abspath(__file__))
chdir(to_junmp)
chdir("..")