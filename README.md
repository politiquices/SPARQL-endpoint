## Build an Entity Knowledge Base

This repo is responsible to build a SPARQL endpoint. 

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
