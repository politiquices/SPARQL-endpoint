wikidata:
	python3 download_entities.py --train-data ../data-releases/politiquices_data_v2.0.jsonl
	cat wiki_ttl/* | bzip2 -vc > fuseki-docker/fuseki-data/wikidata_org_$(shell date +"%Y-%m-%d").ttl.bz2
	cd fuseki-docker/fuseki-data/;ln -sf wikidata_org_$(shell date +"%Y-%m-%d").ttl.bz2 wikidata_org.ttl.bz2;cd ../..
	python3 build_files.py

sparql:
	docker build -t fuseki-docker fuseki-docker
	docker run -dit --name jena_sparql --net politiquices -p 127.0.0.1:3030:3030 fuseki-docker /init.sh  # --tdb2 # --config=/fuseki/config.ttl

wikifiles:
	cat wiki_ttl/* | bzip2 -vc > fuseki-docker/fuseki-data/wikidata_org_$(shell date +"%Y-%m-%d").ttl.bz2
	cd fuseki-docker/fuseki-data/;ln -sf wikidata_org_$(shell date +"%Y-%m-%d").ttl.bz2 wikidata_org.ttl.bz2;cd ../..
