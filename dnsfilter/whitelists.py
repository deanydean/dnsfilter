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
from fnmatch import fnmatch
import logging
import os
import pymongo
import storage

"""
Module containing all whitelist implementations and utils.
"""

_LOG = logging.getLogger("dnsfilter.whitelists") 

def load(url):
    """
    Load a whitelist for the provided url.
    """
    (type, id) = url.split(":", 1)

    if type == "file":
        return FileWhitelist(id)
    if type == "dir":
        return DirWhitelist(id)
    if type == "mongo":
        return MongoWhitelist(id)

    _LOG.warning("Invalid storage url %s", url)
    raise Exception("Invalid storage url : "+url)

def copy(src_url, dst_url):
    """
    Copy the contents of the whitelist from the src_url into the whitelist of 
    the dst_url.
    """
    src_wl = load(src_url)
    dst_wl = load(dst_url)
    copy_lists(src_wl, dst_wl)

def copy_whitelists(src, dst):
    """
    Copy the content of the src whitelist to the dst whitelist.
    """
    for entry in src.get_all():
        dst.add(entry)

class Whitelist(object):
    """
    Base whitelist interface
    """
    
    def contains(self, entry):
        """
        Does the whitelist contain the provided entry.
        """
        pass

    def get_all(self):
        """
        Get all entries in the whitelist.
        """
        pass

    def add(self, entry):
        """
        Add an entry to the whitelist.
        """
        pass

    def delete(self, entry):
        """
        Delete an entry from the whitelist.
        """
        pass


class FileWhitelist(Whitelist):
    """
    A a whitelist of domains from a named file.
    """

    def __init__(self, filename):
        _LOG.debug("Creating FileWhitelist for %s", filename)
        self.domains = []
        
        for line in open(filename):
            line = line.rstrip('\n').strip()
            if not line.startswith("#"):
                _LOG.debug("Adding domain: %s", line)
                self.domains.append(line)

    def contains(self, entry):
        return (entry in self.domains)

    def get_all(self):
        return self.domains

    def add(self, entry):
        self.domains.append(entry)

    def delete(self, entry):
        self.domains.remove(entry)

class DirWhitelist(Whitelist):
    """
    A whitelist of domains from .conf files in a named directory.
    """

    def __init__(self, dirname):
        _LOG.debug("Creating DirWhitelist from directory %s", dirname)
        self.domains = []
        for file in os.listdir(dirname):
            if fnmatch(file, "*.conf"):
                fqFilename = dirname+"/"+file
                _LOG.debug("Loading domains from whitelist file", fqFilename)
                self.domains.extend(FileWhitelist(fqFilename).domains)

    def get_all(self):
        return self.domains

    def contains(self, entry):
        return (entry in self.domains)

    def add(self, entry):
        self.domains.append(entry)

    def delete(self, entry):
        self.domains.remove(entry)

class MongoWhitelist(Whitelist):
    """
    A whitelist of domains provided by mongodb.
    """

    def __init__(self, url):
        _LOG.debug("Creating MongoWhitelist to %s", url)

        params = url.split(":")
        host = params[0]
        port = int(params[1])
        collection = params[2]
        self.store = storage.MongoStore(host, port, collection)

    def _get_domains(self):
        return self.store.read("domains")

    def contains(self, entry):
        return self._get_domains().find_one( { "domain": entry } ) is not None
        
    def add(self, entry):
        self._get_domains().insert( { "domain": entry } )

    def delete(self, entry):
        self._get_domains().remove( { "domain": entry } )

    def get_all(self):
        domains = []
        for domain in self._get_domains().find():
            domains.append(domain["domain"])
        return domains
