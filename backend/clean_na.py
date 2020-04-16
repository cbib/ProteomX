#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski


"""
Remove proteins with number of NA above specified threshold
"""

import argparse
import logging.config
import os
import pandas as pd
import helpers as h
import paths
import functions_preprocessing as fp


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", "-i", help='Input file (csv)')
    parser.add_argument("--output_file_complete", "-oc", help='File (csv) with additional column with % nan values per '
                                                              'protein and group')
    parser.add_argument("--output_file_filtered", "-of", help='File (csv) with only included proteins')
    parser.add_argument("--project", "-p", help='Project name')
    parser.add_argument("--version", "-v", help='Analysis version name')

    args = parser.parse_args()
    return args


def get_groups(data_structure, values_cols_prefix):
    """
    Returns list of strings that describe the beginning of values column to select.
        Example: ['VAL_Patient', 'VAL_Control']
    # TODO : move to helpers.py
    """

    # +1 for all data columns prefix (ex: 'VAL')
    depth = len(rule_params['clean_na']['on']) + 1
    list_group_prefix = h.dict_to_list(data_structure, depth, values_cols_prefix, [])

    return list_group_prefix


if __name__ == "__main__":
    args = get_args()
    rule_params = h.load_json_parameter(args.project, args.version)
    filename = h.filename(args.input_file)
    data_structure = h.load_json_data(args.project, args.version, filename)

    logpath = os.path.join(paths.global_root_dir, paths.global_data_dir, args.project, args.version, 'log/remove_lines_na.log')
    logger = h.get_logger(logpath)

    data_df = pd.read_csv(args.input_file, header=0, index_col=None)
    values_cols_prefix = rule_params['all']['values_cols_prefix']

    # NaN per protein and per group
    group_prefix = get_groups(data_structure, values_cols_prefix)

    result_df, stats_per_groups = fp.na_per_group(data_df,
                                                  group_prefix,
                                                  values_cols_prefix)

    result_df = fp.flag_row_with_nas(result_df, stats_per_groups, rule_params['clean_na']['max_na_percent_proteins'])

    # NaN per samples
    stats_per_sample = fp.na_per_samples(data_df, values_cols_prefix, rule_params["clean_na"]["max_na_percent_samples"])

    # create json with information on % of NaN
    out = os.path.join(paths.global_root_dir, paths.global_data_dir,
                       args.project, args.version, 'no_na', rule_params["clean_na"]["output_json"])
    fp.export_json_sample(stats_per_sample, out, values_cols_prefix)

    # filter dataframe for following analysis
    filtered_df = fp.remove_flagged_rows(result_df, 'exclude_na', 1)
    filtered_df = fp.remove_flagged_samples(filtered_df, stats_per_sample['to_exclude'], rule_params)

    # Export dataframe with only proteins/samples compliant with threshold
    h.export_result_to_csv(filtered_df, args.output_file_filtered)

    # Export dataframe with all data and information on nan percentage per group and protein
    h.export_result_to_csv(result_df, args.output_file_complete)

    logging.info("Keeping " + str(len(filtered_df)) + " proteins with current parameters.")
    logging.info("Keeping " + str(len(stats_per_sample[stats_per_sample['to_exclude'] == False])) +
                 " samples with current parameters.")
