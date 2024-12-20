import json
import os
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from time import sleep
from random import randint
from typing import List

import requests
import sys
from SPARQLWrapper import SPARQLWrapper, JSON


def just_sleep(upper_bound=3, verbose=False):
    sec = randint(1, upper_bound)
    if verbose:
        print(f"sleeping for {sec} seconds")
    sleep(sec)


def read_ground_truth(filename, skip_classes: List[str] = None):
    if skip_classes is None:
        skip_classes = []
    with open(filename, encoding="UTF8") as f_in:
        data = [json.loads(line) for idx, line in enumerate(f_in)]
    data = [entry for entry in data if entry["label"] not in skip_classes]
    print("Considering only the classes:", sorted(set([entry["label"] for entry in data])))
    return data


# persons that are/were affiliated with a recent/relevant portuguese political party
affiliated_with_relevant_political_party = """
    SELECT DISTINCT ?person ?personLabel
        WHERE {
          { VALUES ?relevant_parties 
                { wd:Q59325416 wd:Q884840 wd:Q1054298 wd:Q63645885 wd:Q46122950 wd:Q19694667 
                   wd:Q16947563 wd:Q6516904 wd:Q5899673 wd:Q605026 wd:Q20895387 wd:Q5154439 
                   wd:Q2054628 wd:Q10345627 wd:Q1819658 wd:Q6540639 wd:Q2054681 wd:Q1332539 
                   wd:Q1851550 wd:Q595575 wd:Q847263 wd:Q2054807 wd:Q3293542 wd:Q7232654 
                   wd:Q20901233 wd:Q10345705 wd:Q2054840 wd:Q1352945 wd:Q2105350 wd:Q18166125 
                   wd:Q65164025 wd:Q769829 wd:Q46122950
                }
             ?person wdt:P102 ?relevant_parties . 
             ?person rdfs:label ?personLabel }
        FILTER(LANG(?personLabel) = "pt")
    } ORDER BY ?personLabel
    """

# famous portuguese persons, such as: judges, economists, lawyers, civil servants, politicians,
# businessperson, bankers, etc.; born after 1935
portuguese_persons_occupations = """
    SELECT DISTINCT ?person ?personLabel ?date_of_birth
    WHERE {
      ?person wdt:P27 wd:Q45.
      { VALUES ?occupations { wd:Q16533 wd:Q188094 wd:Q40348 wd:Q212238  
                              wd:Q82955 wd:Q43845 wd:Q806798 }} .
      ?person wdt:P106 ?occupations .
      ?person wdt:P569 ?date_of_birth .
      ?person rdfs:label ?personLabel.
      FILTER(?date_of_birth >= "1935-01-01T00:00:00"^^xsd:dateTime )
      FILTER(LANG(?personLabel) = "pt")
    } 
    ORDER BY ?personLabel
    """

# all portuguese political parties
portuguese_political_parties = """
    SELECT DISTINCT ?wiki_id ?partyLabel ?logo ?inception ?disbanded
    WHERE {
      ?wiki_id wdt:P31 wd:Q7278;
             wdt:P17 wd:Q45.
      OPTIONAL {
        ?wiki_id wdt:P154 ?logo.
      }
      OPTIONAL {
        ?wiki_id wdt:P576 ?disbanded.
        ?wiki_id wdt:P571 ?inception.
      }
      SERVICE wikibase:label { bd:serviceParam wikibase:language "pt". }
    } ORDER BY ?partyLabel
    """

# portuguese banks or banks with headquarters in Lisbon
portuguese_banks = """
    SELECT DISTINCT ?wiki_id ?bankLabel WHERE {
      { 
        VALUES ?bank_related_instances {wd:Q837171 wd:Q806718}
        ?wiki_id wdt:P452 ?bank_related_instances;
          rdfs:label ?bankLabel.
        ?wiki_id wdt:P17 wd:Q45.
      }
      UNION {
         ?wiki_id wdt:P452 wd:Q806718;
          rdfs:label ?bankLabel.
        ?wiki_id wdt:P159 wd:Q597
      }
      UNION {
         ?wiki_id wdt:P31 wd:Q848507;
          rdfs:label ?bankLabel.
        ?wiki_id wdt:P159 wd:Q597
      }

      FILTER((LANG(?bankLabel)) = "pt")
    }
    ORDER BY (?bankLabel)
    """

