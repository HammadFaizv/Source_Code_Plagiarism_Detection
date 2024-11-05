import javalang
import os
import sys  # used for system exceptions
import time  # used to record how long methods take to run
import itertools    # used for combinations
import util
import pickle
import operator
import attributes
import constants
import math
from results import Result
import config
from collections import defaultdict

from gst.quickGST import main as quick_gst

from sklearn.ensemble import RandomForestRegressor
# from sklearn.model_selection import train_test_split 
# from sklearn.neighbors import KNeighborsClassifier 

import pandas as pd
import numpy as np


def create_df(lizard_data, lizard_col, file_data, file_columns, outbox):

    util.print_tk(outbox, "Creating Dataframes\n")
    lizard_df = pd.DataFrame(lizard_data, columns=lizard_col)
    lizard_df.set_index("filename", inplace=True)

    raw_tree_df = pd.DataFrame(file_data, columns=file_columns)
    raw_tree_df.set_index("filename", inplace=True)

    attribute_df = pd.concat([lizard_df, raw_tree_df], axis=1, sort=True).astype(float)
    attribute_df.reset_index(inplace=True)   # gets rid of filename index
    attribute_df.rename(columns={"index": "filename"}, inplace=True)

    full_df_col = list(attribute_df)     # gets the column values from full dataframe
    full_df_rows = attribute_df.values.tolist()   # getting all the rows from the full dataframe

    util.print_tk(outbox, "Computing combinations\n")
    # Gets all combinations of the attributes of each file
    final_df_list = []
    for file1_att, file2_att in itertools.combinations(full_df_rows, 2):
        if util.STOPFLAG:
            break      # Used to exit function
        filename_1 = file1_att[0]
        filename_2 = file2_att[0]
        # Sets an order to the filenames to make it easier to access specific rows later from the dataframe
        filenames = [filename_1, filename_2] if filename_1 < filename_2 else [filename_2, filename_1]
        data = []
        for i, j in zip(file1_att[1:], file2_att[1:]):
            if i != 0 or j != 0:
                data.append(abs(i - j))
            else:
                data.append(np.nan)
        final_df_list.append(filenames + data)

    # Adds column headings to rows and creates a final dataframe
    final_df_col = ["filename_1_", "filename_2_"] + full_df_col[1:]
    final_df = pd.DataFrame(final_df_list, columns=final_df_col)
    final_df.set_index(['filename_1_', 'filename_2_'], inplace=True)
    # final_df = final_df.reindex(sorted(final_df.columns), axis=1)   # reorders columns based on alphabetic order
    return final_df


