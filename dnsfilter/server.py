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
import filters
import resolvers
import utils
import whitelists

"""
Module containing the main DNS server components.
"""

_LOG = logging.getLogger("dnsfilter.server")

class ServerFactory(server.DNSServerFactory):
    """
    A DNSServerFactory impl that allows interceptions of connection info
    """

    def __init__(self, clients):
        server.DNSServerFactory.__init__(self, clients=clients)

    def _get_addr(self, protocol, address):
        if address:
            return address[0]
        else:
            return protocol.transport.getPeer().host

    def handleQuery(self, message, protocol, address):
        _LOG.info("Handling query from "+str(self._get_addr(protocol, address)))
        server.DNSServerFactory.handleQuery(self, message, protocol, address)

def init(args):
    utils.init_logging(None, args.debug, args.quiet, args.logfile)

def _get_filter(args):
    # Create the filters list
    filter_list = []

    # If we want to record all requests, add the file logger filter
    if args.record:
        filter_list.append(filters.FileLoggerFilter(args.record))

    # Add the whitelist filter
    wl_filter = filters.WhitelistedDomainFilter(whitelists.load(args.url))
    filter_list.append(wl_filter)

    # Create and return the filter chain
    return filters.FilterChain(filter_list)

def start(args):
    """
    Run the dnsfilter server.
    """
    
    # Create the resolvers
    dns_resolver = client.Resolver(resolv='/etc/resolv.conf')
    filter_resolver = resolvers.FilterResolver(dns_resolver, _get_filter(args))
    
    # Create the controller
    factory = ServerFactory(clients=[filter_resolver])
    
    protocol = dns.DNSDatagramProtocol(controller=factory)
    
    reactor.listenUDP(args.port, protocol, args.addr)
    reactor.listenTCP(args.port, factory, 50, args.addr)

    _LOG.info("DNS server listening on %s:%d...", args.addr, args.port)
    reactor.run()

# Read options from CLI
parser = utils.init_argparser("Start the DNS server", { "port": 10053 })
parser.add_argument('--record', nargs='?', type=str,
    default=None, help="Enable domain recording")
args = parser.parse_args()

if __name__ == '__main__':
    init(args)
    raise SystemExit(start(args))
