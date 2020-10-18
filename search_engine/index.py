"""
*Index Generator*

    * Assigns a docID to each document in the corpus.
    * Parses The documents to create intermediate inverted indices.
    * Uses Block Sort and Merge Algorithm to generate an unified inverted index.
    * Finally, creates a shelf containing term as key and list of (docId,freq) as value.

"""

import pickle
import shelve
import os
import sys
import pathlib
from .query_processing import process_string
from .settings import BLOCK_SIZE


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


def assign_docId():
    """Assigns an id number to each document in the corpus"""
    print("Assigning Doc ID")
    id_dict = {}
    curr_id = 1
    file_list = os.listdir("corpus")
    if not file_list:
        raise Exception("Error- Corpus is Empty! Add some documents.")
    for filename in file_list:
        print(curr_id, end="\r")
        id_dict[curr_id] = filename
        curr_id += 1
    try:
        os.mkdir("./index_files")
    except OSError:
        pass  # Folder Already Exists
    with open("./index_files/docId.pkl", "wb") as f:
        pickle.dump(id_dict, f, pickle.HIGHEST_PROTOCOL)
    print("Done assigning Doc ID")


def parse_docs():
    """
    After normalization of documents, parses them to construct
    intermediate inverted indices.

        * temp_index<no>.pkl store the intermediate indices

    """
    print("Parsing Docs")
    # Load the id dictionary.
    id_dict = {}
    with open("./index_files/docId.pkl", "rb") as f:
        id_dict = pickle.load(f)
        curr_file_no = 1
        # Stores (termId,docId) pairs for current intermediate index.
        curr_list = []
        id_dict_len = len(id_dict)
        for docId, name in id_dict.items():
            print(f"Processing {docId} of {id_dict_len}", end="\r")
            # Get document text as String.
            doc_text = pathlib.Path("./corpus/" + name).read_text().replace("\n", " ")

            # Get list of terms in document after normalization.
            doc_terms = process_string(doc_text)

            for term in doc_terms:
                curr_list.append((term, docId))
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
    print("Done parsing Docs")


def merge_indices():
    """ Merges the intermediate indices using k-way merge to get an unified inverted index. """

    print("Merging indices")
    file_list = os.listdir("index_files")
    temp_index_obj = open_file(filename="./index_files/temp_index.pkl")
    ptrs = []  # List of file pointers for all intermediate indices.
    curr_list = []  # Stores list to tuples to be written to the unified index.
    obj_list = []  # List of (tuple,ptr) pair for every file.
    for filename in file_list:
        if filename not in ["docId.pkl", "termId.pkl", "temp_index.pkl", "index.db"]:
            ptrs.append(open("./index_files/" + filename, "rb"))
    for ptr in ptrs:
        obj = pickle.load(ptr)
        obj_list.append((obj, ptr))

    # Until all intermediate indices are parsed , find smallest and write to unified index.
    slash_value = 0
    while obj_list:
        if slash_value:
            print("Merging /", end="\r")
        else:
            print("Merging \\", end="\r")
        slash_value = not slash_value
        req_obj, obj_list = find_smallest(obj_list)
        curr_list.append(req_obj)
        if len(curr_list) > BLOCK_SIZE:
            write_to_file(temp_index_obj, curr_list)
            curr_list = []
    if curr_list:
        write_to_file(temp_index_obj, curr_list)
    temp_index_obj.close()
    print("Done Merging indices")


def construct_index():
    """
    Constructs the final index in the form of a shelf
    where the key is each term in the corpus and the value is
    a dictionary containing docId,freq as the key-value pairs.
    """

    print("Starting to Index")
    index_obj = shelve.open("./index_files/index.db")
    with open("./index_files/temp_index.pkl", "rb") as temp_index:
        # Dict of docId,freq as key-value pairs for the current term.
        term_dict = {}
        prev_term = ""
        prev_docId = -1
        freq = 0  # Frequency value for a term in a particular document.
        slash_value = 0
        while True:
            try:
                term, docId = pickle.load(temp_index)
                if slash_value:
                    print("Indexing /", end="\r")
                else:
                    print("Indexing \\", end="\r")
                slash_value = not slash_value
                if term == prev_term:
                    if docId == prev_docId:
                        freq += 1
                    else:  # new docId for same term.
                        if prev_docId != -1:
                            term_dict[prev_docId] = freq
                        prev_docId = docId
                        freq = 1
                else:  # new term.
                    if prev_term != "":
                        term_dict[prev_docId] = freq
                        index_obj[prev_term] = term_dict
                    prev_term = term
                    prev_docId = docId
                    freq = 1
                    term_dict = {}
            except EOFError:
                term_dict[prev_docId] = freq
                index_obj[prev_term] = term_dict
                index_obj.close()
                break

    # Delete temporary files
    print("Deleting Temporary Files")
    no_files = len(os.listdir("./index_files")) - 2
    count = 1
    for file_name in os.listdir("./index_files"):
        if file_name[:10] == "temp_index":
            print(f"Deleting file {count} of {no_files}", end="\r")
            os.remove("./index_files/" + file_name)
            count += 1
    print("Done Deleting Temporary files")


# Temporary function to print pickle files. To be removed later.
def display(final_index=True):
    if final_index:
        ptr = shelve.open("./index_files/index.db")
        for key in ptr.keys():
            print(key, ptr[key], sep=" ")
        ptr.close()
        return
    else:
        with open("./index_files/temp_index.pkl", "rb") as openfile:
            while True:
                try:
                    print(pickle.load(openfile))
                except EOFError:
                    break


def start_indexing():
    assign_docId()
    parse_docs()
    merge_indices()
    construct_index()
    # Uncomment during development.
    # display()
