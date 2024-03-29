### List the personalities in the graph

    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX  wd: <http://www.wikidata.org/entity/>

    SELECT ?x WHERE {
        ?x wdt:P31 wd:Q5
    }



### List articles in the graph

    PREFIX politiquices: <http://www.politiquices.pt/>
    PREFIX ns1: <http://purl.org/dc/elements/1.1/>
    
    SELECT ?date ?title ?article WHERE {
        ?x politiquices:url ?article .
        ?article ns1:title ?title;
                 ns1:date ?date.
    }
    LIMIT 1000



### The total number of articles

    PREFIX politiquices: <http://www.politiquices.pt/>
    
    SELECT (COUNT(?x) as ?n_artigos) WHERE {
        ?x politiquices:url ?y .
    }



### The total number of news articles grouped by year 

    PREFIX        dc: <http://purl.org/dc/elements/1.1/>
    
    SELECT ?year (COUNT(?x) as ?n_artigos) WHERE {
      ?x dc:date ?date .
    }
    GROUP BY (YEAR(?date) AS ?year)
    ORDER BY ?year



### List for each personality the total number of articles where he/she occurs

    PREFIX           wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX            wd: <http://www.wikidata.org/entity/>
    PREFIX  politiquices: <http://www.politiquices.pt/>
    PREFIX          rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
    SELECT ?person ?name (COUNT(*) as ?count)
    WHERE {
      VALUES ?rel_values {'ent1_opposes_ent2' 'ent2_opposes_ent1' 
                          'ent1_supports_ent2' 'ent2_supports_ent1'}
      ?person rdfs:label ?name .
      ?person wdt:P31 wd:Q5 ;
              {?rel politiquices:ent1 ?person} UNION {?rel politiquices:ent2 ?person} .
      ?rel politiquices:type ?rel_values .
    }
    GROUP BY ?person
    ORDER BY DESC (?count)



### The personalities in the graph, and the names from Wikidata     

    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT DISTINCT ?person ?personLabel {
      ?person wdt:P31 wd:Q5 .
      SERVICE <http://0.0.0.0:3030/wikidata/query> {
        ?person wdt:P102 wd:Q847263.
        ?person rdfs:label ?personLabel
        FILTER(LANG(?personLabel) = "pt")
      }
    }



### Top personalities that oppose someone
    
    PREFIX politiquices: <http://www.politiquices.pt/>
    
    SELECT DISTINCT ?person_a (COUNT(?url) as ?nr_articles) {
      { ?rel politiquices:ent1 ?person_a .
        ?rel politiquices:type 'ent1_opposes_ent2'.
      }  
      UNION 
      { ?rel politiquices:ent2 ?person_a .
        ?rel politiquices:type 'ent2_opposes_ent1'.
      }
      ?rel politiquices:url ?url .
    }
    GROUP BY ?person_a
    ORDER BY DESC(?nr_articles)



### Get articles where someone supports José Sócrates  
    
    PREFIX politiquices: <http://www.politiquices.pt/>
    PREFIX dc: <http://purl.org/dc/elements/1.1/>
    
    SELECT DISTINCT ?url ?title ?ent1 ?ent1_name ?score 
    WHERE {
      ?rel politiquices:type "ent1_supports_ent2" .
      ?rel politiquices:score ?score .
      ?rel politiquices:type ?rel_type .
      ?rel politiquices:ent1 ?ent1 .
      ?rel politiquices:ent1_str ?ent1_name .
      ?rel politiquices:ent2 wd:Q182367 .
      ?rel politiquices:url ?url .
      ?url dc:title ?title
    }
    LIMIT 25



### List all the politicians in the graph belonging to the 'PS'     

    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT DISTINCT ?person ?personLabel {
      ?person wdt:P31 wd:Q5 .
      SERVICE <http://0.0.0.0:3030/wikidata/query> {
        ?person wdt:P102 wd:Q847263.
        ?person rdfs:label ?personLabel
        FILTER(LANG(?personLabel) = "pt")
      }
    }



### List everyone affiliated with 'Partido Socialista' that opposed 'José Sócrates'

    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX politiquices: <http://www.politiquices.pt/>
    PREFIX dc: <http://purl.org/dc/elements/1.1/>
        
    SELECT DISTINCT ?url ?title ?ent1 ?ent1_str ?ent1_name ?score WHERE {
      ?rel politiquices:type "ent1_opposes_ent2" .
      ?rel politiquices:score ?score .
      ?rel politiquices:type ?rel_type .
      ?rel politiquices:ent1 ?ent1 .
      ?rel politiquices:ent1_str ?ent1_str .
      ?rel politiquices:ent2 wd:Q182367 .
      ?rel politiquices:url ?url .
      ?url dc:title ?title
      {
        SELECT ?ent1 ?ent1_name WHERE 
        {
          ?ent1 wdt:P31 wd:Q5 .
          SERVICE <http://0.0.0.0:3030/wikidata/query> {
            ?ent1 wdt:P102 wd:Q847263.
            ?ent1 rdfs:label ?ent1_name
            FILTER(LANG(?ent1_name) = "pt")
          }
        }
      }
    }



