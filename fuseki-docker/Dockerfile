FROM ubuntu:22.04

RUN apt update -q && \
    apt install -y -q openjdk-17-jre openjdk-17-jdk-headless

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends bash ca-certificates findutils coreutils pwgen; \
    rm -rf /var/lib/apt/lists/*

ENV FUSEKI_VERSION=5.1.0
ENV JENA_VERSION=5.1.0

# Config and data
VOLUME /fuseki
ENV FUSEKI_BASE=/fuseki

# Installation folder
ENV FUSEKI_HOME=/jena-fuseki
ENV JENA_HOME=/jena

WORKDIR /tmp

COPY apache-jena-fuseki-5.1.0.tar.gz fuseki.tar.gz
RUN tar zxf fuseki.tar.gz && \
     mv apache-jena-fuseki* $FUSEKI_HOME && \
     rm fuseki.tar.gz && \
     chmod 755 $FUSEKI_HOME/fuseki-server

COPY apache-jena-5.1.0.tar.gz jena.tar.gz
RUN tar zxf jena.tar.gz && \
     mv apache-jena-* $JENA_HOME && \
     rm jena.tar.gz

# copy a custom 'shiro.ini' allowing connections from anywhere with auth
# this will allow to use the webapp to see any already created datasets
COPY shiro.ini $FUSEKI_BASE/shiro.ini
COPY config.ttl $FUSEKI_BASE/config.ttl
COPY fuseki-data/wikidata_org.ttl.bz2 /usr/share/data/wikidata_org.ttl.bz2
COPY fuseki-data/politiquices.ttl /usr/share/data/politiquices.ttl
COPY init.sh /
RUN chmod 755 /init.sh; chmod +x /init.sh

WORKDIR $FUSEKI_HOME
EXPOSE 3030

ENTRYPOINT ["/bin/bash"]
