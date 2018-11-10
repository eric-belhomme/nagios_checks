check_unity.py
==============

This is a Nagios monitoring script for DELL EMC Unity storage box.

This work is a fork from https://github.com/rkferreira/nagios initial work.

usage:

    check_unity2.py [-h] -H HOSTADDRESS -u USER -p PASSWORD -m
        {battery,dae,disk,dpe,ethernetport,fan,fcport,iomodule,lcc,memorymodule,powersupply,sasport,ssc,ssd,storageprocessor,system,uncommittedport}

requirements:
* json
* requests

© 2018 Rodrigo Ferreira <rkferreira@gmail.com>  
© 2018 Eric Belhomme <rico-github@ricozome.net> published under MIT license