""" Contains helper classes/functions for searching results in index """

import search_engine
import pickle
import sys
from pathlib import Path
from collections import OrderedDict


class LRUCache:
    """ Class to implement LRU Cache """

    def __init__(self, capacity: int):
        """ Initializes an Ordered Dictionary and cache capacity """
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, key: int) -> int:
        """
        Returns the value of the key that is queried in O(1) and return -1 if the key
        is not found in dict / cache. Moves the key to the end to mark that it
        was recently used.
        """
        if key not in self.cache:
            return -1
        else:
            self.cache.move_to_end(key)
            return self.cache[key]

    def put(self, key: int, value: int) -> None:
        """
        Adds/Updates the key by conventional methods. Moves the key to the end to mark
        that it was recently used. Checks whether the length of our ordered dictionary
        has exceeded the cache capacity, If so then removes the first key (least recently used)
        """
        self.cache[key] = value
        self.cache.move_to_end(key)
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)


def reconstruct(query, operators=None):
    """ Reconstructs the processed query to be stored in cache """
    recons_query = ""
    if not operators:
        for piece in query:
            recons_query += piece + " "
    else:
        for itr in range(len(operators)):
            temp_query = ""
            for piece in query[itr]:
                temp_query += piece + " "
            temp_query = temp_query.strip()
            if operators[itr] != "":
                recons_query += operators[itr] + " " + temp_query + " "
            else:
                recons_query += temp_query + " "
    return recons_query.strip()


def get_link_title_for_docId(docId, id_dict):
    "Given a docId returns the document title and Wikipedia link."
    doc_name = id_dict[docId]
    file = open("./corpus/" + doc_name, "r")
    lines = file.readlines()
    title = lines[2].strip()
    link = "https://en.wikipedia.org/wiki/" + Path(doc_name).stem
    return title, link


def regular_search(processed_query):
    """ Takes in a query and returns a list of corresponding (docId,freq) pairs """
    res = sorted(
        search_engine.calculate_query_tf_idf(processed_query),
        key=lambda x: x[1],
        reverse=True,
    )[:10]
    return res


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


def advanced_search(separated_query, operators):
    """
    Takes in a boolean query and returns results evaluated using
    Optimal Merge Pattern Algorithm
    """
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
        results = results[: pos - 1] + [merged_list] + results[pos + 1 :]
        operators = operators[:pos] + operators[pos + 1 :]
        and_present = 1 if "and" in operators else 0

    # Only "or" operator would have been left
    final_result = []
    for result in results:
        result.sort(key=lambda x: x[0])
        final_result = merge(final_result, result, operator="or")

    res = sorted(final_result, key=lambda x: x[1], reverse=True)[:10]
    return res
