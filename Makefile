wikidata:
	python3 download_entities.py --train-data ../data-releases/politiquices_data_v2.0.jsonl
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
	docker build -t fuseki-docker fuseki-docker
	docker run -dit --name jena_sparql --net politiquices -p 127.0.0.1:3030:3030 fuseki-docker /init.sh  # --tdb2 # --config=/fuseki/config.ttl

wikifiles:
	cat wiki_ttl/* | bzip2 -vc > fuseki-docker/fuseki-data/wikidata_org_$(shell date +"%Y-%m-%d").ttl.bz2
	cd fuseki-docker/fuseki-data/;ln -sf wikidata_org_$(shell date +"%Y-%m-%d").ttl.bz2 wikidata_org.ttl.bz2;cd ../..
