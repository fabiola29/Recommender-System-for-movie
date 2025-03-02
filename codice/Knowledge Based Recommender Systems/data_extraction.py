import rdflib
from SPARQLWrapper import SPARQLWrapper, JSON
import re
import os
import signal
import urllib.parse

# Impostazione dell'endpoint SPARQL di DBpedia con timeout
sparql = SPARQLWrapper("http://dbpedia.org/sparql")
sparql.setTimeout(30)  # Timeout aumentato a 30 secondi

# Creazione del grafo RDF
g = rdflib.Graph()
nspace = rdflib.Namespace("http://dbpedia.org/resource/")
g.bind("dbo", "http://dbpedia.org/ontology/")
g.bind("dbp", "http://dbpedia.org/property/")
g.bind("dbr", "http://dbpedia.org/resource/")

# Caricare l'ontologia esistente se esiste
ontology_file = "movies_ontology.ttl"
if os.path.exists(ontology_file):
    g.parse(ontology_file, format="turtle")
    print("Ontologia esistente caricata.")


def extract_title_and_year(raw_title):
    parts = raw_title.split(",")
    if len(parts) > 1:
        title = parts[1].strip()
    else:
        title = raw_title.strip()

    # Rimuove eventuali virgolette residue
    title = title.strip('"')

    # Estrae l'anno tra parentesi, se presente
    year_match = re.search(r"\((\d{4})\)$", title)
    if year_match:
        year = year_match.group(1)
        title = re.sub(r" \(\d{4}\)$", "", title)  # Rimuove l'anno dal titolo
    else:
        year = None
    print(year)
    return title, year


# Funzione per creare un URI valido per DBpedia
def create_valid_uri(title):
    title = title.strip().replace(" ", "_")  # Sostituisce spazi con "_"
    title = urllib.parse.quote(title, safe="_")  # Codifica caratteri speciali
    return rdflib.URIRef(f"http://dbpedia.org/resource/{title}")


# Funzione per verificare se il titolo è già presente nell'ontologia
def is_title_in_graph(title):
    movie_uri = create_valid_uri(title)
    return (movie_uri, None, None) in g


# Funzione per sanificare il titolo per SPARQL
def sanitize_sparql_title(title):
    title = title.replace('"', "'")  # Sostituisce i doppi apici con apici singoli
    return f'"""{title}"""'  # Usa triple virgolette per evitare problemi di sintassi


# Funzione per eseguire la query SPARQL su DBpedia
def get_movie_data(title, retries=3):
    sparql_title = sanitize_sparql_title(title)  # Sanifica il titolo per la query

    # MODIFICA PRINCIPALE: usiamo GROUP_CONCAT per unire tutti gli attori in un'unica stringa
    # e SAMPLE(...) per le altre proprietà, in modo da avere un'unica riga di risultato per film.
    query = f"""
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX dbp: <http://dbpedia.org/property/>
    SELECT
        (SAMPLE(?country) as ?country)
        (SAMPLE(?abstract) as ?abstract)
        (SAMPLE(?director) as ?director)
        (SAMPLE(?runtime) as ?runtime)
        (GROUP_CONCAT(DISTINCT ?starring; separator=\"@@\") as ?allStarring)
    WHERE {{
        ?film a dbo:Film ;
              rdfs:label {sparql_title}@en ;
              dbo:abstract ?abstract .
        OPTIONAL {{ ?film dbo:director ?director . }}
        OPTIONAL {{ ?film dbo:runtime ?runtime . }}
        OPTIONAL {{ ?film dbo:starring ?starring . }}
        OPTIONAL {{ ?film dbp:country ?country . }}
        FILTER (lang(?abstract) = "en")
    }}
    GROUP BY ?film
    """

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    for attempt in range(retries):
        try:
            results = sparql.query().convert()
            if results["results"]["bindings"]:
                # Otteniamo la prima (e unica) riga di risultato
                result = results["results"]["bindings"][0]

                # Ricordiamo che adesso gli attori sono sotto la chiave "allStarring"
                starring_str = result.get("allStarring", {}).get("value", "")

                return {
                    "Country": result.get("country", {}).get("value", "N/A"),
                    "Abstract": result.get("abstract", {}).get("value", "N/A"),
                    "Director": result.get("director", {}).get("value", "N/A"),
                    "Runtime": result.get("runtime", {}).get("value", "N/A"),
                    "Starring": starring_str if starring_str else "N/A"
                }
            print(f"Nessun dato trovato per {title}, potrebbe non essere su DBpedia con questo nome.")
            return None
        except Exception as e:
            print(f"Tentativo {attempt + 1} fallito per {title}: {e}")

    print(f"Errore definitivo nella richiesta SPARQL per {title}.")
    return None


