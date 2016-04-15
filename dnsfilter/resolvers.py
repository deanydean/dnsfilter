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
from twisted.internet import defer
from twisted.names import error
import whitelists

"""
    Module containing the resolvers for the dnsfilter.
"""

class AllowedDomainResolver(object):
    """
    A resolver which allows lookups only for whitelisted domains
    """

    def __init__(self, resolver, url):
        self.resolver = resolver
        self.whitelist = whitelists.load(url)

    def _isDomainWhitelisted(self, query):
        """
        Check if the domain in the query is whitelisted
        """
        segments = query.name.name.count('.')
        for i in range(0, segments):
            domain = query.name.name.split('.', i)[-1]
            if self.whitelist.contains(domain):
                return True

        return False

    def query(self, query, timeout=None):
        """
        Only allow the query if it is for a whitelisted domain. Fail 
        everything else
        """
        if self._isDomainWhitelisted(query):
            return self.resolver.query(query, timeout)
        else:
            print "Will not resolve domain", query.name
            return defer.fail(error.DomainError())
