import javalang
import os
# import shutil
# import re
# import sys      # used for system exceptions
import inspect  # used yo check objects for all methods
import nodeutil # contains util methods
import constants
import time  # used to record how long methods take to run
import itertools
import tkinter as tk
import util
# import csv

constants.MIN_LINE_MATCHES = 4  # The number of different lines that a match has to be found on


def gst(tree_a, tree_b):
    """ Returns a score given 2 files"""
    treelist_a = nodeutil.convert_to_list(tree_a)
    treelist_b = nodeutil.convert_to_list(tree_b)
    tiles = []
    previousLine = 0

    currentLineMatches = 0
    while True:
        max_match = constants.MIN_MATCH_LENGTH
        matches = []
        unmarked_tokens_a = [x for x in treelist_a if not x.marked]
        unmarked_tokens_b = [x for x in treelist_b if not x.marked]
        for indexA, tokenA in enumerate(unmarked_tokens_a):
            for indexB, tokenB in enumerate(unmarked_tokens_b):
                current_line_num = []
                j = 0   # used as a counter to extend matches
                match_list = []
                while unmarked_tokens_a[indexA + j] == unmarked_tokens_b[indexB + j]:
                    # print("why this is happening")
                    tuple = (unmarked_tokens_a[indexA + j], unmarked_tokens_b[indexB + j])

                    # checking if the tokens line numbers have already been recorded. If they haven't then they are
                    # recorded
                    if (tuple[0].line, tuple[1].line) not in current_line_num:
                        current_line_num.append((tuple[0].line, tuple[1].line))

                    match_list.append(tuple)
                    j += 1

                    #   if the next iteration would cause a loop out of bounds exception
                    if (indexA + j) >= len(unmarked_tokens_a) or (indexB + j) >= len(unmarked_tokens_b):
                        break

                if j == max_match and len(current_line_num)>constants.MIN_LINE_MATCHES:
                    matches.append(match_list)
                elif (j>max_match) and len(current_line_num)>constants.MIN_LINE_MATCHES:
                    matches = []
                    matches.append(match_list)
                    max_match = j
        for match in matches:
            for i in range(0,len(match)):
                match[i][0].marked = True
                match[i][1].marked = True
            tiles.append(match)

        if max_match <= constants.MIN_MATCH_LENGTH:
            break

    lengthA = len(treelist_a)
    lengthB = len(treelist_b)
    count = 0

    for match in tiles:
        for token in match:
            count += 1
    score = (2 * count) / (lengthA + lengthB)
    return score

def main(source_dir, output_dir, outbox):
    start = time.time()
    try:
        javadir = os.listdir(source_dir)  # directory where all java files will be stored
    except FileNotFoundError as inst:
        util.print_tk(outbox, "Incorrect Directory Entered\n")
        return 0
    util.print_tk(outbox, "Reading Files..\n")

    files = []
    error_msgs = {}
    faulty_files = []
    tree_map = {}  # Stores all trees created from the all the files in a separate dictionary

    for filename in javadir:
        address = source_dir + "/" + str(filename)
        try:
            # check if extention is java
            file = open(address, "r")
            # files[str(filename)] = file
            files.append(str(filename))

            text = "".join(file.readlines())

            tree = javalang.parse.parse(text)
            tree_map[filename] = tree

        except FileNotFoundError:
            util.print_tk(outbox, "File " + str(filename) + " was not found\n")
        except javalang.parser.JavaSyntaxError as inst:
            util.print_tk(outbox, str(filename) + " couldn't compile\n")
            faulty_files.append(filename)
        except Exception as inst:
            error_msgs[filename] = str(inst)

    #  2 loops used to go through all pairings of files and perform a structure based method on all of then_statement
    #  The scores are stored in the score map
    score_map = {}

    # -------------------  Greedy String Tiling  ---------------------#
    for filename_1, filename_2 in itertools.combinations(tree_map, 2):

        if util.STOPFLAG:
            break      # Used to exit function

        # the next section ensures that the key for 2 trees in the score map will be the same no matter
        # which tree is tree_1 / tree_2
        hash1 = hash(filename_1)
        hash2 = hash(filename_2)
        if hash1 >= hash2:
            key = (filename_1, filename_2)
        else:
            key = (filename_2, filename_1)

        tree_1 = tree_map[filename_1]
        tree_2 = tree_map[filename_2]

        score = gst(tree_1, tree_2) * 100
        str_score = '%.2f' % score  # rounds score too 2 dp to display

        util.print_tk(outbox, "Compared " + filename_1 + "-" + filename_2 + ": " + str_score + "% \n")
        score_map[key] = score

    # ----------------  End of Greedy String Tiling  ----------------#
    end = time.time()  # stop recording time

    util.print_tk(outbox, "Execution time: " + str(end - start) + " seconds\n")
    if util.STOPFLAG:
        util.print_tk(outbox, "Comparisons interrupted\n")
        util.STOPFLAG = False
    else:
        util.print_tk(outbox, "--Finished Comparisons--\n")