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
from twisted.names import client, dns, server
import resolvers

"""
    Module containing the main DNS server components.
"""

_LOG = logging.getLogger("dnsfilter.server")

def init(args):
    # Set the default logging config
    FORMAT = '%(asctime)-15s %(message)s'
    logging.basicConfig(level=logging.INFO, format=FORMAT)

def start(args):
    """
    Run the DNS server.
    """
    defResolver = client.Resolver(resolv='/etc/resolv.conf')
    mainResolver = resolvers.AllowedDomainResolver(defResolver, args.storage_url)

    factory = server.DNSServerFactory(
        clients=[mainResolver]
    )
    
    protocol = dns.DNSDatagramProtocol(controller=factory)

    reactor.listenUDP(args.port, protocol, args.addr)
    reactor.listenTCP(args.port, factory, 50, args.addr)

    _LOG.info("DNS server listening on %s:%d...", args.addr, args.port)
    reactor.run()

# Read options from CLI
parser = argparse.ArgumentParser(description="Start the DNS server")
parser.add_argument('--addr', nargs='?', type=str, default="", 
    help="IP address to listen on")
parser.add_argument('--port', nargs='?', type=int, default=53,
    help="Port to listen on")
parser.add_argument('--storage-url', nargs='?',
    default="mongo:localhost:27017:dns_filter", help="A storage service to use",
    dest="storage_url")
args = parser.parse_args()

if __name__ == '__main__':
    init(args)
    raise SystemExit(start(args))
