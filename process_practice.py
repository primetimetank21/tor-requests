import os, signal
# import command
import time
import subprocess
from multiprocessing import Process

def run_tor():
    # subprocess.call("tor",stdout=None,stderr=None)
    # command.run(["tor"])
    os.execlp("tor", "tor")
    # os.exec


if __name__ == "__main__":
    process = Process(target=run_tor)
    process.start()
    time.sleep(5)
    child_pid = process.pid
    # process = Process(target=run_tor)
    # process.start()
    # child_pid = process.pid
    # print(child_pid)
    os.kill(child_pid, signal.SIGKILL)
    