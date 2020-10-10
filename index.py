"""
*Index Generator*

    * Assigns a docID to each document in the corpus.
    * Parses The documents to create intermidiate inverted indices.
    * Uses Block Sort and Merge Algorithm to generate an unified inverted index.
    * Finally, creates a shelf containing term as key and list of (docId,freq) as value.

"""

import pickle
import shelve
import os
from settings import BLOCK_SIZE


# Helper functions for the Block Sort Based Indexing Algorithm -
# open_file() --> opens new index files as and when required.
# sort_list() --> sorts a given list of tuples first by term then by docID.
# write_to_file() --> dumps index to disk.
# find_smallest() --> returns the smallest tuple and updates object_list accordingly.


def open_file(curr_file_no=None, filename=None):
    if curr_file_no:
        filename = "./index_files/temp_index" + str(curr_file_no) + ".pkl"
    file_obj = open(filename, "wb")
    return file_obj


def sort_list(unsorted_list):
    return sorted(unsorted_list, key=lambda x: (x[0], x[1]))


def write_to_file(index_obj, curr_list):
    for entry in curr_list:
        pickle.dump(entry, index_obj, pickle.HIGHEST_PROTOCOL)


def find_smallest(obj_list):
    smallest = ()
    small_ptr = None  # stores the file pointer containing the smallest tuple.
    for obj, ptr in obj_list:
        if not smallest or obj[0] < smallest[0]:
            smallest = obj
            small_ptr = ptr
        elif obj[0] == smallest[0] and obj[1] < smallest[1]:
            smallest = obj
            small_ptr = ptr
    obj_list.remove((smallest, small_ptr))
    try:
        new_obj = pickle.load(
            small_ptr
        )  # Increase the file pointer to point to next tuple
        obj_list.append((new_obj, small_ptr))
    except EOFError:
        small_ptr.close()  # Close the file if no more tuples are available.
    return (smallest, obj_list)


def assign_Id():
    """Assigns an id number to each document in the corpus"""
    id_dict = {}
    curr_id = 1
    for filename in os.listdir("corpus"):
        id_dict[curr_id] = filename
        curr_id += 1
    with open("./index_files/docId.pkl", "wb") as f:
        pickle.dump(id_dict, f, pickle.HIGHEST_PROTOCOL)


def parse_docs():
    """
    After normalization of documents, parses them to construct
    intermidiate inverted indices.

        * temp_index<no>.pkl store the intermidiate indices

    """

    # Load the id dictionary
    id_dict = {}
    with open("./index_files/docId.pkl", "rb") as f:
        id_dict = pickle.load(f)
        curr_file_no = 1
        curr_list = []

        # TODO: Normalization of documents

        for id, name in id_dict.items():
            with open("./corpus/" + name, "r") as document:
                for line in document:
                    for word in line.split():
                        curr_list.append((word.lower(), id))
                        if len(curr_list) >= BLOCK_SIZE:
                            curr_list = sort_list(
                                curr_list
                            )  # sort the list before writing to disk.
                            index_obj = open_file(curr_file_no=curr_file_no)
                            write_to_file(index_obj, curr_list)
                            curr_list = []
                            index_obj.close()
                            curr_file_no += 1
        if curr_list:
            curr_list = sort_list(curr_list)
            index_obj = open_file(curr_file_no=curr_file_no)
            write_to_file(index_obj, curr_list)
            index_obj.close()


def merge_indices():
    """ Merges the intermidiate indices using k-way merge to get an unified inverted index. """

    file_list = os.listdir("index_files")
    temp_index_obj = open_file(filename="./index_files/temp_index.pkl")
    ptrs = []  # List of file pointers for all intermidiate indices.
    curr_list = []  # Stores list to tuples to be written to the unified index.
    obj_list = []  # List of (tuple,ptr) pair for every file.
    for filename in file_list:
        if filename != "docId.pkl" and filename != "index.pkl":
            ptrs.append(open("./index_files/" + filename, "rb"))
    for ptr in ptrs:
        obj = pickle.load(ptr)
        obj_list.append((obj, ptr))

    # Until all intermidiate indices are parsed , find smallest and write to final index.
    while obj_list:
        req_obj, obj_list = find_smallest(obj_list)
        curr_list.append(req_obj)
        if len(curr_list) > BLOCK_SIZE:
            write_to_file(temp_index_obj, curr_list)
            curr_list = []
    if curr_list:
        write_to_file(temp_index_obj, curr_list)
    temp_index_obj.close()


def construct_index():
    """
    Constructs the final index in the form of a shelf
    where the key is each term in the corpus and the value is
    a list of tuples containtng the docId and the respective term frequency.
    """

    index_obj = shelve.open("./index_files/index.db")
    with open("./index_files/temp_index.pkl", "rb") as temp_index:
        term_list = []  # List of (docId,freq) pairs for the current term.
        prev_term = ""
        prev_docId = -1
        freq = 0  # Frequency value for a term in a particular document.
        while True:
            try:
                term, docId = pickle.load(temp_index)
                if term == prev_term:
                    if docId == prev_docId:
                        freq += 1
                    else:  # new docId for same term.
                        if prev_docId != -1:
                            term_list.append((prev_docId, freq))
                        prev_docId = docId
                        freq = 1
                else:  # new term.
                    if prev_term != "":
                        term_list.append((prev_docId, freq))
                        index_obj[prev_term] = term_list
                    prev_term = term
                    prev_docId = docId
                    freq = 1
                    term_list = []
            except EOFError:
                term_list.append((prev_docId, freq))
                index_obj[prev_term] = term_list
                index_obj.close()
                break


# Temporary function to print pickle files. To be removed later.
def display():
    with open("./index_files/temp_index.pkl", "rb") as openfile:
        while True:
            try:
                print(pickle.load(openfile))
            except EOFError:
                break


if __name__ == "__main__":
    assign_Id()
    parse_docs()
    merge_indices()
    construct_index()
