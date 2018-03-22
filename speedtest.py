#!/usr/bin/env python3

import re
import sys
import string
import bisect
import logging
import subprocess

try:
    import requests
except ImportError:
    raise ImportError(
        "'requests' library is required for running this program")

from time import time
from multiprocessing import Process, Manager
from math import sqrt
from itertools import cycle

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DOWNLOAD_FILES = [
    '/speedtest/random350x350.jpg',
    '/speedtest/random500x500.jpg',
    '/speedtest/random1500x1500.jpg'
]

def server_is_up(server):
    ''' Pings server, returns True if server is up '''
    hostname = server
    try:
        subprocess.check_output(
            ['ping', '-c', '1', hostname],
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        return True
    except subprocess.CalledProcessError:
        return False

def choose_server():
    ''' Chooses server based on location '''
    get = requests.get('http://www.speedtest.net/speedtest-config.php?')
    if not get.status_code == 200:
        logging.info('GET Request failed')
    reply = get.text
    coordinates = re.search(r'<client ip="([0-9.]*)" lat="([0-9.]*)" lon="([0-9.]*)"', reply)
    if coordinates is None:
        logging.info('Failed to obtain location')
    location = coordinates.groups()
    user_lat = float(location[1])
    user_lon = float(location[2])
    get = requests.get('http://www.speedtest.net/speedtest-servers.php?')
    if not get.status_code == 200:
        logging.info('GET Request failed')
    reply = get.text
    server_list = re.findall(r'<server url="http://([^/]*)/speedtest/upload\.php" lat="([^"]*)" lon="([^"]*)"', reply)
    if server_list is None:
        logging.info('Failed to obtain server list')
    server_list = [list(server) for server in server_list]
    server_adrr_list = []
    for server in server_list:
        server_lat = float(server[1])
        server_lon = float(server[2])
        distance = sqrt(pow(server_lat - user_lat, 2) +pow(server_lon - user_lon, 2))
        bisect.insort_left(server_adrr_list, (distance, server[0]))
        chosen_server = ''
    for server in server_adrr_list[:10]:
        if server_is_up(server[1]):
            chosen_server = server[1]
            logging.info('Chosen server: {}'.format(chosen_server))
            return chosen_server
    if not chosen_server:
        logging.info("Could not choose a server")

def download_process(host, file, return_list):
    ''' Target for download processes '''
    download = requests.get("http://" + host + file)
    return_list.append(len(download.content))

def download(host, runs):
    ''' Measures and outputs download speed '''
    process_manager = Manager()
    return_list = process_manager.list()
    processes = []
    start_time = time()
    for file in DOWNLOAD_FILES:
        for process in range(runs):
            process = Process(target=download_process, args=(host, file, return_list))
            process.start()
            processes.append(process)
        for process in processes:
            process.join()
    total_downloaded = sum(return_list)
    elapsed = (time() - start_time)
    megabits = total_downloaded / (1 * pow(10, 6)) * 8
    speed = megabits / elapsed
    logging.info("Download speed: {} Mbps".format(round(speed, 2)))
    return speed

def upload_process(host, data, return_list):
    ''' Target for upload processes '''
    PARAMS = {
        'Connection': 'Keep-Alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'content0': data
    }

    url = ('http://' + host + '/speedtest/upload.php?x=')
    upload = requests.post(url, data=PARAMS)
    reply = upload.text
    return_list.append(int(reply.split('=')[1]))

def upload(host, runs):
    ''' Measures and outputs upload speed '''
    size = 675000  # 5 Mbits
    data = rand_string(size)
    process_manager = Manager()
    return_list = process_manager.list()
    processes = []
    start_time = time()
    for process in range(runs):
        process = Process(target=upload_process, args=(host, data, return_list))
        process.start()
        processes.append(process)
    for process in processes:
        process.join()
        elapsed = time() - start_time
        upload = sum(return_list)
        megabits = upload / (1 * pow(10, 6)) * 8
        speed = megabits / elapsed
        logging.info("Upload speed: {} Mbps".format(round(speed, 2)))
        return speed

def rand_string(size):
    ''' Generates a random string based on size (in Bytes) '''
    all_chars = string.digits + string.ascii_letters
    cycle_through = cycle(all_chars)
    return ''.join(next(cycle_through) for i in range(size))


def main():
    logging.info('Start of program...')
    if len(sys.argv) > 2:
        runs = sys.argv[1]
    else:
        runs = 3
    host = choose_server()
    download(host, runs)
    upload(host, runs)
    logging.info("End of program...")
    
if __name__ == '__main__':
    main()
