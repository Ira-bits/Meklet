import flask
from flask import request, jsonify, make_response
from flask_cors import CORS
import search_engine
import pickle
import re
from pathlib import Path

# Initialize FLask app
app = flask.Flask(__name__)
CORS(app)
app.config["DEBUG"] = True  # Change to False in Production

# Load docId dict in memory
file = open("./index_files/docId.pkl", "rb")
id_dict = pickle.load(file)


def get_link_title_for_docId(docId):
    "Given a docId returns the document title and Wikipedia link."
    doc_name = id_dict[docId]
    file = open('./corpus/' + doc_name, "r")
    lines = file.readlines()
    title = lines[2].strip()
    link = "https://en.wikipedia.org/wiki/" + Path(doc_name).stem
    return title, link


def regular_search(query):
    processed_query = search_engine.process_string(query)
    return sorted(
        search_engine.calculate_query_tf_idf(processed_query), key=lambda x: x[1], reverse=True)[:10]


@app.route("/", methods=["GET"])
def home():
    return "Serve Home Page from this URL!"


@app.route("/api/search-results", methods=["GET"])
def api_search():
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
        pass  # TODO: Advanced Search
    else:
        results = regular_search(query)
        results_with_data = []
        for docId, tf_idf in results:
            data = get_link_title_for_docId(docId)
            results_with_data.append((docId, tf_idf, data[0], data[1]))
            # Convert the list of results to JSON format.
    return jsonify(results_with_data)


if __name__ == "__main__":

    # Download Required Dependencies
    search_engine.download_nltk_deps()

    print("Do you want to recreate the index? (y/n)")
    recreate = False if input().lower() == "n" else True

    if recreate:
        try:
            print("Constructing Index ...")
            search_engine.start_indexing()
            print("Index Successfully Created!")
        except Exception as e:
            print(e)
            print("Aborting! Please Try Again.")
            exit()

    # Start the Server process
    app.run(use_reloader=False)
