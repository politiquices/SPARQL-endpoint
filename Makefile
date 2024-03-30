wikidata:
	python download_entities.py --train-data politiquices_data_v2.0.jsonl
	cat wiki_ttl/* | bzip2 -vc > fuseki-docker/fuseki-data/wikidata_org_$(shell date +"%Y-%m-%d").ttl.bz2
	cd fuseki-docker/fuseki-data/;ln -sf wikidata_org_$(shell date +"%Y-%m-%d").ttl.bz2 wikidata_org.ttl.bz2;cd ../..
	python build_files.py

sparql:
	# ToDo: --platform linux/arm64
	docker build -t fuseki-docker fuseki-docker
	docker run -dit --name jena_sparql --net politiquices -p 127.0.0.1:3030:3030 fuseki-docker /init.sh  # --tdb2 # --config=/fuseki/config.ttl

wikifiles:
	cat wiki_ttl/* | bzip2 -vc > fuseki-docker/fuseki-data/wikidata_org_$(shell date +"%Y-%m-%d").ttl.bz2
	cd fuseki-docker/fuseki-data/;ln -sf wikidata_org_$(shell date +"%Y-%m-%d").ttl.bz2 wikidata_org.ttl.bz2;cd ../..
