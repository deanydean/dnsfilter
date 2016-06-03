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
import datetime
import logging
import storage
import whitelists

"""
Module containing the filters implementations for the dnsfilter.
"""

_LOG = logging.getLogger("dnsfilter.filters")

class Filter(object):
    """
    Base filter interface.

    A filter is an object that consumes a query, filters it, and produces
    another query.
    """

    def do_filter(self, query):
         pass

class FilterChain(Filter):
    """
    An ordered collections of filters.
    """

    def __init__(self, filters):
        self.filters = filters

    def do_filter(self, query):
        filtering_query = query
        for filter in self.filters:
            filtering_query = filter.do_filter(query)

            if not filtering_query:
                _LOG.debug("Filter chain broken. Filter %s rejected %s",
                    filter, query)
                return None
        return filtering_query

class DeviceACLFilter(FilterChain):
    """
    A filter that allows only named hosts to be filter, all other devices 
    are allowed without filtering
    """

    def __init__(self, filters, store_url):
        FilterChain.__init__(self, filters)
        self.store = storage.create_store(store_url,
            storage.KNOWN_DEVICES_STORE)

    def _add_new_device(self, addr):
        device_info = { 
            "device_addr": addr,
            "is_filtered": False,
            "date_added": datetime.datetime.utcnow(),
            "added_by": "dnsfilter_auto"
        }
        self.store.create(addr, device_info)
        return device_info

    def do_filter(self, query):
        filtering_query = query

        device_addr = query.device_addr
        device_info = self.store.read(device_addr)

        if not device_info:
            device_info = self._add_new_device(device_addr)

        if device_info["is_filtered"]:
            _LOG.debug("Filtering query from %s", device_info)
            return FilterChain.do_filter(self, query)
        else:
            _LOG.debug("Allowing query from %s", device_info)
            return filtering_query

class WhitelistedSiteFilter(object):
    """
    A filter that only allows whitelisted sites to be queried.
    """

    def __init__(self, storage_url):
        self.storage_url = storage_url
        self.whitelist = whitelists.load(storage_url)

    def _isSiteWhitelisted(self, query):
        """
        Check if the site in the query is whitelisted
        """
        segments = query.name.name.count('.')
        for i in range(0, segments):
            site = query.name.name.split('.', i)[-1]
            if self.whitelist.contains(site):
                return True

        return False

    def do_filter(self, query):
        """
        Only allow the query if it is for a whitelisted site
        """
        if self._isSiteWhitelisted(query):
            # Query is whitelisted and therefor allowed 
            return query
        else:
            _LOG.debug("Rejected host %s. Not in whitelist", query.name)
            return None

    def __str__(self):
        return "WhitelistedSiteFilter[whitelist="+str(self.whitelist)+"]"

class FileLoggerFilter(object):
    """
    A filter that will record all hostnames it receives to a file.

    This is useful when trying to work out which hosts are needed for a
    site.
    """

    def __init__(self, record_file):
        self.record_file = open(record_file, "write")

    def do_filter(self, query):
        _LOG.debug("Logging query for %s", query)
        self.record_file.write("["+str(datetime.datetime.today())+"] ")
        self.record_file.write(str(query))
        self.record_file.write("\n")
        self.record_file.flush()
        return query
