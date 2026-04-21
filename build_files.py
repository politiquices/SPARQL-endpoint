import json
from os import walk

from rdflib import Graph, Namespace
from rdflib.namespace import RDFS, SKOS

WD = Namespace("http://www.wikidata.org/entity/")
WDT = Namespace("http://www.wikidata.org/prop/direct/")

LANG_PRIORITY = {"pt": 0, "pt-br": 1, "en": 2, "mul": 3}


def parse_entity(filepath, wiki_id):
    g = Graph()
    g.parse(filepath, format="turtle")

    entity = WD[wiki_id]

    if (entity, WDT.P31, WD.Q5) not in g:
        return None

    best_label = None
    best_priority = 99
    fallback_label = None
    for label in g.objects(entity, RDFS.label):
        priority = LANG_PRIORITY.get(label.language, 99)
        if priority < best_priority:
            best_priority = priority
            best_label = str(label)
        if fallback_label is None:
            fallback_label = str(label)

    if best_label is None:
        if fallback_label is None:
            return None
        best_label = fallback_label

    aliases = list({
        str(alt)
        for alt in g.objects(entity, SKOS.altLabel)
        if alt.language in ("pt", "pt-br")
    })

    return {"wiki_id": str(entity), "label": best_label, "aliases": aliases}


def main():
    filenames = []
    for _, _, f_names in walk("wiki_ttl"):
        filenames.extend(f_names)

    all_docs = []
    total = len(filenames)
    for idx, fname in enumerate(sorted(filenames), 1):
        wiki_id = fname.split(".")[0]
        filepath = f"wiki_ttl/{fname}"
        print(f"[{idx}/{total}] Parsing {filepath}")
        doc = parse_entity(filepath, wiki_id)
        if doc:
            all_docs.append(doc)

    all_docs.sort(key=lambda d: d["label"])

    with open("entities_kb.jsonl", "wt", encoding="UTF8") as kb_index:
        for d in all_docs:
            kb_index.write(json.dumps(d) + "\n")

    print(f"\nWrote {len(all_docs)} entities to entities_kb.jsonl")


if __name__ == "__main__":
    main()
