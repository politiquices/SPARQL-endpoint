wikidata:
	python3 download_entities.py --train-data ../data-releases/politiquices_data_v3.0_enriched.jsonl
	cat wiki_ttl/* | bzip2 -vc > fuseki-docker/fuseki-data/wikidata_org_$(shell date +"%Y-%m-%d").ttl.bz2
	cd fuseki-docker/fuseki-data/;ln -sf wikidata_org_$(shell date +"%Y-%m-%d").ttl.bz2 wikidata_org.ttl.bz2;cd ../..
	python3 build_files.py

download-jena:
	curl --fail --show-error --retry-connrefused --retry 3 \
		--output fuseki-docker/apache-jena-fuseki-5.1.0.tar.gz \
		https://archive.apache.org/dist/jena/binaries/apache-jena-fuseki-5.1.0.tar.gz
	curl --fail --show-error --retry-connrefused --retry 3 \
		--output fuseki-docker/apache-jena-5.1.0.tar.gz \
		https://archive.apache.org/dist/jena/binaries/apache-jena-5.1.0.tar.gz

sparql:
	docker compose -f fuseki-docker/docker-compose.yml down -v
	docker compose -f fuseki-docker/docker-compose.yml up --build -d

wikifiles:
	cat wiki_ttl/* | bzip2 -vc > fuseki-docker/fuseki-data/wikidata_org_$(shell date +"%Y-%m-%d").ttl.bz2
	cd fuseki-docker/fuseki-data/;ln -sf wikidata_org_$(shell date +"%Y-%m-%d").ttl.bz2 wikidata_org.ttl.bz2;cd ../..
