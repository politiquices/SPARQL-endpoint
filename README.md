### Build an Entity Knowledge Base

Build the SPARQL endpoint containing two graphs: wikidata pages of personalities that 
are on politiquices.pt and the politiquices graph with the relationships between these entities
and links to Arquivo.PT news articles supporting these relationships.

Get the entities:
```
    python3 -m venv <something>
    source <something>/bin/activate
    pip install requirements.txt
    make wikidata 
```

This will:

  - download the .TTL files for a few selected political personalities
  - concatenate all the TTL into one big compressed file ttl.bz2 file

Start the SPARQL instance:
```
    make sparql
```

This will start a container running fuseki-docker, mapping port 3030 on the host to port 3030 on 
the container, exposing a SPARQL endpoint. 
