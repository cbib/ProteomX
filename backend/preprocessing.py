#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski


"""
Clean file from protein which : are not master protein and/or are defined by less than x uniques peptides and/or
are considered as contaminant and/or present no values at all, as defined in a config file
"""

import argparse
import pandas as pd
import numpy as np
import logging.config
import os
import helpers as h
import paths


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", "-i", help='Input file (csv)')
    parser.add_argument("--output_file", "-o", help='Output file (csv)')
    parser.add_argument("--project", "-p", help='Project name')
    parser.add_argument("--version", "-v", help='Analysis version name')

    args = parser.parse_args()
    return args


def preprocess_proteomic_data(df):
    preprocess_params = rule_params['preprocessing']
    for param in preprocess_params:
        len_df = len(df)
        if preprocess_params[param]["column_id"]:
            col = preprocess_params[param]["column_id"]

            if "to_discard" in preprocess_params[param]:
                values_to_discard = preprocess_params[param]["to_discard"]
                df = discard_values(df, values_to_discard, col)

            if "too_keep" in preprocess_params[param]:
                values_to_keep = preprocess_params[param]["to_keep"]
                df = keep_values(df, values_to_keep, col)

            if "unique" in preprocess_params[param]:
                unique = preprocess_params[param]["unique"]
                column_id = preprocess_params[param]["column_id"]
                df = df[df[column_id] == unique]

            else:
                logging.info('No values set for {} cutoff.'.format(param))

            proteins_kept = len_df - len(df)
            logging.info('Checking {}: {} proteins kept'.format(param, proteins_kept))

    return df


def discard_values(df, values_to_discard, col):
    for value in values_to_discard:
        df = df[df[col] != value]
    return df


def keep_values(df, values_to_keep, col):
    logical_filters = list()
    for value in values_to_keep:
        logical_filter = (df[col] == value)
        logical_filters.append(logical_filter)
    df = df[np.logical_or.reduce(logical_filters)]
    return df


def subset_preprocessed_df(df, metadata_col, abundance_col_prefix):
    metadata_df = df.filter(metadata_col)
    values_df = df.filter(regex=abundance_col_prefix)
    res = pd.concat([metadata_df, values_df], axis=1)
    return res


def clean_null_row(df, abundance_col_prefix):
    null_row = df.filter(regex=abundance_col_prefix).isnull().all(axis=1)
    res = df[~null_row]
    return res


if __name__ == "__main__":
    args = get_args()
    rule_params = h.load_json_parameter(args.project, args.version)

    logpath = os.path.join(paths.root_dir, paths.data_dir, args.project, args.version, 'log/preprocessing.log')
    logger = h.get_logger(logpath)

    data_df = pd.read_csv(args.input_file, header=0, index_col=None)
    logger.info('{} proteins to analyse.'.format(len(data_df)))

    preprocessed_df = preprocess_proteomic_data(data_df)
    logger.info(' ==> {} proteins compliant with cut-offs.'.format(len(preprocessed_df)))

    subset_df = subset_preprocessed_df(preprocessed_df,
                                     rule_params['all']['metadata_col'],
                                     rule_params['all']['values_cols_prefix'])

    # TODO : à la bonne place ?
    result_df = clean_null_row(subset_df, rule_params['all']['values_cols_prefix'])
    logger.info('{} proteins with enough values have been kept.'.format(len(result_df)))

    h.export_result_to_csv(result_df, args.output_file)