### Personalities with a family relationship (e.g.: 'father', 'fon' or 'brother') connected through a support or opposes relationship  

    PREFIX  politiquices: <http://www.politiquices.pt/>
    PREFIX      rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX        wd: <http://www.wikidata.org/entity/>
    PREFIX       wdt: <http://www.wikidata.org/prop/direct/>
    
    SELECT DISTINCT ?person ?personLabel ?human_relationship ?other_person ?other_personLabel
        WHERE {
          VALUES ?human_relationship { wdt:P22 wdt:P25 wdt:P1038 }
          ?person ?human_relationship ?other_person;
                  rdfs:label ?personLabel. FILTER(LANG(?personLabel) = "pt") .
          ?other_person rdfs:label ?other_personLabel. FILTER(LANG(?other_personLabel) = "pt") .
          {SELECT DISTINCT ?person
            WHERE {
              SERVICE <http://0.0.0.0:3030/politiquices/query> {
                ?person wdt:P31 wd:Q5 .
                {?rel politiquices:ent1 ?person} UNION {?rel politiquices:ent2 ?person} .
                ?rel politiquices:type ?rel_type FILTER(!REGEX(?rel_type,"other")) .
              }
            }
          }
          {SELECT DISTINCT ?other_person
            WHERE {
              SERVICE <http://0.0.0.0:3030/politiquices/query> {
                ?other_person wdt:P31 wd:Q5;
                {?rel politiquices:ent1 ?other_person} UNION {?rel politiquices:ent2 ?other_person} .
                ?rel politiquices:type ?rel_type FILTER(!REGEX(?rel_type,"other")) .
              }
            }
          }
        }



### All public office positions hold by 'José Sócrates' (Wikidata Graph)

    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX wd:  <http://www.wikidata.org/entity/>
    PREFIX p: <http://www.wikidata.org/prop/>
    PREFIX ps: <http://www.wikidata.org/prop/statement/>
    PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
    
    SELECT DISTINCT ?office_title ?start ?end WHERE {
      wd:Q182367 p:P39 ?officeStmnt.
      ?officeStmnt ps:P39 ?office.
      ?office rdfs:label ?office_title. FILTER(LANG(?office_title)="pt")
      OPTIONAL { 
        ?officeStmnt pq:P580 ?start. 
        ?officeStmnt pq:P582 ?end. 
      }  
    } ORDER BY ?start



### All the professional occupations from 'José Sócrates' (Wikidata Graph)

    PREFIX p: <http://www.wikidata.org/prop/>
    PREFIX ps: <http://www.wikidata.org/prop/statement/>
    PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX wd:  <http://www.wikidata.org/entity/>
        
    SELECT DISTINCT ?occupation_label
    WHERE {
      wd:Q182367 p:P106 ?occupationStmnt .
      ?occupationStmnt ps:P106 ?occupation .
      ?occupation rdfs:label ?occupation_label FILTER(LANG(?occupation_label) = "pt").
    }



### All the education information from 'José Sócrates' (Wikidata Graph)

    PREFIX p: <http://www.wikidata.org/prop/>
    PREFIX ps: <http://www.wikidata.org/prop/statement/>
    PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX wd:  <http://www.wikidata.org/entity/>


    SELECT DISTINCT ?educatedAt_label
    WHERE {
          wd:Q182367 p:P69 ?educatedAtStmnt .
          ?educatedAtStmnt ps:P69 ?educatedAt .
          ?educatedAt rdfs:label ?educatedAt_label FILTER(LANG(?educatedAt_label) = "pt").
    }




##### All the wiki id from persons in the graph and the 'known as' and 'image_url' from Wikidata

    Note: some persons can have more than one picture 

    PREFIX       wdt:  <http://www.wikidata.org/prop/direct/>
    PREFIX        wd:  <http://www.wikidata.org/entity/>
    PREFIX        bd:  <http://www.bigdata.com/rdf#>
    PREFIX  wikibase:  <http://wikiba.se/ontology#>
    PREFIX      rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX 		 ns1: <http://xmlns.com/foaf/0.1/>
    PREFIX       rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    
    SELECT DISTINCT ?personLabel ?item ?image_url {
      ?item wdt:P31 wd:Q5 # get all human entities from the local graph
      SERVICE <https://query.wikidata.org/sparql> {
        OPTIONAL { ?item wdt:P18 ?image_url. }
        ?item rdfs:label ?personLabel
        SERVICE wikibase:label { bd:serviceParam wikibase:language "pt". ?item rdfs:label ?personLabel }
      }
    }



