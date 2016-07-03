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
import datetime
import filters
import logging
import storage
import whitelists
import utils

"""
Module containing the client-side utilities for dnsfilter servers.
"""

_LOG = logging.getLogger("dnsfilter.clients")

def _init(args):
    utils.init_logging(None, args.debug, args.quiet, args.logfile)

def _add_trusted_sites(sites, url):
    # Get a whitelist object
    whitelist = whitelists.load(url)

    for site in sites:
        if whitelist.contains(site):
            _LOG.info("Site %s already in whitelist", site)
        else:
            whitelist.add(site)
            _LOG.info("Added site %s", site)

def _delete_trusted_sites(sites, url):
    # Get a whitelist object
    whitelist = whitelists.load(url)

    for site in sites:
        if whitelist.contains(site):
            whitelist.delete(site)
            _LOG.info("Deleted site %s", site)
        else:
            _LOG.info("Site %s is not in whitelist", site)

def _get_trusted_sites(sites, url):
    # Get a whitelist object
    whitelist = whitelists.load(url)

    trusted_sites = []
    
    if not sites:
        trusted_sites = whitelist.get_all()
    else:
        for site in sites:
            if whitelist.contains(site):
                trusted_sites.append(site)
    
    for site in trusted_sites:
        print site

def _add_devices(devices, url):
    store = storage.create_store(url, storage.KNOWN_DEVICES_STORE)

    for device in devices:
        if store.find({"name": device}):
            _LOG.warning("device %s already in filtered devices list", device)
        else:
            device_info = {
                "display_name": device+" (unidentified device)",
                "device_addr": device,
                "date_added": datetime.datetime.utcnow(), 
                "is_filtered": False,
                "added_by": utils.get_current_user()
            }
            store.create(device, device_info)
            _LOG.info("Added %s to filtered devices list", device)

def _delete_devices(devices, url):
    store = storage.create_store(url, storage.KNOWN_DEVICES_STORE)

    for device in devices:
        if store.find({"name": device}):
            store.delete(device)
            _LOG.info("Deleted %s from filtered devices list", device)
        else:
            _LOG.warning("device %s not in filtered devices list", device)

def _get_devices(devices, url):
    store = storage.create_store(url, storage.KNOWN_DEVICES_STORE)

    results = []
    if not devices:
        results = store.find()
    else:
        for device in devices:
            result = store.read(device)
            _LOG.debug("Found device %s : %s", device, result)
            if result:
                results.append(result)

    for result in results:
        print result["name"]+" filtered="+str(result["is_filtered"])

def _set_device_name(args, url):
    device = args[0]
    name = args[1]
    store = storage.create_store(url, storage.KNOWN_DEVICES_STORE)

    result = store.read(device)
    if not result:
        _LOG.warning("Device %s is not found", device)
    else:
        result.set("display_name", name)
        store.update(device, result.properties)

def _show_logs(args, url):
    if args:
        device = args[0]
    else:
        device = None

    store = storage.create_store(url, storage.REQUEST_LOG_STORE)

    if not device:
        results = store.find()
    else:
        results = store.find({ "device": device })

_CMDS = {
    "add-trusted-sites": _add_trusted_sites,
    "delete-trusted-sites": _delete_trusted_sites,
    "get-trusted-sites": _get_trusted_sites,

    "add-devices": _add_devices,
    "delete-devices": _delete_devices,
    "get-devices": _get_devices,
    "set-device-name": _set_device_name,

    "show-logs": _show_logs
}

def run_cmd(args):
    if args.cmd in _CMDS:
        _CMDS[args.cmd](args.args, args.url)
    else:
        _LOG.warning("Unknown cmd %s.", args.cmd)

# Read options from CLI
parser = utils.init_argparser("Run the dns-filter config client",
    is_server=False)
parser.add_argument('--cmd', nargs='?', type=str, default="get-trusted-sites",
    help="The client command to use")
parser.add_argument('--args', nargs='+', type=str, default=[], 
    help="The arguments to pass to command")

args = parser.parse_args()

if __name__ == '__main__':
    _init(args)
    raise SystemExit(run_cmd(args))
