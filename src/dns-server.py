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

#
# A DNS server that will only resolve named from a set of white-listed domains
#
import argparse
from twisted.internet import reactor
from twisted.names import client, dns, server
from wlresolver import WhitelistResolver

DEFAULT_WHITELISTFILE = "etc/domain-whitelist.conf"

def start_dns_server(args):
    """
    Run the DNS server.
    """
    defResolver = client.Resolver(resolv='/etc/resolv.conf')
    wlResolver = WhitelistResolver(defResolver, args.whitelist)

    factory = server.DNSServerFactory(
        clients=[wlResolver]
    )
    
    protocol = dns.DNSDatagramProtocol(controller=factory)

    reactor.listenUDP(args.port, protocol)
    reactor.listenTCP(args.port, factory)

    reactor.run()

# Read options from CLI
parser = argparse.ArgumentParser(description="Start the DNS server")
parser.add_argument('--port', nargs='?', type=int, default=53,
    help="Port to listen on")
parser.add_argument('--whitelist', nargs='?',
    default=DEFAULT_WHITELISTFILE, help="The whitelist file")
args = parser.parse_args()

if __name__ == '__main__':
    raise SystemExit(start_dns_server(args))