### All the "Governo Constitucional de Portugal" that José Sócrates was part of 

    PREFIX         p: <http://www.wikidata.org/prop/>
    PREFIX        ps: <http://www.wikidata.org/prop/statement/>
    PREFIX        pq: <http://www.wikidata.org/prop/qualifier/>
    PREFIX      rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX wd: <http://www.wikidata.org/entity/>
    
    SELECT DISTINCT ?cabinet ?cabinetLabel WHERE {
      wd:Q182367 wdt:P31 wd:Q5;
                 wdt:P27 wd:Q45;
                 p:P39 ?officeStmnt.
      ?officeStmnt ps:P39 ?office.
      OPTIONAL { ?officeStmnt pq:P580 ?start. }
      OPTIONAL { ?officeStmnt pq:P582 ?end. }  
      ?officeStmnt pq:P5054 ?cabinet. 
      ?cabinet ?x ?y.
      ?cabinet rdfs:label ?cabinetLabel . FILTER(LANG(?cabinetLabel) = "pt").
    } ORDER BY ?start



### All 'Legislaturas da Terceira República Portuguesa' (only works on live wikidata)

    PREFIX p: <http://www.wikidata.org/prop/>
    PREFIX ps: <http://www.wikidata.org/prop/statement/>
    PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT DISTINCT ?assembly ?assembly_label ?start ?end WHERE {
      ?assembly wdt:P31 wd:Q15238777;
                wdt:P17 wd:Q45;
                wdt:P571 ?start;
                wdt:P582 ?end;
                rdfs:label ?assembly_label . FILTER(LANG(?assembly_label) = "pt").
    } 
    ORDER BY DESC (?start)


### All 'Legislaturas da Terceira República Portuguesa' based on persons on the graph

    PREFIX p: <http://www.wikidata.org/prop/>
    PREFIX ps: <http://www.wikidata.org/prop/statement/>
    PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT DISTINCT ?legislature ?legislature_label WHERE {
      ?person wdt:P31 wd:Q5;
              wdt:P27 wd:Q45;
              p:P39 ?officeStmnt;
              rdfs:label ?personLabel . FILTER(LANG(?personLabel) = "pt")
      ?officeStmnt pq:P2937 ?legislature.
      ?legislature rdfs:label ?legislature_label . FILTER(LANG(?legislature_label) = "pt")
    } 
    ORDER BY DESC (?personLabel)


### All members of the 11th Portuguese Assembly, e.g: wd:Q25431189

    PREFIX p: <http://www.wikidata.org/prop/>
    PREFIX ps: <http://www.wikidata.org/prop/statement/>
    PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT DISTINCT ?person ?personLabel WHERE {
      ?person wdt:P31 wd:Q5;
              wdt:P27 wd:Q45;
              p:P39 ?officeStmnt;
              rdfs:label ?personLabel . FILTER(LANG(?personLabel) = "pt")
      ?officeStmnt ps:P39 ?office.
      ?officeStmnt pq:P2937 wd:Q25431189. 
    } 
    ORDER BY DESC (?personLabel)



### All 'public office' positions grouped by count

    PREFIX p: <http://www.wikidata.org/prop/>
    PREFIX ps: <http://www.wikidata.org/prop/statement/>
    PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT DISTINCT ?position_label (COUNT(?person) AS ?n)
    WHERE {
      ?person wdt:P31 wd:Q5;
              rdfs:label ?personLabel FILTER(LANG(?personLabel) = "pt") .
      ?person p:P39 ?positionStmnt .
      ?positionStmnt ps:P39 ?position .
      ?position rdfs:label ?position_label FILTER(LANG(?position_label) = "pt").
    }
    GROUP BY ?position_label
    HAVING (?n>1)
    ORDER BY DESC (?n)



### All 'occupations' grouped by count

    PREFIX p: <http://www.wikidata.org/prop/>
    PREFIX ps: <http://www.wikidata.org/prop/statement/>
    PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT DISTINCT ?occupation ?occupation_label (COUNT(?person) AS ?n)
    WHERE {
      ?person wdt:P31 wd:Q5;
              rdfs:label ?personLabel FILTER(LANG(?personLabel) = "pt") .
      ?person p:P106 ?occupationStmnt .
      ?occupationStmnt ps:P106 ?occupation .
      ?occupation rdfs:label ?occupation_label FILTER(LANG(?occupation_label) = "pt").
    }
    GROUP BY ?occupation ?occupation_label
    HAVING (?n>1)
    ORDER BY DESC (?n)


