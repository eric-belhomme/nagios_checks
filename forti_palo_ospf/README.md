check_fw_ospf_routes.py
=======================

Retrieve the number of OSPF routes on Palto Alto firewalls throught CLI by SSH
Nagios check for OSPF routes count, for Fortinet and PaloAlto firewalls

Usage:

    check_fw_ospf_routes.py [-h] -H HOSTNAME -U USERNAME -P PASSWORD -t {paloalto,fortinet}
        [-p] [-w [WARNING]]
        [-c [CRITICAL]]

optional arguments:
* `-h`, `--help`  
  show this help message and exit
* `-H HOSTNAME`, `--hostname HOSTNAME`  
  hostname or IP address
* `-U USERNAME`, `--username USERNAME`  
  username
* `-P PASSWORD`, `--password PASSWORD`  
  user password
* `-t {paloalto,fortinet}`, `--type {paloalto,fortinet}`  
  FW type (PaloAlto, or Fortinet)
* `-p`, `--perfdata`  
  enable pnp4nagios perfdata
* `-w [WARNING]`, `--warning [WARNING]`  
  warning trigger
* `-c [CRITICAL]`, `--critical [CRITICAL]`  
  critical trigger

---
2018-10-29 Eric Belhomme <rico-github@ricozome.net> - Published under MIT license