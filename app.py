import flask
from flask import request, jsonify, make_response
from flask_cors import CORS
import search_engine
import pickle
import sys
from pathlib import Path

# Initialize Flask app
app = flask.Flask(__name__)
CORS(app)
app.config["DEBUG"] = True  # Change to False in Production
id_dict = {}


def get_link_title_for_docId(docId):
    "Given a docId returns the document title and Wikipedia link."
    doc_name = id_dict[docId]
    file = open("./corpus/" + doc_name, "r")
    lines = file.readlines()
    title = lines[2].strip()
    link = "https://en.wikipedia.org/wiki/" + Path(doc_name).stem
    return title, link


def regular_search(query):
    """ Takes in a query and returns a list of corresponding (docId,freq) pairs """
    processed_query = search_engine.process_string(query)
    return sorted(
        search_engine.calculate_query_tf_idf(processed_query),
        key=lambda x: x[1],
        reverse=True,
    )[:10]


def merge(list_a, list_b, operator="and"):
    """ Takes in two sorted lists and returns a single sorted merged list """
    list_c = []
    i = 0
    j = 0
    while i < len(list_a) and j < len(list_b):
        if list_a[i][0] == list_b[j][0]:
            score = (
                list_a[i][1] + list_b[j][1]
                if operator == "and"
                else max(list_a[i][1], list_b[j][1])
            )  # Add scores for "and", take highest for "or"
            list_c.append((list_a[i][0], score))
            i += 1
            j += 1
        elif list_a[i][0] < list_b[j][0]:
            if operator != "and":
                list_c.append(list_a[i])
            i += 1
        else:
            if operator != "and":
                list_c.append(list_b[j])
            j += 1

    while i < len(list_a) and operator == "or":
        list_c.append(list_a[i])
        i += 1
    while j < len(list_b) and operator == "or":
        list_c.append(list_b[j])
        j += 1
    return list_c


def advanced_search(query):
    """
    Takes in a boolean query and returns results evaluated using
    Optimal Merge Pattern Algorithm
    """
    separated_query, operators = search_engine.process_boolean_query(query)
    results = []
    for query in separated_query:
        results.append(
            sorted(
                search_engine.calculate_query_tf_idf(query),
                key=lambda x: x[0],
            )
        )  # Add list (sorted according to docId) to the 2D-List

    and_present = 1 if "and" in operators else 0

    # First Merges list with "and" operator
    while and_present:
        smallest = (
            sys.maxsize,
            sys.maxsize,
        )  # Find lists with smallest length and separated by "and"
        pos = 0
        for i in range(len(results)):
            if operators[i] == "and":
                if len(results[i - 1]) + len(results[i]) < smallest[0] + smallest[1]:
                    smallest = (len(results[i - 1]), len(results[i]))
                    pos = i
        merged_list = merge(results[pos - 1], results[pos])  # Merge smallest lists
        # Remove relevant lists and operator "and", and add merged list
        results = results[: pos - 1] + merged_list + results[pos + 2 :]
        operators = operators[:pos] + operators[pos + 1 :]
        and_present = 1 if "and" in operators else 0

    # Only "or" operator would have been left
    final_result = []
    for result in results:
        result.sort(key=lambda x: x[0])
        final_result = merge(final_result, result, operator="or")

    return sorted(final_result, key=lambda x: x[1], reverse=True)[:10]


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
        results = advanced_search(query)
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
