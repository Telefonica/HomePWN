import os
from subprocess import Popen, PIPE
from signal import SIGTERM


def kill_process_by_name(name):
    ps = Popen(["ps", "-e"], stdout=PIPE)
    grep = Popen(["grep", name], stdin=ps.stdout, stdout=PIPE)
    ps.stdout.close()
    data = grep.stdout.read().decode()

    if data:
        print(f"Active processes with name {name} have been found")
        lines = data.split("\n")
        for line in lines:
            pid = line.split(" ")[0]
            if pid:
                print(f"killing {pid}...")
                os.kill(int(pid), SIGTERM)
