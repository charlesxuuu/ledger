#!/usr/bin/python
# -*- coding: utf-8 -*-
# When web2py is run as a windows service (web2py.exe -W)
# it does not load the command line options but it
# expects to find conifguration settings in a file called
#
#   web2py/options.py
#
# this file is an example for options.py

import socket
import os

ip = '0.0.0.0'
port = 80
interfaces=[('0.0.0.0',80),('0.0.0.0',440,'test.key','test.crt')]
password = '<recycle>'  # ## <recycle> means use the previous password
pid_filename = 'httpserver.pid'
log_filename = 'httpserver.log'
profiler_filename = None
ssl_certificate = 'https/test.crt'  # ## path to certificate file
ssl_private_key = 'https/test.key'  # ## path to private key file
#numthreads = 50 # ## deprecated; remove
minthreads = None
maxthreads = None
server_name = socket.gethostname()
request_queue_size = 100
timeout = 120
shutdown_timeout = 5
folder = os.getcwd()
extcron = None
nocron = None

# After creating "options.py" in the web2py installation folder, you can 
# install web2py as a service with:
#
# 1. python web2py.py -W install
#
# and start/stop the service with:
#
# 1. python web2py.py -W start
# 2. python web2py.py -W stop
