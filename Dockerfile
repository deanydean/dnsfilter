FROM debian:latest

MAINTAINER Deany Dean

ENV DNSFILTER_HOME /opt/dnsfilter
ENV PYTHONPATH $DNSFILTER_HOME

RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
    python-twisted-names python-pymongo
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*

EXPOSE 53

COPY . $DNSFILTER_HOME

CMD python $DNSFILTER_HOME/dnsfilter/server.py --storage-url mongo:mongo:27017:dns_filter
