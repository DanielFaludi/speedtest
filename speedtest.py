#!/usr/bin/env python3

import os
import re
import logging
import requests
import bisect

from math import sqrt

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.debug('Start of program...')

def server_is_up(server):
    hostname = server
    response = os.system('ping -c 1 ' + hostname)
    if response == 0:
        os.system('cls' if os.name == 'nt' else 'clear')
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
    for server in server_adrr_list[:10]:
        if server_is_up(server[1]):
            chosen_server = server[1]
            return chosen_server
        else:
            continue
    if not chosen_server:
        logging.debug("Could not choose a server")

if __name__ == '__main__':
    choose_server()