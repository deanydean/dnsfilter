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
import logging
import pymongo

"""
    Module containing the storage components for dnsfilter.
"""

_LOG = logging.getLogger("dnsfilter.storage") 

class Store(object):
    """
    Interface representing a generic storage container
    """

    def create(self, name, value):
        """
        Create a named object with the provided value
        """
        pass

    def read(self, name):
        """
        Read the value of a named object
        """
        pass

    def update(self, name, value):
        """
        Update the named object with the provide value
        """
        pass

    def delete(self, name):
        """
        Delete the named object
        """
        pass

class MongoStore(Store):
    """
    A store implamentation backed by Mongo DB
    """

    def __init__(self, host, port, collection):
        self.host = host
        self.port = port
        self.collection = collection
        self._connect()  

    def _connect(self):
        _LOG.debug("Connecting to mongodb %s:%d", self.host, self.port)
        self.client = pymongo.MongoClient(self.host, self.port)

    def create(self, name, value):
        self.client[self.collection][name].insert(value)

    def read(self, name):
        return self.client[self.collection][name]

