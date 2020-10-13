from index_lookup import lookup_term
import os
from math import log10


def calculate_term_tf_idf(term):
    """
    Takes in a term and returns a list of (docId, tf-idf weight) pairs.
    Returns an empty list if the term isn't present in any of the documents.
    """
    term_frequencies = lookup_term(term)
    total_number_of_docs = len(os.listdir("corpus"))
    document_frequency = len(term_frequencies.keys())

    # use (total_number_of_docs + 1) as numerator to handle cases when document_frequency = total_number_of_docs
    # use (1 + document_frequency) as denominator to handle cases when document_frequency comes out to be zero
    idf = log10(total_number_of_docs + 1 / 1 + document_frequency)
    tf_idf_weights = []
    for document_data in term_frequencies.items():
        docId, freq = document_data
        log_frequency_weight = 1 + log10(freq)
        document_tf_idf = log_frequency_weight * idf
        tf_idf_weights.append((docId, document_tf_idf))
    return tf_idf_weights


def calculate_query_tf_idf(query):
    """
    Takes in a query (a list of words that is obtained after normalization) and returns a list of (docId, tf-idf weight) pairs.
    Returns an empty list if any term of the query isn't present in any of the documents.
    """
    tf_idf_weights = []
    document_weights_dict = {}

    for term in query:
        term_tf_idfs = calculate_term_tf_idf(term)
        for docId, tf_idf in term_tf_idfs:
            if docId in document_weights_dict:
                document_weights_dict[docId] += tf_idf
            else:
                document_weights_dict[docId] = tf_idf

    for docId, tf_idf in document_weights_dict.items():
        tf_idf_weights.append((docId, tf_idf))

    return tf_idf_weights


print(calculate_query_tf_idf(["and"]))