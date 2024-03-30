## Build an Entity Knowledge Base

This repo is responsible to build a SPARQL endpoint containing two graphs: 
- wikidata pages of personalities that  are on `politiquices.pt` 
- politiquices graph with the relationships between these entities linking to Arquivo.PT news articles


### Get the data
- Download the .TTL files for each political personality based on SPARQL queries and defined in `entities_config.json` file. 
- Concatenate all the TTL files into one big compressed file `ttl.bz2` file to be used in the SPARQL endpoint.
- Generates the `entities_kb.txt` and `entities_names.txt`
- NOTE: it reads this file in this location `../data-releases/politiquices_data_v2.0.jsonl`


     make wikidata


### Start the SPARQL endpoint

This will start the Jena Fuseki server with the politiquices graph and the wikidata graph. It will index all the .TTL files in the `fuseki-docker/fuseki-data` folder.
The server will be available at `http://localhost:3030/`. 

    make sparql

This will start a container running fuseki-docker, mapping port 3030 on the host to port 3030 on the container, exposing a SPARQL endpoint.



### Build TTL files

This will concatenate all the TTL files into one big compressed file `ttl.bz2` file to be used in the SPARQL endpoint.

    make wikifiles