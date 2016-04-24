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
from twisted.internet import defer
from twisted.names import error

"""
    Module containing the resolvers for the dnsfilter.
"""

_LOG = logging.getLogger("dnsfilter.resolvers")

class FilterResolver(object):
    """
    A resolver that filters requests based on a filter object
    """

    def __init__(self, sub_resolver, filter):
        self.sub_resolver = sub_resolver
        self.filter = filter

    def query(self, query, timeout=None):
        """
        Run the query through this object's filter
        """
        filtered_query = self.filter.do_filter(query)

        if filtered_query:
            return self.sub_resolver.query(query, timeout)
        else:
            _LOG.warning("Query for %s rejected by filter %s", query,
                self.filter)
            return defer.fail(error.DomainError())
