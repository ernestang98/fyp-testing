import asyncio
import websockets
import requests
import sys
import argparse
import logging
import json
import time
import datetime

logging.basicConfig(encoding='utf-8', level=logging.INFO)

WS_INGRESS = ""

HTTP_INGRESS = ""


async def connect_to_worker():
    try:
        async with websockets.connect(WS_INGRESS) as websocket:
            data = await websocket.recv()
            return json.loads(data)
    except Exception as E:
        return False


async def connect_to_server():
    try:
        async with websockets.connect(WS_INGRESS) as websocket:
            return True
    except Exception as E:
        return False

 
def connect_to_server_wrapper():
    try:
        websocket_connection = asyncio.get_event_loop().run_until_complete(connect_to_server())
        assert websocket_connection
        status_code = int(requests.get(url = HTTP_INGRESS).status_code)
        assert (status_code >= 200) and (status_code < 300)
        return True
    except:
        return False


def connect_to_worker_wrapper():
    try:
        websocket_connection = asyncio.get_event_loop().run_until_complete(connect_to_worker())
        #logging.info("Checking status of workers: {}".format(websocket_connection))
        num_workers_available = websocket_connection["num_workers_available"]
        assert num_workers_available
        num_workers_available = len(num_workers_available)
        assert num_workers_available > 0
        return True
    except:
        return False


class SmartFormatter(argparse.HelpFormatter):
    def _split_lines(self, text, width):
        if text.startswith('R|'):
            return text[2:].splitlines()  
        return argparse.HelpFormatter._split_lines(self, text, width)


class MetricsManager():
    def __init__(self):
        self.total_count = 0
        self.total_successes = 0

    def retrieve_statistics(self):
        if self.total_count != 0:
            return self.total_successes/self.total_count
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=SmartFormatter)
    parser.add_argument("-t", "--target", type=int, default=0, help="R|1: Master Pod\n2: Worker Pod\n3: System (Both Pods)", required=True)
    parser.add_argument("-d", "--duration", type=float, default=0, help="Duration of Chaos Experiment in minutes (should match duration specified in chaos testing tool)", required=True)
    args = parser.parse_args()

    target = args.target
    duration = args.duration

    serverMetricsManager = MetricsManager()
    workerMetricsManager = MetricsManager()

    now = datetime.datetime.utcnow()

    while datetime.datetime.utcnow() < (now + datetime.timedelta(minutes=duration)):		
        serverMetricsManager.total_count += 1
        workerMetricsManager.total_count += 1
        if target == 1:
            if connect_to_server_wrapper():
                serverMetricsManager.total_successes += 1
        elif target == 2:
            if connect_to_worker_wrapper():
                workerMetricsManager.total_successes += 1
        elif target == 3:
            if connect_to_server_wrapper():
                serverMetricsManager.total_successes += 1
            if connect_to_worker_wrapper():
                workerMetricsManager.total_successes += 1
        else:
            logging.error("Argument -t {} does not match options 1, 2, or 3!".format(target))
            sys.exit(1)
            break
    
    if target == 1:
        stats = "{:.1%}".format(serverMetricsManager.retrieve_statistics())
        logging.info(f"Server is up {stats}")
    elif target == 2:
        stats = "{:.1%}".format(workerMetricsManager.retrieve_statistics())
        logging.info(f"Worker is up {stats}")
    elif target == 3:
        stats = "{:.1%}".format(serverMetricsManager.retrieve_statistics())
        logging.info(f"Server is up {stats}")
        stats = "{:.1%}".format(workerMetricsManager.retrieve_statistics())
        logging.info(f"Worker is up {stats}")
    else:
        logging.error("Argument -t {} does not match options 1, 2, or 3!".format(target))
        sys.exit(1)

    logging.info("Verification completed!")
    sys.exit(0)
