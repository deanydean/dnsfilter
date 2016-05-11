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
RUN_ARGS = --debug

.PHONY = all start stop

all: start

start: startserver startweb

# Start the dnsfilter server
startserver:
	@echo -n "Starting dnsfilter server... "
	@SERVER_ARGS="--quiet"; \
	[ -z "$(SERVER_ADDR)" ] || SERVER_ARGS+=" --addr $(SERVER_ADDR)"; \
	[ -z "$(SERVER_PORT)" ] || SERVER_ARGS+=" --port $(SERVER_PORT)"; \
	python dnsfilter/server.py $${SERVER_ARGS} & \
	    echo $$! >.dnsfilter.pid
	@echo " [DONE]"

# Start web
startweb:
	@echo -n "Starting webservices... "
	@WEB_ARGS="--quiet"; \
	[ -z "$(WEB_ADDR)" ] || WEB_ARGS+=" --addr $(WEB_ADDR)"; \
	[ -z "$(WEB_PORT)" ] || WEB_ARGS+=" --port $(WEB_PORT)"; \
	python dnsfilter/web.py $${WEB_ARGS} & \
	    echo $$! >.web.pid
	@echo " [DONE]"

# Run the server
runserver:
	python dnsfilter/server.py $(RUN_ARGS)

# Run the web
runweb:
	python dnsfilter/web.py $(RUN_ARGS)

# Make a docker image
dockerimage:
	docker build .

# Stop any running services
stop:
	@for proc in web dnsfilter; do \
	    if [ -f .$${proc}.pid ]; then \
	    	echo -n "Stopping $${proc}... "; \
	        kill $$(cat .$${proc}.pid); \
		rm -f .$${proc}.pid; \
		echo "[DONE]"; \
	    fi; \
	 done

# Clean the python runtime artifacts
clean: stop
	@for mod in client filters resolvers server web whitelists; do \
	    if [ -f dnsfilter/$${mod}.pyc ]; then \
	    	echo -n "Removing $${mod}.pyc... "; \
	        rm -f dnsfilter/$${mod}.pyc; \
		echo "[DONE]"; \
	    fi; \
	 done