# Funzione per salvare periodicamente il grafo
def save_graph():
    g.serialize(destination=ontology_file, format="turtle")
    print(f"Ontologia RDF salvata in '{ontology_file}' e interrogabile con query SPARQL in locale!")


# --- AGGIUNTA: Caricamento delle views dal file ratings.csv ---
ratings_file = "../../dataset/archive/ratings.csv"
views_dict = {}

if os.path.exists(ratings_file):
    with open(ratings_file, mode="r", encoding="utf-8") as rf:
        next(rf)  # Salta l'intestazione
        for rating_row in rf:
            splitted_rating = rating_row.strip().split(",")
            # Formato standard: userId,movieId,rating,timestamp
            if len(splitted_rating) >= 2:
                rating_movie_id = splitted_rating[1]
                views_dict[rating_movie_id] = views_dict.get(rating_movie_id, 0) + 1
else:
    print(f"File delle valutazioni '{ratings_file}' non trovato. Nessuna view sarà aggiunta.")
# --- FINE AGGIUNTA ---

# Lettura del dataset di input
input_file = "../../dataset/archive/movies.csv"

with open(input_file, mode="r", encoding="utf-8") as infile:
    next(infile)  # Salta la prima riga (intestazioni)
    for idx, row in enumerate(infile, start=1):
        genres = []
        title, year = extract_title_and_year(row.strip())
        genres = row.strip()

        if is_title_in_graph(title):
            print(f"Il film '{title}' è già presente nell'ontologia, salto.")
            continue

        print(f"Recupero dati per: {title}")
        movie_data = get_movie_data(title)

        # Creiamo subito l'URI del film
        movie_uri = create_valid_uri(title)

        # AGGIUNTA: Cattura l'anno tra parentesi dalla riga originale e inseriscilo in 'dbp:released'
        if year and year.isdigit():
            g.add((movie_uri, rdflib.URIRef("http://dbpedia.org/property/released"),
                   rdflib.Literal(int(year))))

        if movie_data:
            # Tipizzazione e proprietà base
            g.add((movie_uri, rdflib.RDF.type, rdflib.URIRef("http://dbpedia.org/ontology/Film")))
            g.add((movie_uri, rdflib.RDFS.label, rdflib.Literal(title, lang="en")))
            g.add((movie_uri, rdflib.URIRef("http://dbpedia.org/ontology/abstract"),
                   rdflib.Literal(movie_data["Abstract"], lang="en")))
            g.add((movie_uri, rdflib.URIRef("http://dbpedia.org/ontology/director"),
                   rdflib.Literal(movie_data["Director"])))
            runtime_value = movie_data["Runtime"]
            print(f"Valore di runtime ricevuto: '{runtime_value}'")
            runtime_value = runtime_value.strip()
            try:
                runtime_as_int = int(float(runtime_value))
                g.add((movie_uri, rdflib.URIRef("http://dbpedia.org/ontology/runtime"),
                       rdflib.Literal(runtime_as_int)))
            except ValueError:
                print(f"Valore di runtime non convertibile in numero: '{runtime_value}'")

            g.add((movie_uri, rdflib.URIRef("http://dbpedia.org/ontology/country"),
                   rdflib.Literal(movie_data["Country"])))


            # GESTIONE ATTORI MULTIPLI: la query li concatena con '@@'
            # Se 'Starring' è diverso da 'N/A', scompone la stringa
            if movie_data["Starring"] != "N/A":
                # Sarà una stringa come \"Actor1@@Actor2@@Actor3...\"
                starring_list = movie_data["Starring"].split("@@")
                for actor in starring_list:
                    actor = actor.strip()
                    if actor:
                        g.add((movie_uri, rdflib.URIRef("http://dbpedia.org/ontology/starring"),
                               rdflib.Literal(actor)))

        splitted = row.strip().split(",")
        # AGGIUNTA: Salva l'ID del film
        movie_id = splitted[0]  # Consideriamo che la prima colonna sia l'ID
        # AGGIUNTA: Recupera il numero di views dal dizionario creato prima
        views = views_dict.get(movie_id, 0)
        # AGGIUNTA: Inserisci la property "views" nel grafo
        g.add((movie_uri, rdflib.URIRef("http://dbpedia.org/property/views"), rdflib.Literal(views)))

        # AGGIUNTA (pre-esistente): controlla se splitted[2], splitted[3], ecc. è un anno (4 cifre) o dei generi.
        for col in range(2, len(splitted)):
            val = splitted[col].strip()
            if re.match(r'^\\d{4}$', val):
                g.add((movie_uri, rdflib.URIRef("http://dbpedia.org/property/released"),
                       rdflib.Literal(val)))
            else:
                g.add((movie_uri, rdflib.URIRef("http://dbpedia.org/ontology/genre"),
                       rdflib.Literal(val)))

        if idx % 10 == 0:
            save_graph()

save_graph()
