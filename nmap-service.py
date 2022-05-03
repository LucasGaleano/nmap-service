#! /usr/bin/env python3

from fastapi import File
import nmap
from repository import Repository
from datetime import datetime, timedelta
import json
import time
import configparser


def log_json(jsonFile, content: dict):
    content['timestamp'] = str(datetime.now().isoformat())
    content['app'] = "Nmap"
    print(json.dumps(content))
    jsonFile.write(json.dumps(content))
    jsonFile.write('\n')
    jsonFile.flush()

def is_ipv6(IP):
    return ':' in IP

config = configparser.ConfigParser()
config.read('nmap.conf')
sleepTime = int(config['nmap']['loopTime'])

jsonFile = open('log.json','a')
nma = nmap.PortScannerAsync()
nma_service = nmap.PortScanner()

def callback_result(host, scan_result):
    repo = Repository('ddbb')

    if not scan_result:
        log_json(jsonFile,{"message":"The scan failed to start"})
    elif not scan_result['scan']:
        log_json(jsonFile,{"message":f"No result for {host}"})
    else:
        for protocol in ['tcp','udp']:
            if protocol in scan_result['scan'][host]:
                for port in scan_result['scan'][host][protocol]:
                    arguments = f"-p {port} -sV -n -Pn"
                    if is_ipv6(host):
                        arguments += ' -6'
                    if protocol == 'udp':
                        arguments += ' -sU'
                    service = nma_service.scan(hosts=host, arguments=arguments, sudo=True)
                    try:
                        service = service['scan'][host][protocol][port]
                    except:
                        print("Error", service)
                        exit()
                    service['dstport'] = str(port)
                    service['dstip'] = host
                    service['protocol'] = protocol
                    service['type'] = 'common'
                    service['message'] = f"{host} {port}/{protocol}"

                    if repo.is_new_service(service['dstip'], service['dstport'], service['protocol'], service['state']):
                        service['type'] = 'new'
                        repo.add_new_service(host, str(port), protocol, service['state'])
                    log_json(jsonFile,service)

while True:

    nmapArguments = config["nmap"]["arguments"]
    nmapScopeFile = config["nmap"]["scopeFile"]

    start = time.time()
    log_json(jsonFile,{"message":"Starting Nmap"})

    with open(nmapScopeFile,'r') as networks:
        networks = [ip for ip in networks if not is_ipv6(ip)]
        networks = ' '.join([network.strip() for network in networks])
        nma.scan(hosts=networks, arguments=nmapArguments, callback=callback_result, sudo=True)

    while nma.still_scanning():
        nma.wait(100)

    with open(nmapScopeFile,'r') as networks:
        networks = [ip for ip in networks if is_ipv6(ip)]
        nmapArguments += ' -6'
        networks = ' '.join([network.strip() for network in networks])
        nma.scan(hosts=networks, arguments=nmapArguments, callback=callback_result, sudo=True)

    while nma.still_scanning():
        nma.wait(100)


    end = time.time()
    TimeTaken = int(end - start)
    sleepFor = max(sleepTime - TimeTaken, 0)
    log_json(jsonFile,{"message":"Nmap is done", "duration": str(timedelta(seconds=TimeTaken))})
    log_json(jsonFile,{"message": f"Waiting {timedelta(seconds=sleepFor)} hs"})
    time.sleep(sleepFor)
    
