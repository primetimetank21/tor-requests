import requests
import aiohttp
from aiohttp_socks import ProxyConnector
import asyncio
import os
import signal
from multiprocessing import Process
from fake_useragent import UserAgent
from stem import Signal
from stem.control import Controller

#TODO:
# - tor practice with aiohttp session
#  => create coroutine so asyncio can create tasks

def new_tor_id():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM)

def run_tor():
    STDOUT = 1
    os.dup2(os.open(os.devnull, os.O_WRONLY), STDOUT)
    os.execlp("tor", "tor")

def activate_tor():
    try:
        process = Process(target=run_tor)
        process.start()
        child_pid = process.pid
        return child_pid
        
    except Exception as exception:
        print(exception)
        return None

async def get_data(session:aiohttp.ClientSession, url:str) -> aiohttp.ClientResponse:
    for _ in range(5):
        try:
            headers = {"User-Agent": UserAgent().random}
            new_tor_id()
            r_sesh = await session.get(url, headers=headers)
            r_sesh_json = await r_sesh.json()
            return r_sesh_json 
        except Exception as e:
            print(e)
            await asyncio.sleep(3)
    return None


async def main():
    urls = ["http://httpbin.org/ip" for _ in range(50)]
    proxy = "socks5://127.0.0.1:9050"
    proxy_connector = ProxyConnector.from_url(proxy)
    r = requests.get("http://httpbin.org/ip")
    print(f"Real IP: {r.json()}")
    child_pid = activate_tor()
    async with aiohttp.ClientSession(connector=proxy_connector) as session:
        tasks = [asyncio.create_task(get_data(session,url)) for url in urls]
        responses = await asyncio.gather(*tasks)
        print(responses)

    if child_pid:
        print(f"Killing tor (PID: {child_pid})")
        os.kill(child_pid, signal.SIGKILL)


if __name__ == "__main__":
    asyncio.run(main())
