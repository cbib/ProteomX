#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski


"""
Input:
    - csv file with proteomics data.
    - mapping file: each line is a sample. For each sample, the mapping file provides name of the relevant column in the
     proteomics data file, and metadata such as the group it belongs to, or additional groups or clinical features.
Returns:
    - proteomics data file with modified column names: relevant abundance columns are labelled with user sample names or
    automatically generated sample name from the mapping file
    - JSON file with information used for column relabelling as dictionary.
"""

import os
import argparse
import pandas as pd
import logging.config
import helpers as h
import paths
import functions_preprocessing as fpreprocessing


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", "-i", help='Input file (csv) with proteomics data.')
    parser.add_argument("--output_file", "-o", help='Output file (csv) with proteomics data.')
    parser.add_argument("--mapping_file", "-map", help="cvs file describing the samples.")
    parser.add_argument("--file_id", "-f", help='Unique identifier of the file.')

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = get_args()

    logger = h.get_logger(args.file_id, 'mapping')
    logging.info('Starting mapping step for file: ' + args.input_file)

    # get data
    data_df = pd.read_csv(args.input_file, header=0, index_col=None)

    logging.info("Proteomics data file successfully loaded.")
    mapping_df = pd.read_csv(args.mapping_file, header=0, index_col=None, sep='\t')
    logging.info("Mapping file successfully loaded.")

    # get parameters
    file_name = h.filename(args.input_file)
    rule_params = h.load_json_parameter(args.file_id)
    values_cols_prefix = rule_params['all']['values_cols_prefix']
    col_for_mapping = rule_params['mapping']['col_for_mapping']
    col_label = rule_params['mapping']['col_label']

    logging.info("Parameters used:")
    logging.info("values_cols_prefix: {}".format(values_cols_prefix))
    logging.info("Mapping file column with raw labels: {}".format(col_label))
    logging.info("Mapping file columns with group to use: {}".format(col_for_mapping))

    # rename columns with abundances values in the data frame based on metadata in the mapping df
    result_df = fpreprocessing.rename_col_abundance_withjson(mapping_df, data_df, values_cols_prefix, col_for_mapping,
                                                             col_label)

    # build json corresponding to new column name
    json_for_groups = "metadata_{}.json".format(file_name)
    path_to_json = os.path.join(paths.global_data_dir, args.file_id, json_for_groups)
    d = fpreprocessing.build_json(mapping_df, path_to_json, col_for_mapping)

    # export results
    h.export_result_to_csv(result_df, args.output_file)
