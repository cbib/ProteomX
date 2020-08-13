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
import numpy as np
import helpers as h
import matplotlib.pyplot as plt
import functions_quality_check as fqc
import paths


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", "-i", help='Input file (csv)')
    parser.add_argument("--output_file_complete", "-oc", help='File (csv) with additional column with % nan values per '
                                                              'protein and group')
    parser.add_argument("--output_file_filtered", "-of", help='File (csv) with only included proteins')
    parser.add_argument("--output_file_figure", "-ofig", help='Histogram (png)')
    parser.add_argument("--file_id", "-f", help='Unique ID')

    args = parser.parse_args()
    return args


def get_groups(data_structure, values_cols_prefix):
    """
    Returns list of strings that describe the beginning of values column to select.
        Example: ['VAL_Patient', 'VAL_Control']
    # TODO : move to helpers.py
    """

    # +1 for all data columns prefix (ex: 'VAL')
    depth = len(rule_params['missing_values']['on']) + 1
    list_group_prefix = h.dict_to_list(data_structure, depth, values_cols_prefix, [])

    return list_group_prefix


def plot_CV(df, output_fig, bins, threshold):
    CV_col = df.filter(regex = 'CV_')
    for col in CV_col:
        plot_name = col.split('_')[2] #ex : vescalagine
        toplot = df[col].dropna()
        plt.hist(np.array(toplot), bins=bins)
        plt.xlabel('CV values')
        plt.ylabel('proteins #')
        if threshold:
            plt.axvline(threshold, color='k', linestyle='dashed', linewidth=1)
        plt.title('CV ' + plot_name)
        output_png = output_fig + '_histogramm_' + plot_name + '.png'
        plt.savefig(output_png)
        plt.close()



if __name__ == "__main__":
    args = get_args()
    rule_params = h.load_json_parameter(args.file_id)
    filename = h.filename(args.input_file)
    data_structure = h.load_json_data(args.file_id, filename, rule_params['all']['divide'])

    logpath = os.path.join(paths.global_data_dir, args.file_id, 'log/CV.log')
    logger = h.get_logger(logpath)

    data_df = pd.read_csv(args.input_file, header=0, index_col=None)

    # parameters
    values_cols_prefix = rule_params['all']['values_cols_prefix']

    # Compute CV per protein and per group
    group_prefix = get_groups(data_structure, values_cols_prefix)

    if rule_params['all']['divide']:
        group_prefix = h.remove_absent_groups(data_df, group_prefix, values_cols_prefix)

    result_df, stats_per_groups = fqc.cv_per_group(data_df, group_prefix, values_cols_prefix)
    print(rule_params['CV']['threshold'])
    result_df = fqc.flag_row_inf(result_df, stats_per_groups, rule_params['CV']['threshold'], 'CV')

    if rule_params['CV']['keep_specific']:
        result_df = fqc.keep_specific_proteins_cv(result_df, 'CV_', rule_params['CV']['threshold'])

    # filter dataframe for following analysis
    # remove row to discard
    filtered_df = fqc.remove_flagged_rows(result_df, 'exclude_CV', 1)

    # Export dataframe with only proteins compliant with threshold
    h.export_result_to_csv(filtered_df, args.output_file_filtered)

    # Export dataframe with all data and information on nan percentage per group and protein
    h.export_result_to_csv(result_df, args.output_file_complete)

    # plot histograms results
    plot_CV(result_df, args.output_file_figure, bins=150, threshold=rule_params['CV']['threshold'])

    logging.info("Keeping " + str(len(filtered_df)) + " proteins with current parameters.")
