#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski


"""
Rank the protein based on the mean of abundance values for all replicates of one sample
TODO : only gmean available
"""

import argparse
import pandas as pd
import numpy as np
import logging.config
import os
import helpers as h
from locale import atof
import scipy.stats as stats


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", "-i", help='Input file (csv)')
    parser.add_argument("--output_file", "-o", help='Output file (csv)')
    parser.add_argument("--project", "-p", help='Project name')
    parser.add_argument("--version", "-v", help='Analysis version name')

    args = parser.parse_args()
    return args


# TODO : rename
def get_abundance_subset(data_structure, rule_params):
    # +1 for col prefix (ex: 'VAL')
    depth = len(rule_params['abundance_rank']['on']) + 1
    ab_col_prefix = rule_params['all']['abundance_col_prefix']
    abundance_col_names = h.dict_to_list(data_structure, depth, ab_col_prefix, [])
    return abundance_col_names


# TODO: return mean of empty slice (expected) ==> warnings.catch warnings ?
def compute_protein_gmean_per_subset(data_df, abundance_col_name):
    for col in abundance_col_name:
        for protein in data_df.index.values:
            protein_abundances = np.array(data_df.loc[protein, data_df.columns.str.startswith(col)].map(lambda x: atof(x) if type(x) == str else x))

            gmean_protein = stats.gmean(protein_abundances[~np.isnan(protein_abundances)])

            # first element = abundance col prefix
            subset_name = '_'.join(col.split('_')[1:])
            data_df.at[protein, 'gmean_{}'.format(subset_name)] = gmean_protein
    return data_df


def compute_protein_rank_per_subset(data_df):
    gmean_col = data_df.filter(regex='gmean_')

    for col in gmean_col:
        subset_name = '_'.join(col.split('_')[1:])
        data_df['rank_abundance_{}'.format(subset_name)] = data_df['gmean_{}'.format(subset_name)].rank(ascending=False)

    return data_df


if __name__ == "__main__":
    args = get_args()
    rule_params = h.load_json_parameter(args.project, args.version)
    filename = h.filename(args.input_file)
    data_structure = h.load_json_data(args.project, args.version, filename)

    logpath = os.path.join(rule_params['all']['logpath'], 'abundance_rank.log')
    logger = h.get_logger(logpath)

    data_df = pd.read_csv(args.input_file, header=0, index_col=0)
    print(data_df.columns.values)
    print(data_df.head())
    logger.info('{} proteins to analyse.'.format(len(data_df)))

    ab_col = get_abundance_subset(data_structure, rule_params)
    print(ab_col)
    data_df = compute_protein_gmean_per_subset(data_df, ab_col)
    result_df = compute_protein_rank_per_subset(data_df)

    try:
        result_df.to_csv(args.output_file, index=True)
        logging.info('Writing in ' + args.output_file)

    except OSError:
        os.makedirs(args.output_file)
        result_df.to_csv(args.output_file, index=True)
        logging.info('Creating directory : ' + os.path.dirname(args.output_file))
        logging.info('Writing in ' + args.output_file)

    except TypeError as e:
        logging.info('Error writing output file:  ' + e )

    logging.info(' ------------------')