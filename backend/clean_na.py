#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski


"""
Remove dataframe rows with number of NA above specified threshold
TODO : methode pour accéder à différents valeurs de max na autorisées selon les groupes
"""

import argparse
import os
import pandas as pd
import helpers as h
import collections
import logging.config
import paths


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", "-i", help='Input file (csv)')
    parser.add_argument("--output_file", "-o", help='Output file (csv)')
    parser.add_argument("--project", "-p", help='Project name')
    parser.add_argument("--version", "-v", help='Analysis version name')

    args = parser.parse_args()
    return args


def get_groups(data_structure):
    # +1 for all data columns prefix (ex: 'VAL')
    depth = len(rule_params['clean_na']['on']) + 1
    ab_col_prefix = rule_params['all']['values_cols_prefix']
    list_group_prefix = h.dict_to_list(data_structure, depth, ab_col_prefix, [])

    return list_group_prefix


def create_dictionary(df, list_group_prefix):

    d = collections.defaultdict(dict)

    for group in list_group_prefix:
        # strip prefix shared with all other groups
        #group_name = '_'.join(group.split('_')[1:])

        # add max NA authorized
        samples_number = len(df.filter(regex=group).columns)
        max_na = get_max_na(samples_number)
        d[group]["max_na"] = max_na

        # add column to check in df
        d[group]["na_number_column"] = "na_number_{}".format(group)

    return d


def get_max_na(sample_number):
    percent_max_na = rule_params['clean_na']["max_na_percent"]
    number_max_na = sample_number * percent_max_na / 100
    return number_max_na


def compute_number_of_na(df, d):
    group_list = [*d]

    for group in group_list:
        data = df.filter(regex=group)
        kwargs = {d[group]["na_number_column"]: data.isna().sum(axis=1)}
        df = df.assign(**kwargs) # keyword in assign can't be an expression

    return df


def remove_row_with_nas(df, d):
    res = df.copy()
    print(d)
    for group in d:

        col = d[group]["na_number_column"]

        max_na = d[group]["max_na"]
        print('group : ', group)
        print('col : ', col)
        print("max_na : ", max_na)

        res = res[res[col] <= max_na]

    return res


if __name__ == "__main__":
    args = get_args()
    rule_params = h.load_json_parameter(args.project, args.version)
    filename = h.filename(args.input_file)
    data_structure = h.load_json_data(args.project, args.version, filename)

    logpath = os.path.join(paths.root_dir, paths.data_dir, args.project, args.version, 'log/remove_lines_na.log')
    logger = h.get_logger(logpath)

    data_df = pd.read_csv(args.input_file, header=0, index_col=None)

    group_prefix = get_groups(data_structure)
    d_na = create_dictionary(data_df, group_prefix)
    result_df = compute_number_of_na(data_df, d_na)
    result_df = remove_row_with_nas(result_df, d_na)

    if rule_params['clean_na']['keep_specific']:
        pass

    logging.info("Keeping " + str(len(result_df)) + " proteins.")

    coltodrop = result_df.filter(regex='na_number_')
    result_df = result_df.drop(coltodrop, axis=1)

    h.export_result_to_csv(result_df, args.output_file)