def main(source_dir, output_dir, outbox):

    source_dir = source_dir.split("/")[-1] + "/"
    print(source_dir)
    start = time.time()  # #start recording how long program takes
    try:
        javadir = os.listdir(source_dir)  # directory where all java files will be stored
    except FileNotFoundError as inst:
        util.print_tk(outbox, "Incorrect Directory Entered\n")
        return 0

    util.print_tk(outbox, "Reading Files..\n")

    files = []
    file_map = {}
    tree_map = {}  # Stores all trees created from the all the files in a separate dictionary
    lizard_data, lizard_col = attributes.lizard_analysis(source_dir)
    file_data = []
    file_columns = ["filename"] + attributes.get_raw_col() + attributes.get_tree_col()

    util.print_tk(outbox, "Calculating attributes for files...\n")

    for filename in javadir:
        print(filename)
        if filename[-5:] != ".java":    # Ensures that the current file is a java file
            pass
        address = source_dir + str(filename)
        try:

            file = open(address, "r")
            # files[str(filename)] = file
            files.append(str(filename))

            temp = [source_dir + filename]
            text = "".join(file.readlines())
            file_map[filename] = text
            data_raw = attributes.calculate_raw_attributes(text)

            tree = javalang.parse.parse(text)
            data_tree = attributes.calculate_tree_attributes(tree)

            temp = temp + data_raw + data_tree
            file_data.append(temp)

        except FileNotFoundError:
            util.print_tk(outbox, "File " + str(filename) + " was not found\n")
        except javalang.parser.JavaSyntaxError as inst:
            util.print_tk(outbox, str(filename) + " couldn't compile\n")

    distro_map = defaultdict(int)   # Map used to store the distribution of scores

    # Load Random Forest Model
    rf_classifier = pickle.load(open(config.get_rf_model_path(), 'rb'))

    lizard_df = pd.DataFrame(lizard_data, columns=lizard_col)
    lizard_df.set_index("filename", inplace=True)

    raw_tree_df = pd.DataFrame(file_data, columns=file_columns)
    raw_tree_df.set_index("filename", inplace=True)

    attribute_df = pd.concat([lizard_df, raw_tree_df], axis=1, sort=True).astype(float)
    attribute_df.reset_index(inplace=True)  # gets rid of filename index
    attribute_df.rename(columns={"index": "filename"}, inplace=True)
    # attribute_df.drop('num_type4_var', axis=1, inplace=True)

    full_df_col = list(attribute_df)  # gets the column values from full data frame
    full_df_rows = (
        attribute_df.values.tolist()
    )
    score_map = quick_gst(source_dir, None, None) # takes the most amount of time
    
    final_df_list = []

    final_df_col = (
        ["filename_1_", "filename_2_"]
        + full_df_col[1:]
        + ["gst_sim", "euclid_dist", "cosine_dist"]
    )

    size_count = 0  # Used as a counter to ensure the length of the list doesnt exceed the available size in memory

    n = len(attribute_df)
    total_comparisons = (n * (n - 1)) / 2
    ten_percent = math.ceil(total_comparisons / 10)
    progress_counter = 0
    progress_iter = 0

    for file1_att, file2_att in itertools.combinations(full_df_rows, 2):
        progress_counter += 1
        if progress_counter >= ten_percent:
            progress_counter = 0
            progress_iter += 10
            print("Completed " + str(progress_iter) + "%")

        filename_1 = file1_att[0].replace(source_dir, "")
        filename_2 = file2_att[0].replace(source_dir, "")

        # Sets an order to the filenames to make it easier to access specific rows later from the dataframe
        filenames = (
            [filename_1, filename_2]
            if filename_1 < filename_2
            else [filename_2, filename_1]
        )
        data = []

        # Looks through all attribute values for each file to see if there is any 0s present. If not then the difference of
        # each file is calculates( file 1 attributes - file 2 attributes).
        for i, j in zip(file1_att[1:], file2_att[1:]):
            if i == 0 and j == 0:
                data.append(np.nan)
            else:
                temp = abs(i - j)
                if temp == 0:
                    temp -= math.sqrt(i)
                else:
                    avg = (i + j) / 2.0
                    temp -= math.log(avg)
                data.append(temp)

        # Adds the calculated greedy string tiling similarity score between files and adds them to the data list
        try:
            f1 = filename_1.replace(source_dir, "")
            f2 = filename_2.replace(source_dir, "")
            gst_sim = score_map[f1, f2] if f1 <= f2 else score_map[f2, f1]
        except KeyError as ke:
            gst_sim = 0.0
        except Exception as inst:
            gst_sim = np.nan

        data.append(gst_sim)

        # Calculating distance metrics----------------#
        euclid_dist = util.euclid_dist(file1_att[1:], file2_att[1:])
        cosine_sim = util.cosine_sim(file1_att[1:], file2_att[1:])
        # ----------------------------------------------#

        # Adding full row to the a list containing all rows
        final_df_list.append(filenames + data + [euclid_dist, cosine_sim])

        size_count += 1
    
    if len(final_df_list) == 0:
        util.print_tk(outbox, "Something went wrong no final data...\n")
    
    test_df = pd.DataFrame(final_df_list, columns=final_df_col)
    test_df.set_index(['filename_1_', 'filename_2_'], inplace=True)
    # test_df.drop(["filename_1_", "filename_2_"], axis=1, inplace=True)
    test_df = test_df.fillna(0)


    pred_rf = rf_classifier.predict_proba(test_df.values)
    # get first value from each pair
    pred_rf = pred_rf[:, 1]
    test_df['similarity'] = pred_rf * 100
    final_df = test_df[test_df['similarity'] > constants.SIMILARITY_THRESHOLD]
    final_df = final_df[['similarity']]
    final_df = final_df.reset_index()
    final_df = final_df.sort_values('similarity', ascending=False)

    score_list = final_df.values.tolist()
    # dir_length = len(source_dir)
    sorted_scores = []
    for data in score_list:
        filename1 = data[0][data[0].rfind("/") + 1:]
        filename2 = data[1][data[1].rfind("/") + 1:]
        score = int(data[2] * 100) / 100
        sorted_scores.append(((filename1, filename2), score))

        rounded_score = int(math.ceil(score / 10.0)) * 10
        distro_map[rounded_score] += 1

    sorted_distro = sorted(distro_map.items(), key=operator.itemgetter(0), reverse=True)

    end = time.time()  # stop recording time
    util.print_tk(outbox, "Execution time: " + str(end - start) + " seconds")
    if util.STOPFLAG:
        util.print_tk(outbox, "Comparisons interrupted\n")
        util.STOPFLAG = False
    else:
        util.print_tk(outbox, "--Finished Comparisons--\n")

    message = """
    These are the results computed using the application of machine learning to attribute counting. The model used for
    these scores was a trained random forest model. Each score is presented as a percentage where each percentage 
    represents the average similarity between files. This means that extending one file will not affect the score."""

    res = Result(files, message, output_dir, sorted_scores, sorted_distro, "ml", file_map)
    res.print_html()

    # h = res.get_hm()


if __name__ == "__main__":
    main('../test', '../result', None)