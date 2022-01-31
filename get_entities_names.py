import sys
from collections import defaultdict
from os import walk

from SPARQLWrapper import SPARQLWrapper, JSON

from nlp_extraction.utils.utils import just_sleep, write_iterator_to_file

endpoint_url = "https://query.wikidata.org/sparql"

def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]


def get_results(endpoint_url, query):
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    # TODO adjust user agent; see https://w.wiki/CX6
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


def get_names():
    filenames = []
    for _, _, f_names in walk("wiki_ttl"):
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
        results = get_results(endpoint_url, query)
        all_results.extend(results["results"]["bindings"])

    return all_results


def main():
    all_results = get_names()
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

    for d in all_docs:
        print(d)

if __name__ == '__main__':
    main()
