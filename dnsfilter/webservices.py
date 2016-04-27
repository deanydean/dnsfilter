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
from twisted.internet import reactor
from twisted.web import server, resource, http
import whitelists

"""
Module containing the webservices interface.
"""

_LOG = logging.getLogger("dnsfilter.webservices")

class DNSFilterWebservice(resource.Resource):

    """
    Twisted web resource impl that handles the webservice requests
    """

    def __init__(self, storage_url):
        self.storage_url = storage_url
        resource.Resource.__init__(self)

    def getChild(self, path, request):
        return DNSFilterWebservice(self.storage_url)

    def render_GET(self, request):
         request.setResponseCode(http.NOT_IMPLEMENTED)
         return "NOT IMPLEMENTED\n"

    def render_DELETE(self, request):
        request.setResponseCode(http.NOT_IMPLEMENTED) 
        return "NOT IMPLEMENTED\n"

    def render_PUT(self, request):
        request.setResponseCode(http.NOT_IMPLEMENTED) 
        return "NOT IMPLEMENTED\n"

    def render_POST(self, request):
        return self.render_PUT(request)

def init(args):
    # Set the default logging config
    FMT = '%(asctime)-15s [%(levelname)s] [%(module)s:%(lineno)d]  %(message)s'
    logging.basicConfig(level=logging.INFO, format=FMT)

def start(args):
    """
    Run the dnsfilter webservices.
    """
    webservice = DNSFilterWebservice(args.url)
    
    reactor.listenTCP(args.port, server.Site(webservice), 80, args.addr)

    _LOG.info("DNS filter webservices listening on %s:%d...", args.addr, args.port)
    reactor.run()

# Read options from CLI
parser = argparse.ArgumentParser(description="Start the DNS filter webservices")
parser.add_argument('--addr', nargs='?', type=str, default="", 
    help="IP address to listen on")
parser.add_argument('--port', nargs='?', type=int, default=8080,
    help="Port to listen on")
parser.add_argument('--storage-url', nargs='?', type=str,
    default="mongo:localhost:27017:dnsfilter", help="A storage service to use",
    dest="url")
args = parser.parse_args()

if __name__ == '__main__':
    init(args)
    raise SystemExit(start(args))
