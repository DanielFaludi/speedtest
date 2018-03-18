#!/usr/bin/env python3

import re
import logging
import requests
import subprocess

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.debug('Start of program...')

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
    server_list = re.findall(r'<server url="([^"]*)" lat="([^"]*)" lon="([^"]*)"', reply)
    if server_list is None:
        logging.debug('Failed to obtain server list')
    server_list = [list(server) for server in server_list]
    s_lat_list = [float(server[1]) for server in server_list]
    s_lon_list = [float(server[2]) for server in server_list]
    closest_lat = min(s_lat_list, key=lambda x: abs(x - user_lat))
    closest_lon = min(s_lon_list, key=lambda x: abs(x - user_lon))

if __name__ == '__main__':
    choose_server()