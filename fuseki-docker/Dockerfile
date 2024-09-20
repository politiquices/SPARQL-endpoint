FROM ubuntu:22.04

RUN apt update -q && \
    apt install -y -q openjdk-17-jre openjdk-17-jdk-headless

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends bash curl ca-certificates findutils coreutils pwgen; \
    rm -rf /var/lib/apt/lists/*

ENV FUSEKI_VERSION=5.1.0
ENV JENA_VERSION=5.1.0
ENV ASF_ARCHIVE=https://archive.apache.org/dist/

# Config and data
VOLUME /fuseki
ENV FUSEKI_BASE /fuseki

# Installation folder
ENV FUSEKI_HOME /jena-fuseki
ENV JENA_HOME /jena

WORKDIR /tmp

RUN curl --fail --silent --show-error --retry-connrefused --retry 3 --output fuseki.tar.gz $ASF_ARCHIVE/jena/binaries/apache-jena-fuseki-$FUSEKI_VERSION.tar.gz && \
     tar zxf fuseki.tar.gz && \
     mv apache-jena-fuseki* $FUSEKI_HOME && \
     rm fuseki.tar.gz* && \
     cd $FUSEKI_HOME && rm -rf fuseki.war && chmod 755 fuseki-server

RUN curl --fail --silent --show-error --retry-connrefused --retry 3 --output jena.tar.gz $ASF_ARCHIVE/jena/binaries/apache-jena-$JENA_VERSION.tar.gz && \
     tar zxf jena.tar.gz && \
     mv apache-jena-* $JENA_HOME && \
     rm jena.tar.gz*

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
