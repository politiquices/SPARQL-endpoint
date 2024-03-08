## Build an Entity Knowledge Base

Build a SPARQL endpoint containing two graphs: 
- wikidata pages of personalities that  are on `politiquices.pt` 
- politiquices graph with the relationships between these entities linking to Arquivo.PT news articles

Get the entities:

    make wikidata 

or

    python download_entities.py --train-data ../data-releases/politiquices_data_v1.0.jsonl

This will:

  - download the .TTL files for a few selected political personalities
  - concatenate all the TTL into one big compressed file ttl.bz2 file

Start the SPARQL instance:

    make sparql

This will start a container running fuseki-docker, mapping port 3030 on the host to port 3030 on 
the container, exposing a SPARQL endpoint. 
