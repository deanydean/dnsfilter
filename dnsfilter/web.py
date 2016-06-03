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
import json
import logging
import os
import storage
from twisted.internet import reactor
from twisted.web import static, server, resource, http
import utils
import whitelists

"""
Module containing the web interface
"""

_LOG = logging.getLogger("dnsfilter.web")

class WebResource(resource.Resource):

    """
    Base resource type
    """

    def render(self, request):
        _LOG.info("Request received: %s", request)
        
        response = resource.Resource.render(self, request)
        return _get_response(request, response)

class RootWebResource(WebResource):

    """
    The handler for the root resources
    """

    def __init__(self, args):
        WebResource.__init__(self)
        self.putChild("sites", SitesWebservice(args.url))
        self.putChild("devices", DevicesWebservice(args.url))
        self.putChild("admin", static.File(os.getcwd()+"/www/admin"))

    def getChild(self, path, request):
        return WelcomeHandler()

class WelcomeHandler(WebResource):
    
    """
    The handler for the welcome page
    """

    def render_GET(self, request):
        return "WELCOME\n"

class SitesWebservice(WebResource):

    """
    The handler for the sites webservice interface
    """

    def __init__(self, storage_url):
        self.storage_url = storage_url
        WebResource.__init__(self)

    def getChild(self, path, request):
        return SitesWebservice(self.storage_url)

    def render_POST(self, request):
        """
        Add a new site entry
        """
        if request.path == "/sites":
            if "site" not in request.args.keys():
                request.setResponseCode(http.BAD_REQUEST)
                return "BAD REQUEST\n"

            site = request.args["site"][0]
            wl = _get_whitelist(self.storage_url)

            if not wl.contains(site):
                _LOG.info("Adding site %s for request %s", site, request)
                wl.add(site)
            
            request.setHeader("Location", "/sites/"+site)
            return "CREATED\n" 
        else:
            request.setResponseCode(http.NOT_FOUND) 
            return "NOT FOUND\n"

    def render_GET(self, request):
        """
        Read the list of configure sites
        """
        if request.path == "/sites":
            _LOG.debug("Getting sites for %s", request)
            result = []

            for site in _get_whitelist(self.storage_url).get_all():
                result.append(site)

            _LOG.debug("Got sites %s for request %s", result, request)
            return result
        else:
            request.setResponseCode(http.NOT_FOUND)
            return "NOT FOUND\n"

    def render_DELETE(self, request):
        """
        Delete a site entry
        """
        if request.path.startswith("/sites/"):
            site = request.path.replace("/sites/", "")
            wl = _get_whitelist(self.storage_url)
            if wl.contains(site):
                _LOG.info("Deleting site %s for request %s", site, request)
                wl.delete(site)
                return "DELETED\n"
            else:
                request.setResponseCode(http.NOT_FOUND) 
                return "NOT FOUND\n"   
        else:
            request.setResponseCode(http.NOT_FOUND) 
            return "NOT FOUND\n"

    def render_PUT(self, request):
        request.setResponseCode(http.NOT_IMPLEMENTED) 
        return "NOT IMPLEMENTED\n"

class DevicesWebservice(WebResource):
    """
    The handler for the devices webservice interface
    """

    def __init__(self, storage_url):
        self.storage_url = storage_url
        WebResource.__init__(self)

    def getChild(self, path, request):
        return DevicesWebservice(self.storage_url)

    def render_POST(self, request):
        request.setResponseCode(http.NOT_IMPLEMENTED) 
        return "NOT IMPLEMENTED\n"

    def render_GET(self, request):
        """
        Read the list of known devices
        """
        if request.path.startswith("/devices"):
            _LOG.debug("Getting devices for %s", request.path)
            result = []
            store = _get_known_devices_store(self.storage_url)

            path_bits = request.path.split("/")
            _LOG.debug("Path bits is %s", str(path_bits))
            if len(path_bits) == 2:
                # Get all devices
                for device in store.find():
                    result.append(device.name)
            elif len(path_bits) >= 3:
                device = store.read(path_bits[2])
                if not device:
                    return "NOT FOUND\n"
                
                if len(path_bits) == 3:
                    # Get device attribute names
                    result = device.properties.keys()
                elif len(path_bits) == 4 and path_bits[3] in device:
                    # Get device attribute values
                    result = [ device[path_bits[3]] ]
                else:
                    return "NOT FOUND\n"

            _LOG.debug("Got %s for request %s", result, request)
            return result
        else:
            request.setResponseCode(http.NOT_FOUND)
            return "NOT FOUND\n"

    def render_DELETE(self, request):
        request.setResponseCode(http.NOT_IMPLEMENTED) 
        return "NOT IMPLEMENTED\n"

    def render_PUT(self, request):
        request.setResponseCode(http.NOT_IMPLEMENTED) 
        return "NOT IMPLEMENTED\n"


def _get_whitelist(url):
    return whitelists.load(url)

def _get_known_devices_store(url):
    return storage.create_store(url, storage.KNOWN_DEVICES_STORE)

def _get_response_str(data):
    if isinstance(data, basestring) or not hasattr(data, "__iter__"):
        return str(data)
    return '\n'.join((str(i) for i in data))+"\n"

def _get_response(request, data):
    content_type = request.getHeader("Content-Type")

    if content_type == "application/json":
        return json.dumps(data)
    else:
        return _get_response_str(data)

def init(args):
    utils.init_logging(None, args.debug, args.quiet, args.logfile)

def start(args):
    """
    Run the dnsfilter web interface.
    """
    web = RootWebResource(args)

    reactor.listenTCP(args.port, server.Site(web), 80, args.addr)

    _LOG.info("DNS filter web listening on %s:%d...", args.addr, args.port)
    reactor.run()

# Read options from CLI
parser = utils.init_argparser("Start the DNS filter web", { "port": 8080 })
args = parser.parse_args()

if __name__ == '__main__':
    init(args)
    raise SystemExit(start(args))