# all_portuguese_municipalities
portuguese_municipalities = """
    SELECT DISTINCT ?locality ?localityLabel WHERE {
        ?locality wdt:P31 wd:Q13217644;
           rdfs:label ?localityLabel.
      FILTER((LANG(?localityLabel)) = "pt")
    }
    ORDER BY (?localityLabel)
    """

# all public portuguese enterprises
portuguese_public_enterprises = """
    SELECT DISTINCT ?wiki_id ?enterpriseLabel ?x WHERE {
        ?wiki_id wdt:P31 wd:Q270791;
          rdfs:label ?enterpriseLabel.
        ?wiki_id wdt:P17 wd:Q45;
      FILTER((LANG(?enterpriseLabel)) = "pt")
    }
    ORDER BY (?enterpriseLabel)
    """

# get a list of all possible public office positions hold by someone portuguese
public_office_positions = """
    SELECT DISTINCT ?personLabel ?person ?positionLabel ?position WHERE {
        ?person wdt:P27 wd:Q45 .
        ?person rdfs:label ?personLabel .
        ?person wdt:P39 ?position.
        ?position rdfs:label ?positionLabel.
      FILTER((LANG(?personLabel)) = "pt")
      FILTER((LANG(?positionLabel)) = "pt")
    }
    ORDER BY (?personLabel)
    LIMIT 100
    """


def get_parties(personalities, batch_size=200):
    """get all political parties associated to every personality"""

    parties_id = []
    persons = ['wd:' + str(x) for x in personalities]
    for x in range(0, len(persons), batch_size):
        per_query = ' '.join(persons[x:x+batch_size])
        political_parties = f"""
            SELECT DISTINCT ?wiki_id  
                WHERE {{
                    VALUES ?person {{{per_query}}} 
                    OPTIONAL {{
                        ?person p:P102 ?political_partyStmnt.
                        ?political_partyStmnt ps:P102 ?wiki_id.
                    }}
                }}
            """
        results = query_wikidata(political_parties)
        parties_id.extend([party['wiki_id']['value'].split("/")[-1] for party in results['results']['bindings']
                           if 'wiki_id' in party])
    return set(parties_id)


def get_relevant_persons_based_on_public_office_positions():
    """
    Read the all the wikidata portuguese public offices objects from: `public_office_positions.json`
    and extract all the persons connected to it through the following property:

        wdt:P39 position held
        subject currently or formerly holds the object position or public office

        filter to return only those born after 1935
    """

    wiki_ids = []
    with open("entities_config.json") as f_in:
        data = json.load(f_in)
        for k, v in data['positions'].items():
            for wiki_id, description in v.items():
                wiki_ids.append("wd:" + wiki_id)

    query = f"""
    SELECT DISTINCT ?person ?personLabel
    WHERE {{
      VALUES ?positions {{ {' '.join(wiki_ids)} }}
      ?person wdt:P39 ?positions.
      ?person rdfs:label ?personLabel .
      ?person wdt:P569 ?date_of_birth .
      FILTER(LANG(?personLabel) = "pt")
      FILTER(?date_of_birth >= "1935-01-01T00:00:00"^^xsd:dateTime )
    }} ORDER BY ?personLabel
    """

    return query


