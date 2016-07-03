#!/usr/bin/python
#
# Copyright 2016 Deany Dean
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
import argparse
import logging
import filters
import os
import pwd
import resolvers
import socket
import whitelists

"""
Module containing utility components.
"""

_LOG = logging.getLogger("dnsfilter.utils")

_DEFAULT_LOG_FORMAT = '%(asctime)-15s [%(levelname)s] [%(module)s:%(lineno)d]  %(message)s'

def init_logging(fmt, debug, quiet, filename):
    """
    Init logging
    """
    if not fmt:
        fmt = _DEFAULT_LOG_FORMAT

    if debug:
        level = logging.DEBUG
    elif quiet:
        level = logging.ERROR
    else:
        level = logging.INFO

    logging.basicConfig(filename=filename, level=level, format=fmt)

def init_argparser(desc, defaults={}, is_server=True):
    """
    Init a default argparser
    """
    parser = argparse.ArgumentParser(description=desc)

    if is_server:
        parser.add_argument('--addr', nargs='?', type=str, default="", 
            help="IP address to listen on")
        parser.add_argument('--port', nargs='?', type=int, 
            default=defaults["port"], help="Port to listen on")

    parser.add_argument('--storage-url', nargs='?', type=str,
        default="mongo:localhost:27017:dnsfilter", 
        help="A storage service to use", dest="url")
    parser.add_argument("--debug", action="store_true", default=False,
        help="Enable debugging mode (verbose logging)")
    parser.add_argument("--quiet", action="store_true", default=False,
        help="Enable quiet mode (no logging)")
    parser.add_argument("--logfile", type=str, default=None,
        help="Name of the file to log to");

    return parser

def get_current_user():
    return pwd.getpwuid(os.getuid())[0]+"@"+socket.gethostname()
