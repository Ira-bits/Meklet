""" Contains helper functions for searching results in index """

import search_engine
import pickle
import sys
from pathlib import Path
from collections import OrderedDict

class LRUCache:
 
    # initialising capacity
    def __init__(self, capacity: int):
        self.cache = OrderedDict()
        self.capacity = capacity
 
    # we return the value of the key
    # that is queried in O(1) and return -1 if we
    # don't find the key in out dict / cache.
    # And also move the key to the end
    # to show that it was recently used.
    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        else:
            self.cache.move_to_end(key)
            return self.cache[key]
 
    # first, we add / update the key by conventional methods.
    # And also move the key to the end to show that it was recently used.
    # But here we will also check whether the length of our
    # ordered dictionary has exceeded our capacity,
    # If so we remove the first key (least recently used)
    def put(self, key: int, value: int) -> None:
        self.cache[key] = value
        self.cache.move_to_end(key)
        if len(self.cache) > self.capacity:
            self.cache.popitem(last = False)


def get_link_title_for_docId(docId, id_dict):
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
        results = results[: pos - 1] + [merged_list] + results[pos + 1 :]
        operators = operators[:pos] + operators[pos + 1 :]
        and_present = 1 if "and" in operators else 0

    # Only "or" operator would have been left
    final_result = []
    for result in results:
        result.sort(key=lambda x: x[0])
        final_result = merge(final_result, result, operator="or")

    res= sorted(final_result, key=lambda x: x[1], reverse=True)[:10]
    return res
