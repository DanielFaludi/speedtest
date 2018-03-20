#!/usr/bin/env python3

import os
import re
import logging
import bisect

try:
    import requests
except ImportError:
    raise ImportError("'requests' library is required for running this program")

from time import time
from multiprocessing import Process, current_process, Manager
from math import sqrt

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.debug('Start of program...')

DOWNLOAD_FILES = [
        '/speedtest/random350x350.jpg',
        '/speedtest/random500x500.jpg',
        '/speedtest/random1500x1500.jpg'
    ]

def server_is_up(server):
    hostname = server
    response = os.system('ping -c 1 ' + hostname)
    # os.system('cls' if os.name == 'nt' else 'clear')
    if response == 0:
        return True
    else:
        return False

def choose_server():
    get = requests.get('http://www.speedtest.net/speedtest-config.php?')
    if not get.status_code == 200:
        logging.debug('GET Request failed')
    reply = get.text
    coordinates = re.search(r'<client ip="([0-9.]*)" lat="([0-9.]*)" lon="([0-9.]*)"', reply)
    if coordinates is None:
        logging.debug('Failed to obtain location')
    location = coordinates.groups()
    user_lat = float(location[1]) 
    user_lon = float(location[2])
    get = requests.get('http://www.speedtest.net/speedtest-servers.php?')
    if not get.status_code == 200:
        logging.debug('GET Request failed')
    reply = get.text
    server_list = re.findall(r'<server url="http://([^/]*)/speedtest/upload\.php" lat="([^"]*)" lon="([^"]*)"', reply)
    if server_list is None:
        logging.debug('Failed to obtain server list')
    server_list = [list(server) for server in server_list]
    server_adrr_list = []
    for server in server_list:
        server_lat = float(server[1])
        server_lon = float(server[2])
        distance = sqrt(pow(server_lat - user_lat, 2) + pow(server_lon - user_lon, 2))
        bisect.insort_left(server_adrr_list, (distance, server[0]))
    chosen_server = ''
    for server in server_adrr_list[:10]:
        if server_is_up(server[1]):
            chosen_server = server[1]
            print(chosen_server)
            return chosen_server
    if not chosen_server:
        logging.debug("Could not choose a server")

def download_process(file, return_list):
    download = requests.get("http://" + host + file)
    return_list.append(len(download.content))

def download(host, runs):
    total_downloaded = 0
    start_time = time()
    process_manager = Manager()
    return_list = process_manager.list()
    processes = []
    for file in DOWNLOAD_FILES:
        for process in range(runs):
            process = Process(target=download_process, args=(file, return_list))
            process.start()
            processes.append(process)
        for process in processes:
            process.join()
    total_downloaded = sum(return_list)
    elapsed = (time() - start_time)
    megabits = total_downloaded / (1 * pow(10, 6)) * 8
    return megabits / elapsed

if __name__ == '__main__':
    host = choose_server()
    runs = 3
    download(host, runs)