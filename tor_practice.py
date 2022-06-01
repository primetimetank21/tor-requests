import requests
import os
import signal
import time
from multiprocessing import Process
from fake_useragent import UserAgent
from stem import Signal
from stem.control import Controller

def new_tor_id():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM)

def run_tor():
    STDOUT = 1
    os.dup2(os.open(os.devnull, os.O_WRONLY), STDOUT)
    os.execlp("tor", "tor")

def is_tor_activated(session:requests.Session, url:str):
    try:
        if requests.get(url).text == session.get(url).text:
            print("Unprotected: tor not activated")
            return None
    except:
        try:
            # print("Attempting to start tor")
            process = Process(target=run_tor)
            process.start()
            child_pid = process.pid
            return child_pid

        except Exception as exception:
            print(exception)
            return None

def main():
    url = "http://httpbin.org/ip"
    with requests.Session() as session:
        session.proxies = {"http": "socks5://127.0.0.1:9050",
                           "https": "socks5://127.0.0.1:9050",
        }
        session.headers = {"User-Agent": UserAgent().random}
        child_pid = is_tor_activated(session, url)
        print(session.headers)
        r = requests.get(url)
        print(f"Real IP: {r.json()}")
        while True:
            try:
                new_tor_id()
                print(" " * (os.get_terminal_size().columns -  1), end="\r")
                r_sesh = session.get(url)
                print(f"Proxy IP: {r_sesh.json()}", flush=True)
                break
            except:
                print("Retrying...",end="\r")
                time.sleep(3)
        if child_pid:
            print(f"Killing tor (PID: {child_pid})")
            os.kill(child_pid, signal.SIGKILL)


if __name__ == "__main__":
    main()