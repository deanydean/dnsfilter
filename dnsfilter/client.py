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
import whitelists

"""
    Module containing the main DNS server components.
"""

DEFAULT_STORAGEURL = "mongo:localhost:27017:dns_filter"

_LOG = logging.getLogger("dnsfilter.clients")

def _init(args):
    # Set the default logging config
    FMT = '%(asctime)-15s [%(levelname)s] [%(module)s:%(lineno)d]  %(message)s'
    logging.basicConfig(level=logging.INFO, format=FMT)

def _add_allowed_domains(domains, whitelist):
    for domain in domains:
        if whitelist.contains(domain):
            _LOG.info("Domain %s already in whitelist", domain)
        else:
            whitelist.add(domain)
            _LOG.info("Added domain %s", domain)

def _delete_allowed_domains(domains, whitelist):
    for domain in domains:
        if whitelist.contains(domain):
            whitelist.delete(domain)
            _LOG.info("Deleted domain %s", domain)
        else:
            _LOG.info("Domain %s is not in whitelist", domain)

def _get_allowed_domains(domains, whitelist):
    allowed_domains = []
    
    if not domains:
        allowed_domains = whitelist.get_all()
    else:
        for domain in domains:
            if whitelist.contains(domain):
                allowed_domains.append(domain)
    
    for domain in allowed_domains:
        print domain

_CMDS = {
    "add-allowed-domains": _add_allowed_domains,
    "delete-allowed-domains": _delete_allowed_domains,
    "get-allowed-domains": _get_allowed_domains,
}

def run_cmd(args):
    # Get a whitelist object
    whitelist = whitelists.load(args.storage_url)

    if args.cmd in _CMDS:
        _CMDS[args.cmd](args.domains, whitelist)
    else:
        _LOG.warning("Unknown cmd %s.", args.cmd)

# Read options from CLI
parser = argparse.ArgumentParser(description="Run the dns-filter config client")
parser.add_argument('--cmd', nargs='?', type=str, default="get-allowed-domains",
    help="The client command to use")
parser.add_argument('--domains', nargs='+', type=str, default=[], 
    help="The domains to use")
parser.add_argument('--storage-url', nargs='?', type=str,
    default="mongo:localhost:27017:dns_filter", help="A storage service to use",
    dest="storage_url")
args = parser.parse_args()

if __name__ == '__main__':
    _init(args)
    raise SystemExit(run_cmd(args))
