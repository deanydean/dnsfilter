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
import copy
import logging
import pymongo

"""
Module containing storage components.
"""

_LOG = logging.getLogger("dnsfilter.storage") 

KNOWN_DEVICES_STORE = "known_devices"
TRUSTED_SITES_STORE = "trusted_sites"
REQUEST_LOG_STORE = "request_log"

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

    def find(self, query):
        """
        Find objects in the store.
        """
        pass

def create_store(url, name):
    """
    Create a new store object for the provided URL
    """
    (type, uri) = url.split(":", 1)

    if type == "mongo":
        return MongoStore(uri, name)

    _LOG.warning("Unknown storage type '%s'", type)
    raise Exception("Invalid storage url : "+url)
 

class StoreObject(object):
    
    def __init__(self, name, properties={}):
        self._id = properties["_id"]
        self.name = name
        self.properties = copy.deepcopy(properties)
        self.properties.pop("_id")

    def __iter__(self):
        return self.properties.__iter__()

    def __getitem__(self, i):
        return self.properties.__getitem__(i)

    def get(self, prop):
        if prop in self.properties:
            return self.properties[prop]
        else:
            return None

    def set(self, prop, value):
        self.properties[prop] = value

_MONGO_CLIENTS = { }

class MongoStore(Store):
    """
    A store implementation backed by Mongo DB
    """

    def __init__(self, url, collection_name):
        (host, port, db_name) = url.split(":") 
        self.host = host
        self.port = int(port)
        self.db_name = db_name
        self.collection_name = collection_name
        self._connect()
        _LOG.debug("Connected, using db=%s collection=%s", self.db_name,
            self.collection_name)

    def _connect(self):
        key = (self.host, self.port)
        if key not in _MONGO_CLIENTS:
            _LOG.debug("Connecting to mongodb %s:%d", self.host, self.port)
            _MONGO_CLIENTS[key] = pymongo.MongoClient(self.host, self.port)

        self.client = _MONGO_CLIENTS[key]
        self.collection = self.client[self.db_name][self.collection_name]

    def _mongo_to_store(self, obj):
        if not obj:
            return None

        if "name" in obj:
            name = obj["name"]
        else:
            name = obj["_id"]
           
        return StoreObject(name, obj)

    def create(self, name, value):
        value["name"] = name
        self.collection.insert(value)

    def read(self, name):
        doc = self.collection.find_one({ "name": name })

        _LOG.debug("Read %s : %s", name, str(doc))
        return self._mongo_to_store(doc)

    def update(self, name, value):
        doc = self.collection.find_one({ "name": name })
        if not doc:
            _LOG.warning("Failed to update missing object %s", name)

        _LOG.debug("Update %s : %s", doc, value)

        self.collection.update(
            { '_id': doc["_id"] },
            { '$set': value } 
        ) 
        
    def delete(self, name):
        self.collection.remove({"name": name})

    def find(self, query={}):
        result = []
        for doc in self.collection.find(query):
            _LOG.debug("Found doc %s", doc)
            result.append(self._mongo_to_store(doc))
       
        _LOG.debug("Found %d results for %s", len(result), str(query))
        return result
