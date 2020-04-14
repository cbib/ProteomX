#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski

"""
Apply reduction of abundance values for each protein per line or groups of samples
# TODO : pouvoir changer de méthode ?
"""

import argparse
import pandas as pd
import os
import locale
import numpy as np
import logging.config
import paths
import helpers as h
import utils


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", "-i", help='Input file (csv)')
    parser.add_argument("--output_file", "-o", help='Output file (csv)')
    parser.add_argument("--project", "-p", help='Project name')
    parser.add_argument("--version", "-v", help='Analysis version name')

    args = parser.parse_args()
    return args


def subset_data(df, filename):
    # TODO: pas beosin 'initialiser liste ?
    subsets = []
    reduction_param = rule_params['reduce']['subsets']

    if reduction_param == "all_data":
        abundance_values_col = list(df.filter(regex=rule_params['all']['values_cols_prefix']))
        subsets.append(abundance_values_col)

    elif reduction_param == "group":
        abundance_values_col = h.get_ab_col(filename, "group", rule_params)
        subsets.append(abundance_values_col)

    elif reduction_param == "sample":
        #abundance_values_col = h.get_ab_col(filename, "sample", rule_params)
        #subsets.append(abundance_values_col)
        subsets.append("sample")
    elif reduction_param == "custom":
        #TODO : groupe particuliers d'échantillons définis dans config_file ou csv ? Intérêt ?
        pass

    else:
        logging.error('No reduction subsets defined')

    return subsets


def reduce_data(df, subsets):
    reduced_df = df.copy()
    ddof = rule_params["reduce"]["ddof"]
    for subset in subsets:
        if subset == "sample":
            reduced_df = utils.reduction_row_by_group(df, ['Proteomic'])
        for protein in df[subset].index.values:
            subset_values = np.array(df[subset].iloc[protein].map(lambda x: locale.atof(x) if type(x) == str else x))  # apply(atof))
            reduced_abundances = subset_values / np.nanstd(subset_values, ddof = ddof)
            reduced_df.loc[protein, subset] = reduced_abundances

        #TODO : necessary ?
        #reduced_df[subset] = reduced_df[subset].add_prefix('Reduced_')

    return reduced_df


if __name__ == "__main__":
    args = get_args()
    rule_params = h.load_json_parameter(args.project, args.version)
    filename = h.filename(args.input_file)

    logpath = os.path.join(paths.root_dir, paths.data_dir, args.project, args.version, 'log/reduce_line.log')
    logger = h.get_logger(logpath)

    data_df = pd.read_csv(args.input_file, header=0, index_col=None)

    subsets = subset_data(data_df, filename)
    result_df = reduce_data(data_df, subsets)

    h.export_result_to_csv(result_df, args.output_file)