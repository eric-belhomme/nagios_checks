check_elasticsearch.py
======================

A Nagios plugin that checks ElasticSearch health status

Usage:

    check_elasticsearch.py [-h] -H HOSTNAME -U USERNAME -P PASSWORD [-p [PORT]] [-s] [-d]

optional arguments:

* `-h, --help`  
  show this help message and exit
* `-H HOSTNAME`, `--hostname HOSTNAME`  
  Elastic server hostname or IP address
* `-U USERNAME`, `--username USERNAME`  
  username
* `-P PASSWORD`, `--password PASSWORD`  
  user password
* `-p [PORT]`, `--port [PORT]`  
  listening port
* `-s`, `--ssl`  
  use SSL/TLS layer
* `-d`, `--perfdata`  
  enable Nagios perf data

---
2018-10-31 Eric Belhomme <rico-github@ricozome.net> - Published under MIT license