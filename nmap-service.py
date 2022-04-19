#! /usr/bin/env python3

from fastapi import File
import nmap
from repository import repo
from datetime import datetime, timedelta
import json
import time
import configparser





def log_json(jsonFile, content: dict):
    content['timestamp'] = str(datetime.now())
    content['app'] = "Nmap"
    print(json.dumps(content))
    jsonFile.write(json.dumps(content))
    jsonFile.write('\n')
    jsonFile.flush()

config = configparser.ConfigParser()
config.read('nmap.conf')
nmapArguments = config["nmap"]["arguments"]
nmapScopeFile = config["nmap"]["scopeFile"]

jsonFile = open('log.json','a')
nma = nmap.PortScannerAsync()
nma_service = nmap.PortScanner()

def callback_result(host, scan_result):

    if not scan_result:
        log_json(jsonFile,{"message":"The scan failed to start"})
    else:
        for protocol in ['tcp','udp']:
            if protocol in scan_result['scan'][host]:
                for port in scan_result['scan'][host][protocol]:
                    arguments = f"--min-rate 3000 -p {port} -sV -n -Pn"
                    if protocol == 'udp':
                        arguments += ' -sU'
                    service = nma_service.scan(hosts=host, arguments=arguments, sudo=True)
                    try:
                        service = service['scan'][host][protocol][port]
                    except:
                        print("Error", service)
                        exit()
                    service['port'] = str(port)
                    service['host'] = host
                    service['protocol'] = protocol
                    service['type'] = 'common'
                    service['message'] = f"{host} {port}/{protocol}"

                    if repo.is_new_service(service['host'], service['port'], service['protocol'], service['state']):
                        service['type'] = 'new'
                        repo.add_new_service(host, str(port), protocol, service['state'])
                    log_json(jsonFile,service)

while True:

    start = time.time()
    log_json(jsonFile,{"message":"Starting Nmap"})

    with open(nmapScopeFile,'r') as networks:
        networks = ' '.join([network.strip() for network in networks])
        nma.scan(hosts=networks, arguments=nmapArguments, callback=callback_result, sudo=True)
        

    while nma.still_scanning():
        nma.wait(10)


    end = time.time()
    loopTime = 60 * 60 * 24 * 30 #one month
    TimeTaken = int(end - start)
    sleepFor = max(loopTime -TimeTaken, 0)
    log_json(jsonFile,{"message":"Nmap is done", "duration": str(timedelta(seconds=TimeTaken))})
    log_json(jsonFile,{"message": f"Waiting {timedelta(seconds=sleepFor)} hs"})
    time.sleep(sleepFor)
    