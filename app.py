""" Flask app for Meklet Search Engine Web Client """

from flask import Flask, request, jsonify, make_response, render_template
from flask_cors import CORS
import search_engine
import pickle
import time
from pathlib import Path
from helper import regular_search, advanced_search, get_link_title_for_docId, LRUCache

cache=LRUCache(5)
adv_cache=LRUCache(5)

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


@app.route("/", methods=["GET"])
def home():
    """ Route to serve home page of the Web App """
    print("here")
    return render_template("index.html")


@app.route("/api/search-results", methods=["GET"])
def api_search():
    """
    API Route for querying the backend.

        * Params - 1. advanced = {"true","false"}
                   2.  query="<query_string>"
        * Return Format - [(docID, tf-idf score, title, summary)]
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
    start=time.time()
    flag=True
    if(flag):
        if advanced == "true":
            cache_search=adv_cache.get(query)
            if(cache_search!=-1):
                results=cache_search
            else:
                results = advanced_search(query)
                adv_cache.put(query,results)
        else:
            cache_search=cache.get(query)
            if(cache_search!=-1):
                results=cache_search
            else:
                results = regular_search(query)
                cache.put(query,results)
    else:
        if advanced == "true":
            results = advanced_search(query)
        else:
            results = regular_search(query)
    results_with_data = []
    for docId, tf_idf in results:
        data = get_link_title_for_docId(docId, id_dict)
        results_with_data.append((docId, tf_idf, data[0], data[1]))
    end=time.time()
    print(end-start)
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
