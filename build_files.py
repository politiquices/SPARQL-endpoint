import json
import sys
from collections import defaultdict
from os import walk

from SPARQLWrapper import SPARQLWrapper, JSON

from nlp_extraction.utils.utils import just_sleep, write_iterator_to_file

endpoint_url = "https://query.wikidata.org/sparql"


def batch(iterable, n=1):
    lst = len(iterable)
    for ndx in range(0, lst, n):
        yield iterable[ndx:min(ndx + n, lst)]


def get_results(query):
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


def get_names():
    filenames = []
    for _, _, f_names in walk("wiki_ttl_old"):
        filenames.extend(f_names)

    batch_size = 400
    all_results = []

    for ids_batch in batch(filenames, batch_size):
        wiki_ids = ' '.join(['wd:' + f.split(".")[0] for f in ids_batch])
        print(f"Downloading {len(ids_batch)} names")

        query = f"""
            SELECT DISTINCT ?item ?label ?alternative {{
              VALUES ?item {{{wiki_ids}}}
              ?item wdt:P31 wd:Q5.      
              ?item rdfs:label ?label . FILTER(LANG(?label) = "pt")
              OPTIONAL {{
                ?item skos:altLabel ?alternative . FILTER(LANG(?alternative) = "pt") 
              }}
            }}
            ORDER BY ?label
            """

        just_sleep(2, verbose=False)
        results = get_results(query)
        all_results.extend(results["results"]["bindings"])

    return all_results


def main():
    all_results = get_names()
    all_results = sorted(all_results, key=lambda x: x['label']['value'])
    write_iterator_to_file([x['label']['value'] for x in all_results], 'entities_names.txt')

    name = dict()
    alternatives = defaultdict(list)
    for entity in all_results:
        name[entity['item']['value']] = entity['label']['value']
        if 'alternative' in entity:
            alternatives[entity['item']['value']].append(entity['alternative']['value'])

    all_docs = []
    for wiki_id, name in name.items():
        all_docs.append({'wiki_id': wiki_id, 'label': name, 'aliases': alternatives[wiki_id]})

    query_names = open('entities_names.txt', 'wt', encoding="UTF8")
    kb_index = open('entities_kb.txt', 'wt', encoding="UTF8")
    for d in all_docs:
        query_names.write(d['label']+'\n')
        kb_index.write(json.dumps(d)+'\n')
    query_names.close()
    kb_index.close()


if __name__ == '__main__':
    main()