### 'Governo Constitucional' with the count of number of personalities from the graph


    PREFIX p: <http://www.wikidata.org/prop/>
    PREFIX ps: <http://www.wikidata.org/prop/statement/>
    PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT DISTINCT ?cabinet ?cabinetLabel (COUNT(?person) as ?n)
    WHERE {
      ?person wdt:P31 wd:Q5;
              p:P39 ?officeStmnt .
      ?officeStmnt ps:P39 ?office .
      ?officeStmnt pq:P5054 ?cabinet.
      ?cabinet rdfs:label ?cabinetLabel FILTER(LANG(?cabinetLabel) = "pt") .
    }
    GROUP by ?cabinet ?cabinetLabel
    ORDER BY DESC (?n)


### Education institution(s) attended by personalities from PS


    PREFIX p: <http://www.wikidata.org/prop/>
    PREFIX ps: <http://www.wikidata.org/prop/statement/>
    PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX wd:  <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>

    SELECT DISTINCT ?person ?personLabel ?educatedAt ?educatedAt_label {
      ?person wdt:P31 wd:Q5 .
      SERVICE <http://0.0.0.0:3030/wikidata/query> {
        ?person wdt:P102 wd:Q847263.
        ?person rdfs:label ?personLabel
        FILTER(LANG(?personLabel) = "pt")
        ?person p:P69 ?educatedAtStmnt .
        ?educatedAtStmnt ps:P69 ?educatedAt .
        ?educatedAt rdfs:label ?educatedAt_label FILTER(LANG(?educatedAt_label) = "pt")
      }
    }
    
### Get all personalities that studied at ISEG
    
    PREFIX p: <http://www.wikidata.org/prop/>
    PREFIX ps: <http://www.wikidata.org/prop/statement/>
    PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX wd:  <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>

    SELECT ?ent1 ?ent1_name ?educatedAt_label
    WHERE {
        ?ent1 wdt:P31 wd:Q5;
              rdfs:label ?ent1_name;
              p:P69 ?educatedAtStmnt.
        ?educatedAtStmnt ps:P69 wd:Q2655186 .
        wd:Q2655186 rdfs:label ?educatedAt_label FILTER(LANG(?educatedAt_label) = "pt").
        FILTER(LANG(?ent1_name) = "pt")
      }
      
      
      
      
### Get all education instutions on the graph
      
    PREFIX p: <http://www.wikidata.org/prop/>
    PREFIX ps: <http://www.wikidata.org/prop/statement/>
    PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX wd:  <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>

    SELECT DISTINCT ?educatedAt ?educatedAt_label
    WHERE {
        ?ent1 wdt:P31 wd:Q5;
              rdfs:label ?ent1_name;
              p:P69 ?educatedAtStmnt.
        ?educatedAtStmnt ps:P69 ?educatedAt .
        ?educatedAt rdfs:label ?educatedAt_label FILTER(LANG(?educatedAt_label) = "pt").
        FILTER(LANG(?ent1_name) = "pt")
      }
    ORDER BY ASC(?educatedAt_label)
    
    
### Get all the 'advogados' in the graph

    PREFIX p: <http://www.wikidata.org/prop/>
    PREFIX ps: <http://www.wikidata.org/prop/statement/>
    PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX wd:  <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>

    SELECT ?ent1 ?ent1_name ?profissao
    WHERE {
        ?ent1 wdt:P31 wd:Q5;
              rdfs:label ?ent1_name;
              p:P106 ?occupationStmnt .
        ?occupationStmnt ps:P106 wd:Q40348 .
        wd:Q40348 rdfs:label ?profissao FILTER(LANG(?profissao) = "pt").
        FILTER(LANG(?ent1_name) = "pt")
      }


### List all the Governments of Portugal since the first Republic

    PREFIX p: <http://www.wikidata.org/prop/>
    PREFIX ps: <http://www.wikidata.org/prop/statement/>
    PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT DISTINCT ?government ?government_label ?head ?head_label ?start ?end WHERE {
      ?government wdt:P31 wd:Q16850120;
                  wdt:P17 wd:Q45;
                  wdt:P571 ?start;
                  wdt:P576 ?end;
                  wdt:P6 ?head;
                  rdfs:label ?government_label . FILTER(LANG(?government_label) = "pt").
      ?head rdfs:label ?head_label . FILTER(LANG(?head_label) = "pt").
    } 
    ORDER BY DESC (?start)
