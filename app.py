import flask
from flask import request, jsonify, make_response
from flask_cors import CORS
import search_engine

# Initialize FLask app
app = flask.Flask(__name__)
CORS(app)
app.config["DEBUG"] = True  # Change to False in Production


def regular_search(query):
    processed_query = search_engine.process_string(query)
    return sorted(
        search_engine.calculate_query_tf_idf(processed_query), key=lambda x: x[1]
    )


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

    # Convert the list of results to JSON format.
    return jsonify(results)


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