def query_wikidata(sparql_query):
    endpoint_url = "https://query.wikidata.org/sparql"
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(sparql_query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


def read_extra_entities(f_name):
    with open(f_name) as f_in:
        data = json.load(f_in)
        remove = [url.split("/")[-1] for url in data['persons']['remove']]
        add = [url.split("/")[-1] for url in data['persons']['add']]
    return add, remove


def get_wiki_ids_from_annotations(f_name):
    training_data = read_ground_truth(f_name)
    annotated_wiki_ids = set()
    for entry in training_data:
        p1_id = entry["ent1_id"]
        p2_id = entry["ent2_id"]
        if p1_id == 'None' or p2_id == 'None':
            continue
        annotated_wiki_ids.add(p1_id.split("/")[-1])
        annotated_wiki_ids.add(p2_id.split("/")[-1])
    print(f"{len(list(annotated_wiki_ids))} entities from annotations")
    return list(annotated_wiki_ids)


def gather_wiki_ids(queries, to_add=None, to_remove=None):

    relevant_ids = []

    for query in queries:
        results = query_wikidata(query)
        just_sleep(3)
        wiki_ids = [r["person"]["value"].split("/")[-1] for r in results["results"]["bindings"]]
        relevant_ids.extend(wiki_ids)

    print(f"{len(set(relevant_ids))} entities gathered from SPARQL queries")

    if to_add:
        print(f"{len(to_add)} manually selected entities to be added")
        relevant_ids.extend(to_add)

    if to_remove:
        print(f"{len(to_remove)} manually selected entities to be removed")
        for el in to_remove:
            if el in relevant_ids:
                relevant_ids.remove(el)

    return list(set(relevant_ids))


def download(ids_to_retrieve, overwrite, lang="pt"):
    """
    Downloads the TTL from wikidata.org for each entity in a given list entities using a
    special endpoint, e.g.:

    https://www.wikidata.org/wiki/Special:EntityData?id=Q610788&format=ttl
    """
    base_url = "https://www.wikidata.org/wiki/Special:EntityData?"
    default_dir = "wiki_ttl"
    print(f"\nDownloading {len(ids_to_retrieve)} unique entities")
    if not os.path.exists(default_dir):
        os.makedirs(default_dir)
    for idx, wiki_id in enumerate(sorted(ids_to_retrieve)):
        f_name = os.path.join(default_dir, wiki_id + ".ttl")
        if os.path.exists(f_name) and not overwrite:
            print(f"skipped {f_name}")
            continue
        print(f"Downloading {f_name} - {str(idx)}/ {str(len(set(ids_to_retrieve)))}")
        just_sleep(2)
        r = requests.get(base_url, params={"format": 'ttl', "id": wiki_id, "uselang": lang})
        open(f_name, "wt").write(r.text)


def create_args():
    parser = ArgumentParser(
        description=__doc__,
        formatter_class=RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--train-data",
        help="Path to directory with training data",
        type=str,
        required=False,
    )

    parser.add_argument(
        "--overwrite",
        help="Overwrite existing TTL files",
        action="store_true",
        required=False,
    )

    return parser


def main():
    parser = create_args()
    args = parser.parse_args()

    # print the arguments values
    print(f"train_data: {args.train_data}")
    if args.overwrite:
        print("Overwriting existing TTL files")
        overwrite = True
    else:
        print("Not overwriting existing TTL files")
        overwrite = False

    # get entities from wikidata.org through SPARQL queries
    print("Selecting entities from wikidata.org")
    queries = [
        affiliated_with_relevant_political_party,
        get_relevant_persons_based_on_public_office_positions(),
        portuguese_persons_occupations,
    ]

    # get wiki entities ids from a manual curated list
    add, remove = read_extra_entities('entities_config.json')

    # get all the unique entities wiki ids: queries + manual list
    entities_ids = gather_wiki_ids(queries, to_add=add, to_remove=remove)

    # get all unique parties
    parties_ids = get_parties(entities_ids)

    # add also the entities' wiki id from annotations data
    if args.train_data:
        print("Selecting entities from the training data")
        entities_ids.extend(get_wiki_ids_from_annotations(args.train_data))

    # download the TTL for each entity
    download(list(set(entities_ids).union(parties_ids)), overwrite)


if __name__ == "__main__":
    main()
