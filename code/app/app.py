import os, requests, json
from rdflib import Graph
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
from flask import jsonify, request, render_template, Flask, redirect

app = Flask(__name__)
load_dotenv()
format_dict = {"JSON-LD": "json", "Turtle": "turtle", "N-Triples": "turtle", "TriG": "trig", "RDF/XML": "xml"}
serializer_dict = {"JSON-LD": "json-ld", "Turtle": "turtle", "N-Triples": "nt", "TriG": "trig", "RDF/XML": "pretty-xml"}
loaded_games = []

def load_games_from_db():
    global loaded_games
    try:
        basic = HTTPBasicAuth(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
        r = requests.post(f"{os.getenv('NEO4J_HTTP_URI')}/rdf/neo4j/cypher",
                         auth=basic, json={"cypher": "MATCH (g:Game) RETURN g", "format": "JSON-LD"})
        for game in r.json()["@graph"]:
            loaded_games.append({"name":game['sch:name'], "score":game['sch:aggregateRating']['@value'], "id":game['@id']})
        loaded_games.sort(key=lambda x: x['score'], reverse=True)

    except Exception as e:
        print(f"Error while loading the games: {e}")

@app.route("/")
def index():
    return redirect('/form')

@app.route("/game/name/<name>", methods=["GET"])
def get_game(name, game_id, format="JSON-LD"):
    basic = HTTPBasicAuth(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
    if game_id:
        r = requests.get(f"{os.getenv('NEO4J_HTTP_URI')}/rdf/neo4j/describe/{game_id.replace('n4ind:', '')}?format=JSON-LD",
                         auth=basic)
    else:
        r = requests.get(f"{os.getenv('NEO4J_HTTP_URI')}/rdf/neo4j/describe/find/Game/name/{name}?format=JSON-LD", auth=basic)

    # Load json-ld data into an dict
    request_data = json.loads(r.text)

    # Retrieve the names for the ids
    genres, platforms, developers, publishers = name_lookup_for_game(name)

    # Add the new names to the request data
    processed_request = process_response_for_game(request_data, genres, platforms, developers, publishers)

    # Parse the JSON-LD data into an RDF graph
    if format.lower() != "json-ld":  
        graph = Graph()
        graph.parse(data=processed_request, format="json-ld", publicID="http://schema.org/")

        # Get the format to the serializer format
        serializer_format = serializer_dict.get(format)

        # Serialize the graph into the requested format
        processed_request = graph.serialize(format=serializer_format)

    return render_template("view.html", format_name=format, format=format_dict.get(format), data=processed_request)

def process_response_for_game(response, genres, platforms, developers, publishers):
    response['sch:genre'] = genres
    response['sch:gamePlatform'] = platforms
    response['sch:publisher'] = publishers
    response['sch:creator'] = developers
    if response.get('sch:datePublished'):
        response['sch:datePublished'] = response.get('sch:datePublished').get('@value')

    # Drop n4sch prefix from @context, since obsolete
    del response['@context']['n4sch']

    processed_response = json.dumps(response, indent=4)

    return processed_response

def name_lookup_for_game(name):
    queries = {
        "genre": """
            MATCH (v:Game)-[:HAS_GENRE]->(g:Genre)
            WHERE v.name = "{name}"
            RETURN g;
        """,
        "platform": """
            MATCH (v:Game)-[:AVAILABLE_ON]->(p:Platform)
            WHERE v.name = "{name}"
            RETURN p;
        """,
        "developer": """
            MATCH (v:Game)-[:developer]->(d:Company)
            WHERE v.name = "{name}"
            RETURN d;
        """,
        "publisher": """
            MATCH (v:Game)-[:publisher]->(p:Company)
            WHERE v.name = "{name}"
            RETURN p;
        """
    }
    
    results = {}
    basic = HTTPBasicAuth(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
    url = f"{os.getenv('NEO4J_HTTP_URI')}/rdf/neo4j/cypher"

    for key, query in queries.items():
        cypher_query = query.format(name=name)
        response = requests.post(url, auth=basic, json={"cypher": cypher_query, "format": "JSON-LD"})

        if response.status_code == 200:
            r_json = response.json()
            del r_json["@context"]
            if r_json.get("@graph"):
                r_json = r_json["@graph"]

            # To keep the standard from schema.org, genre only as a list of strings
            if key == "genre":
                r_json = [genre["sch:name"] for genre in r_json]

            results[key] = r_json
        else:
            results[key] = {"error": response.text}

    return results.get("genre", {}), results.get("platform", {}), results.get("developer", {}), results.get("publisher", {})

@app.route("/autocomplete", methods=["GET"])
def autocomplete():
    input_text = request.args.get("q", "").lower()

    suggestions = [
        game for game in loaded_games
        if input_text in game["name"].lower()
    ]

    return jsonify(suggestions)

@app.route("/form", methods=["GET", "POST"])
def show_form():
    if request.method == "POST":
        search_term = request.form.get("search_term")
        format_option = request.form.get("format_dropdown")
        game_id = request.form.get("game_id")
        return get_game(search_term, game_id, format_option)

    format_options = format_dict.keys()
    return render_template("form.html", format_options=format_options)

with app.app_context():
    load_games_from_db()

if __name__ == "__main__":
    app.run(debug=True)