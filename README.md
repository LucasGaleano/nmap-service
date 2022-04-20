# Nmap-service

## How it works

The program scans all the IPs from the file (file 'ips' by default) using the arguments parameter on the config file.
It will run every month or when the scanning is finished.
The results are in real time and will be logged in json format, through stdout and to the log.json file.
For the UDP ports will only scan the ports that found open without checking the service.


## How to install
`pip3 install -r requirements.txt`

For performance purpose, change the package file ~/.local/lib/python<version>/site-packages/nmap/nmap.py adding the parameters '-n'
From `output = self.scan(hosts, arguments="-sL")` to `output = self.scan(hosts, arguments="-sL -n")`

## How to configure
All settings are made in nmap.conf

```
[nmap]
scopeFile = ips
arguments = --min-rate 3000  --open -n -Pn -sT -sU -p-
;One month
loopTime = 2592000
```

