"""
*Index Generator*

    * Assigns a docID to each document in the corpus.
    * Parses The documents to create intermidiate inverted indices.
    * Uses Block Sort and Merge Algorithm to generate the unified inverted index.

"""

import pickle
import os
from settings import INDEX_SIZE


def open_file(curr_file_no):
    """
    Opens a new pickle file

       * accepts an integer - current file number  as operand
       * returns the file object for newly opened file

    """

    filename = "./index_files/temp_index" + str(curr_file_no) + ".pkl"
    file_obj = open(filename, "wb")
    return file_obj


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
        index_obj = open_file(curr_file_no)

        # TODO: Normalization of documents

        for id, name in id_dict.items():
            with open("./corpus/" + name, "r") as document:
                for line in document:
                    for word in line.split():
                        pickle.dump((word, id), index_obj, pickle.HIGHEST_PROTOCOL)
                        if os.path.getsize(index_obj.name) >= INDEX_SIZE:
                            index_obj.close()
                            curr_file_no += 1
                            index_obj = open_file(curr_file_no)


def assign_Id():
    id_dict = {}
    curr_id = 1
    for filename in os.listdir("corpus"):
        id_dict[curr_id] = filename
        curr_id += 1
    with open("./index_files/docId.pkl", "wb") as f:
        pickle.dump(id_dict, f, pickle.HIGHEST_PROTOCOL)


# temporary function to print pickle files. To be removed later.
def display():
    file_list = os.listdir("index_files")
    for filename in file_list:
        with (open("./index_files/" + filename, "rb")) as openfile:
            while True:
                try:
                    print(pickle.load(openfile))
                except EOFError:
                    break
