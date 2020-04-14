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
            reduced_df = reduction_row_by_group(df, ['Proteomic'])
        for protein in df[subset].index.values:
            subset_values = np.array(df[subset].iloc[protein].map(lambda x: locale.atof(x) if type(x) == str else x))  # apply(atof))
            reduced_abundances = subset_values / np.nanstd(subset_values, ddof = ddof)
            reduced_df.loc[protein, subset] = reduced_abundances

        #TODO : necessary ?
        #reduced_df[subset] = reduced_df[subset].add_prefix('Reduced_')

    return reduced_df


def reduction_row_by_group(input_df, metadata_col):
    abundancies = input_df.filter(regex='VAL')
    if metadata_col[0] == 'Proteomic': #args : nargs '+' => list
        input_df_metadata = input_df.filter(items=['Accession', 'Description'])
    else:
        input_df_metadata = pd.DataFrame(index=input_df.index)
        for i in range(len(metadata_col)):
            input_df_metadata = input_df_metadata.join(input_df[metadata_col[i]])
    #input_df_abundance_rank = input_df.filter(regex = 'Rank_*')


    name_ab = []
    for col in abundancies:
        col_red = '_'.join(col.split('_')[:-1])
        name_ab.append(col_red)
    unique_name_abundance = list(set(name_ab))
    print(unique_name_abundance)
    #other_col_to_keep = pd.concat([input_df_metadata, input_df_abundance_rank], axis=1)
    other_col_to_keep = pd.concat([input_df_metadata], axis=1)

    cond1  = [ x for x in abundancies if unique_name_abundance[0] in x ]
    cond2 = [x for x in abundancies if unique_name_abundance[1] in x]

    abundancies_red_1 = pd.DataFrame(columns=cond1, index=abundancies.index.values)
    abundancies_red_2 = pd.DataFrame(columns=cond2, index=abundancies.index.values)
    for protein in abundancies.index.values:
        cond1_abundancies = np.array(input_df.loc[protein][cond1].map(lambda x: atof(x) if type(x) == str else x))
        reduced_abundancies_cond1 = cond1_abundancies / np.nanstd(cond1_abundancies)

        cond2_abundancies = np.array(input_df.loc[protein][cond2].map(lambda x: atof(x) if type(x) == str else x))
        reduced_abundancies_cond2 = cond2_abundancies / np.nanstd(cond2_abundancies)

        abundancies_red_1.iloc[protein] = reduced_abundancies_cond1
        abundancies_red_2.iloc[protein] = reduced_abundancies_cond2

    red_avundancies = pd.concat([abundancies_red_1, abundancies_red_2], axis=1)
    red_avundancies = red_avundancies.add_prefix('Reduced_')


    output_df = pd.concat([other_col_to_keep, red_avundancies], axis=1)
    return (output_df)

if __name__ == "__main__":
    args = get_args()
    rule_params = h.load_json_parameter(args.project, args.version)
    filename = h.filename(args.input_file)

    logpath = os.path.join(paths.global_root_dir, paths.global_data_dir, args.project, args.version, 'log/reduce_line.log')
    logger = h.get_logger(logpath)

    data_df = pd.read_csv(args.input_file, header=0, index_col=None)

    subsets = subset_data(data_df, filename)
    result_df = reduce_data(data_df, subsets)

    h.export_result_to_csv(result_df, args.output_file)