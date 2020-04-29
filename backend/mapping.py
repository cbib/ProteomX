#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski


"""
Take a data frame as input and change column names according to mapping file ; return also a json file with mapping
data as dictionary
"""


import argparse
import pandas as pd
import os
import logging.config
import helpers as h
import paths
import functions_preprocessing as fpreprocessing


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", "-i", help='Input file (csv)')
    parser.add_argument("--output_file", "-o", help='Output file (csv)')
    parser.add_argument("--mapping_file", "-map")
    parser.add_argument("--file_id", "-f", help='Unique ID')

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = get_args()
    filename = h.filename(args.input_file)
    rule_params = h.load_json_parameter(args.file_id)

    logpath = os.path.join(paths.global_data_dir, args.file_id, 'log/mapping.log')
    logger = h.get_logger(logpath)
    logging.info('Starting mapping file: ' + args.input_file)

    # get data
    data_df = pd.read_csv(args.input_file, header=0, index_col=None)
    mapping_df = pd.read_csv(args.mapping_file, header=0, index_col=None)

    # get parameters
    values_cols_prefix = rule_params['all']['values_cols_prefix']
    col_for_mapping = rule_params['mapping']['col_for_mapping']
    col_label = rule_params['mapping']['col_label']

    # rename columns with abundances values in the data frame based on metadata in the mapping df
    result_df = fpreprocessing.rename_col_abundance_withjson(mapping_df, data_df, values_cols_prefix, col_for_mapping, col_label)

    # build json corresponding to new column name
    json_for_groups = "metadata_{}.json".format(filename)
    path_to_json = os.path.join(paths.global_data_dir, args.file_id, json_for_groups)
    d = fpreprocessing.build_json(mapping_df, path_to_json, col_for_mapping)

    # export results
    h.export_result_to_csv(result_df, args.output_file)
