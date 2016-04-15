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
import os

"""
    Module containing all whitelist implementations.
"""

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
        raise Exception("Not implemented mongo whitelists")

    raise Exception("Invalid storage url : "+url)

class Whitelist(object):
    """
        Base whitelist interface
    """
    
    def contains(self, entry):
        """
            Does the whitelist contain the provided entry.
        """
        pass

class FileWhitelist(Whitelist):
    """
        Generate a whitelist of domains from a named file.
    """

    def __init__(self, filename):
        self.domains = []
        
        for line in open(filename):
            line = line.rstrip('\n').strip()
            if not line.startswith("#"):
                print " - Adding domain", line
                self.domains.append(line)

    def contains(self, entry):
        return (entry in self.domains)

class DirWhitelist(Whitelist):
    """
        Generate a whitelist of domains from .conf files in a named directory.
    """

    def __init__(self, dirname):
        self.domains = []
        for file in os.listdir(dirname):
            if fnmatch(file, "*.conf"):
                fqFilename = dirname+"/"+file
                print " - Loading domains from whitelist file", fqFilename
                self.domains.extend(FileWhitelist(fqFilename).domains)

    def contains(self, entry):
        return (entry in self.domains)
