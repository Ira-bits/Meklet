""" Flask app for Meklet Search Engine Web Client """

from flask import Flask, request, jsonify, make_response, render_template
from flask_cors import CORS
import search_engine
import pickle
import time
from pathlib import Path
from helper import (
    regular_search,
    advanced_search,
    get_link_title_for_docId,
    LRUCache,
    reconstruct,
)


# Initialize Flask app
app = Flask(
    __name__,
    static_url_path="",
    static_folder="search_client/static",
    template_folder="search_client/templates",
)
CORS(app)
app.config["DEBUG"] = True  # Change to False in Production
id_dict = {}

# Initialize Cache
cache = LRUCache(100)
adv_cache = LRUCache(100)


@app.route("/", methods=["GET"])
def home():
    """ Route to serve home page of the Web App """
    return render_template("index.html")


@app.route("/api/search-results", methods=["GET"])
def api_search():
    """
    API Route for querying the backend.

        * Params - 1. advanced = {"true","false"}
                   2.  query="<query_string>"
        * Return Format - [(docID, tf-idf score, title, summary)]

    Processes the query -> Looks in cache -> If results not found, Looks in Index -> Returns results
    """

    params = request.args
    advanced = params["advanced"]
    query = params["query"]

    # Validate Request Parameters
    try:
        assert type(advanced) == str
        assert type(query) == str
        if advanced not in ["true", "false"]:
            raise AssertionError()
    except AssertionError:
        response = make_response("Invalid Request Parameters", 400)
        return response

    if advanced == "true":
        separated_query, operators = search_engine.process_boolean_query(query)
        cache_query = reconstruct(separated_query, operators)
        cache_search = adv_cache.get(cache_query)
        if cache_search != -1:
            results = cache_search
        else:
            results = advanced_search(separated_query, operators)
            adv_cache.put(cache_query, results)
    else:
        processed_query = search_engine.process_string(query)
        cache_query = reconstruct(processed_query)
        cache_search = cache.get(cache_query)
        if cache_search != -1:
            results = cache_search
        else:
            results = regular_search(processed_query)
            cache.put(cache_query, results)

    results_with_data = []
    for docId, tf_idf in results:
        data = get_link_title_for_docId(docId, id_dict)
        results_with_data.append((docId, tf_idf, data[0], data[1]))

    # Convert the list of results to JSON format.
    return jsonify(results_with_data)


if __name__ == "__main__":

    # Download Required Dependencies
    search_engine.download_nltk_deps()

    # Check if index needs to be created
    if not Path("./index_files/index.db").exists():
        create = True
    else:
        print("Do you want to recreate the index? (y/n)")
        create = False if input().lower() == "n" else True

    if create:
        try:
            print("Constructing Index ...")
            search_engine.start_indexing()
            print("Index Successfully Created!")
        except Exception as e:
            print(e)
            print("Aborting! Please Try Again.")
            exit()

    # Load docId dict in memory
    file = open("./index_files/docId.pkl", "rb")
    id_dict = pickle.load(file)

    # Start the Server process
    app.run(use_reloader=False)
