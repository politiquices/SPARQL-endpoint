import json
from time import sleep
from collections import defaultdict
from os import walk
from random import randint

import sys
from SPARQLWrapper import SPARQLWrapper, JSON

endpoint_url = "https://query.wikidata.org/sparql"



def just_sleep(upper_bound=3, verbose=False):
    sec = randint(1, upper_bound)
    if verbose:
        print(f"sleeping for {sec} seconds")
    sleep(sec)


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


LANG_PRIORITY = {"pt": 0, "pt-br": 1, "en": 2}


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
              ?item rdfs:label ?label .
              FILTER(LANG(?label) = "pt" || LANG(?label) = "pt-br" || LANG(?label) = "en")
              OPTIONAL {{
                ?item skos:altLabel ?alternative .
                FILTER(LANG(?alternative) = "pt" || LANG(?alternative) = "pt-br")
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

    # For each entity keep the highest-priority label: pt > pt-br > en
    best_label: dict = {}
    alternatives = defaultdict(list)
    for entity in all_results:
        wiki_id = entity['item']['value']
        label = entity['label']['value']
        lang = entity['label'].get('xml:lang', '')
        priority = LANG_PRIORITY.get(lang, 99)
        if wiki_id not in best_label or priority < best_label[wiki_id][1]:
            best_label[wiki_id] = (label, priority)
        if 'alternative' in entity:
            alt = entity['alternative']['value']
            if alt not in alternatives[wiki_id]:
                alternatives[wiki_id].append(alt)

    all_docs = sorted(
        [{'wiki_id': wid, 'label': lbl, 'aliases': alternatives[wid]} for wid, (lbl, _) in best_label.items()],
        key=lambda d: d['label'],
    )

    with open('entities_kb.jsonl', 'wt', encoding="UTF8") as kb_index:
        for d in all_docs:
            kb_index.write(json.dumps(d)+'\n')


if __name__ == '__main__':
    main()
