import shelve


def lookup_term(term):
    """
    Takes in a term ,looks it up in the index and returns a dict containing docId,freq
    as key-value pairs. Returns an empty dictionary if the term is absent in the index.
    """

    index_obj = shelve.open("./index_files/index.db")
    try:
        result = index_obj[term]
    except KeyError:  # term not found in the index.
        result = {}
    finally:
        index_obj.close()
        return result
