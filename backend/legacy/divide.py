#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski


"""
Divide input dataframe according to contrast matrix
"""

import argparse
import logging.config
import collections
import pandas as pd
import os
import helpers as h


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", "-i", help='Input file (csv)')
    parser.add_argument("--comparison_file", "-c")
    parser.add_argument("--output_file", "-o", help='Output file')
    parser.add_argument("--project", "-p", help='Project name')
    parser.add_argument("--version", "-v", help='Analysis version name')

    args = parser.parse_args()
    return args


# TODO condition and reference = list !
def get_comparison_data(comparison_df):
    comparisons = h.autovivify(2, list)
    #comparisons = collections.defaultdict(list)

    for i in range(comparison_df.shape[0]):
        for j in range(comparison_df.shape[1]):
            if comparison_df.iloc[i][j] == 1:

                reference = comparison_df.index[i]
                condition = comparison_df.columns[j]
                print(reference)
                print(condition)
                comparison_name = "{}_{}_vs_{}.csv".format(filename, condition, reference)
                comparisons[comparison_name]['condition'].append(condition)
                comparisons[comparison_name]['reference'].append(reference)

    return comparisons


def get_base_df(rule_params):
    metadata_col = data_df.filter(items=rule_params["all"]["metadata_col"])
    supplementary_col = pd.DataFrame()

    for supp_col in rule_params["all"]["metadata_col"]:
        supplementary_col = pd.concat([supplementary_col, data_df.filter(regex=supp_col)], axis=1)

    base_df = pd.concat([metadata_col, supplementary_col], axis=1)

    return base_df


def subset_df_for_each_comparison(data_df, base_df, comparisons):

    for comparison in comparisons.keys():

        reference_abundance_col_name = rule_params["all"]["abundance_col_prefix"] + comparisons[comparison]["reference"][0]
        reference_abundances_col = data_df.filter(regex=reference_abundance_col_name)
        reference_abundances_col = reference_abundances_col.add_suffix('_reference')

        condition_abundance_col_name = rule_params["all"]["abundance_col_prefix"] + comparisons[comparison]["condition"][0]
        condition_abundances_col = data_df.filter(regex=condition_abundance_col_name)

        result_df = pd.concat([base_df, reference_abundances_col, condition_abundances_col], axis=1)

        output_result = os.path.dirname(args.output_file), '{}.csv'.format(comparison)
        print(output_result)
        result_df.to_csv(output_result)

        logger.info('Data for {} exported to csv'.format(comparison))

    return


if __name__ == "__main__":
    args = get_args()
    rule_params = h.load_json_parameter(args.project, args.version)
    filename = h.filename(args.input_file)
    data_structure = h.load_json_data(args.project, args.version, filename)

    logpath = os.path.join(rule_params['all']['logpath'], 'divide.log')
    logger = h.get_logger(logpath)

    data_df = pd.read_csv(args.input_file, header=0, index_col=0)
    logger.info('{} proteins to analyse.'.format(len(data_df)))

    comparison_df = pd.read_csv(args.comparison_file, index_col=0, header=0)

    comparisons = get_comparison_data(comparison_df)
    base_df = get_base_df(rule_params)
    subset_df_for_each_comparison(data_df, base_df, comparisons)
