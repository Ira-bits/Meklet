"""
*Index Generator*

    * Assigns a docID to each document in the corpus.
    * Parses The documents to create intermidiate inverted indices.
    * Uses Block Sort and Merge Algorithm to generate an unified inverted index.

"""

import pickle
import os
from settings import BLOCK_SIZE


# Helper functions for the Block Sort Based Indexing Algorithm -
# open_file() --> opens new index files as and when required.
# sort_list() --> sorts a given list of tuples first by term then by docID.
# write_to_file --> dumps index to disk.
# find_smallest --> returns the smallest tuple and updates object_list accordingly.


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
    """Assigns an id numbber to each document in the corpus"""
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
    index_obj = open_file(filename="./index_files/index.pkl")
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
            write_to_file(index_obj, curr_list)
            curr_list = []
    if curr_list:
        write_to_file(index_obj, curr_list)
    index_obj.close()


# Temporary function to print pickle files. To be removed later.
def display():
    with open("./index_files/index.pkl", "rb") as openfile:
        while True:
            try:
                print(pickle.load(openfile))
            except EOFError:
                break


if __name__ == "__main__":
    assign_Id()
    parse_docs()
    merge_indices()
    display()
