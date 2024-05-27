#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski


"""
Clean file from protein which : are not master protein and/or are defined by less than x uniques peptides and/or
are considered as contaminant and/or present no values at all, as defined in a config file
"""

import argparse
import pandas as pd
import os
import helpers as h
import paths
import functions_preprocessing as fpreprocessing


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", "-i", help='Input file (csv)')
    parser.add_argument("--output_file", "-o", help='Output file (csv)')
    parser.add_argument("--file_id", "-f", help='Unique ID')

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = get_args()
    rule_params = h.load_json_parameter(args.file_id)

    # get logger
    logpath = os.path.join(paths.global_data_dir, args.file_id, 'log/preprocessing.log')
    logger = h.get_logger(logpath)

    # get data
    data_df = pd.read_csv(args.input_file, header=0, index_col=None)

    logger.info('{} proteins to analyse.'.format(len(data_df)))

    # apply filters defined in config file
    preprocessed_df = fpreprocessing.preprocess_proteomic_data(data_df, rule_params['preprocessing'])

    logger.info(' ==> {} proteins compliant with cut-offs.'.format(len(preprocessed_df)))

    # keep only columns with abundances values and supplementary columns defined in the config file
    subset_df = fpreprocessing.subset_df(preprocessed_df,
                                         rule_params['all']['metadata_col'],
                                         rule_params['all']['values_cols_prefix'])
    # TODO : à la bonne place ?
    result_df = fpreprocessing.clean_null_row(subset_df, rule_params['all']['values_cols_prefix'])

    logger.info('{} proteins with enough values have been kept.'.format(len(result_df)))

    h.export_result_to_csv(result_df, args.output_file)
