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

SHELL = /bin/bash
SERVER_PORT = 10053
WEBSERVICES_PORT = 8080

.PHONY = all start stop

all: start

start: startserver startwebservices

# Start the dnsfilter server
startserver:
	@echo -n "Starting dnsfilter server on port ${SERVER_PORT}... "
	@python dnsfilter/server.py --quiet --port ${SERVER_PORT} & \
	    echo $$! >.dnsfilter.pid
	@echo " [DONE]"

# Start webservices
startwebservices:
	@echo -n "Starting webservices on port ${WEBSERVICES_PORT}... "
	@python dnsfilter/webservices.py --quiet \
	    --port ${WEBSERVICES_PORT} & \
	    echo $$! >.webservices.pid
	@echo " [DONE]"

# Run the server
runserver:
	python dnsfilter/server.py --debug --port $(SERVER_PORT)

# Run the webservices
runwebservices:
	python dnsfilter/webservices.py --debug --port $(WEBSERVICES_PORT)

# Make a docker image
docker image:
	docker build .

# Stop any running services and clean the python runtime artifacts
stop:
	@for proc in webservices dnsfilter; do \
	    if [ -f .$${proc}.pid ]; then \
	    	echo -n "Stopping $${proc}... "; \
	        kill $$(cat .$${proc}.pid); \
		rm .$${proc}.pid; \
		echo "[DONE]"; \
	    fi; \
	 done

# Clean the python runtime artifacts
clean: stop
	@for mod in client filters resolvers server webservices whitelists; do \
	    if [ -f dnsfilter/$${mod}.pyc ]; then \
	    	echo -n "Removing $${mod}.pyc... "; \
	        rm dnsfilter/$${mod}.pyc; \
		echo "[DONE]"; \
	    fi; \
	 done
