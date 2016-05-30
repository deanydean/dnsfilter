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
import filters
import logging
import storage
import whitelists
import utils

"""
    Module containing the client-side utilities for dnsfilter servers.
"""

DEFAULT_STORAGEURL = "mongo:localhost:27017:dnsfilter"

_LOG = logging.getLogger("dnsfilter.clients")

def _init(args):
    utils.init_logging(None, args.debug, False, None)

def _add_allowed_domains(domains, url):
    # Get a whitelist object
    whitelist = whitelists.load(url)


    for domain in domains:
        if whitelist.contains(domain):
            _LOG.info("Domain %s already in whitelist", domain)
        else:
            whitelist.add(domain)
            _LOG.info("Added domain %s", domain)

def _delete_allowed_domains(domains, url):
    # Get a whitelist object
    whitelist = whitelists.load(url)

    for domain in domains:
        if whitelist.contains(domain):
            whitelist.delete(domain)
            _LOG.info("Deleted domain %s", domain)
        else:
            _LOG.info("Domain %s is not in whitelist", domain)

def _get_allowed_domains(domains, url):
    # Get a whitelist object
    whitelist = whitelists.load(url)

    allowed_domains = []
    
    if not domains:
        allowed_domains = whitelist.get_all()
    else:
        for domain in domains:
            if whitelist.contains(domain):
                allowed_domains.append(domain)
    
    for domain in allowed_domains:
        print domain

def _add_filtered_clients(clients, url):
    store = storage.create_store(url, filters.FILTERED_CLIENTS)

    for client in clients:
        if store.find({"client_addr": client}):
            _LOG.warning("Client %s already in filtered clients list", client)
        else:
            store.create(client, { "client_addr": client })
            _LOG.info("Added %s to filtered clients list", client)

def _delete_filtered_clients(clients, url):
    store = storage.create_store(url, filters.FILTERED_CLIENTS)

    for client in client:
        if store.find({"client_addr": client}):
            store.delete(client)
            _LOG.info("Deleted %s from filtered clients list", client)
        else:
            _LOG.warning("Client %s not in filtered clients list", client)

def _get_filtered_clients(clients, url):
    store = storage.create_store(url, filters.FILTERED_CLIENTS)

    filtered_clients = []
    if not clients:
        filtered_clients = store.find()
    else:
        for client in clients:
            filtered_client = store.find({"client_addr": client})
            if filtered_client:
                filtered_clients.append(filtered_client)

    for filtered_client in filtered_clients:
        print filtered_client.get("client_addr")

_CMDS = {
    "add-allowed-domains": _add_allowed_domains,
    "delete-allowed-domains": _delete_allowed_domains,
    "get-allowed-domains": _get_allowed_domains,

    "add-filtered-clients": _add_filtered_clients,
    "delete-filtered-clients": _delete_filtered_clients,
    "get-filtered-clients": _get_filtered_clients
}

def run_cmd(args):
    if args.cmd in _CMDS:
        _CMDS[args.cmd](args.args, args.storage_url)
    else:
        _LOG.warning("Unknown cmd %s.", args.cmd)

# Read options from CLI
parser = argparse.ArgumentParser(description="Run the dns-filter config client")
parser.add_argument('--cmd', nargs='?', type=str, default="get-allowed-domains",
    help="The client command to use")
parser.add_argument('--args', nargs='+', type=str, default=[], 
    help="The arguments to pass to command")
parser.add_argument('--storage-url', nargs='?', type=str,
    default="mongo:localhost:27017:dnsfilter", help="A storage service to use",
    dest="storage_url")
parser.add_argument('--debug', action="store_true", default=False,
    help="Enable debugging mode (verbose logging)")

args = parser.parse_args()

if __name__ == '__main__':
    _init(args)
    raise SystemExit(run_cmd(args))
