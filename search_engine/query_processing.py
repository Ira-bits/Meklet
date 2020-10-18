from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import nltk


def download_nltk_deps():
    """
    Downloads NLTK English language datasets. This function needs to be called only once in a lifetime.
    """
    nltk.download("punkt")
    nltk.download("stopwords")


def tokenize(text):
    """
    Given an input string `text`, returns a list of lowercase words containing
    representing the tokenized version of `text`, excluding punctuation
    like comma, question mark, whitespace, etc.
    """
    assert type(text) == str
    tokenized_words = word_tokenize(text.lower())

    # Remove tokens like comma, question mark and other punctuation.
    filtered_words = list(filter(lambda word: len(word) > 1, tokenized_words))
    return filtered_words


# Uncomment below to test tokenizer
# print(tokenize("was it raining yesterday night or i have been gaming! It can't be true?"))


def remove_stopwords(token_list):
    """
    Given a list of english words, removes stopwords from it ( such as he her was etc.).
    """
    stop_words = set(stopwords.words("english"))
    filtered_tokens = [w for w in token_list if not w in stop_words]
    return filtered_tokens


# Uncomment below to test remove_stopwords
# print(remove_stopwords(["a", "and", "the", "hello", "goodbye"]))


def stem(token_list):
    """
    Given an list of tokenized words, returns their stemmed forms, using NLTK
    For example, `["playing"]` becoms `["play"]`.
    """

    assert type(token_list) == list
    ps = PorterStemmer()
    stemmed_words = list(map(lambda word: ps.stem(word), token_list))
    result = " ".join(map(str, stemmed_words))
    return result


# Uncomment below to test stemmer
# print(stem(tokenize("was it raining yesterday night OR i have been gaming! It can't be true?")))


def process_boolean_query(query):
    """
    Given a boolean search query as a string, splits it into individual queries and operators.
    Also performs stemming, normalization, tokenization and removal of stopwords.
    For example, given the query `"Harry potter books" and "best movies" or "best scenes"` the processing will return a tuple:
    `1. queries: ["Harry potter books", "best movies", "best scenes"]`
    `2. operators: ["and", "or"]`

    Note: If the first operator is empty (`''`), it means the first sub-query does not have any operactor for itself.

    Queries are intended to be processed in LTR direction.
    """
    assert type(query) == str
    query = query.strip()
    in_query = False
    pieces = query.split('"')
    queries = []
    operators = []

    for item in pieces:
        disposable = item.strip()
        if in_query:
            disposable = process_string(disposable)
            queries += disposable
        else:
            operators.append(disposable)
        in_query = not in_query
    operators.pop()
    return queries, operators


# Uncomment below to test process_boolean_query
# queries, operators = process_boolean_query(
#     '"hi" and "bye" or not "hey"')
# print(queries)
# print(operators)


def process_string(query):
    """
    Given a query string, performs stemming, normalization, tokenization and removal of stopwords and returns
    a list.
    """
    assert type(query) == str
    disposable = query.strip()
    disposable = tokenize(disposable)
    disposable = remove_stopwords(disposable)
    disposable = stem(disposable)
    print(disposable)
    return disposable.split(" ")


# Uncomment below to test process_string
# print(process_string("i want to be sleeping right now and he is bothering me"))
