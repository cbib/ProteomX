#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski


"""
Compute several scores for each protein to assess overlap between value intervals
TODO : rajouter logs

Two methods:
- symmetric overlap: proteins from both groups are of interest
- asymmetric overlap : only proteins from one group are of interest
"""


import argparse
import pandas as pd
import numpy as np
import helpers as h
from locale import atof
import matplotlib.pyplot as plt
import os
import paths


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", "-i", help='Input file (csv)')
    parser.add_argument("--output_file", "-o", help='Output file (csv)')
    parser.add_argument("--output_figure", "-f", help='Histogram of overlap values distribution')
    parser.add_argument("--project", "-p", help='Project name')
    parser.add_argument("--version", "-v", help='Analysis version name')


    args = parser.parse_args()
    return args


def get_data_subset(df):
    # TODO; args / kwarg to return dictionary ?
    df_list = list()
    i=0
    for subset in rule_params['overlap']['subset']:

        sub_df = df.filter(regex=subset)
        df_list.append(sub_df)
        i=i+1
    return df_list


def overlap_symmetric(x, y):
    a = [np.nanmin(x), np.nanmax(x)]
    b = [np.nanmin(y), np.nanmax(y)]

    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)

    overlap = np.nanmax([a[0], b[0]]) - np.nanmin([a[1], b[1]])

    return overlap


def compute_overlap(df, condition1, condition2, overlap_method):

    for i in df.index.values:
        condition1_values = np.array(condition1.iloc[i].map(lambda x: atof(x) if type(x) == str else x))
        condition2_values = np.array(condition2.iloc[i].map(lambda x: atof(x) if type(x) == str else x))

        if overlap_method == "symmetric":
            df.loc[i, 'score_overlap'] = overlap_symmetric(condition1_values, condition2_values)
        else:
            df.loc[i, 'score_overlap'] = overlap_asymmetric(condition1_values, condition2_values)

    return df


def overlap_asymmetric(x, y):
    # x is the reference group
    overlap = np.nanmin(y) - np.nanmax(x)

    return overlap


def plot_histogram_distribution(v_list,filename,filepath, type, ylabel, bins, axvline = None):
    plt.hist(list(v_list), bins=bins)
    plt.xlabel(type + ' values')
    plt.ylabel(ylabel)
    if axvline:
        plt.axvline(axvline, color='red', linestyle='dashed', linewidth=1)

    plt.title(type + ' distribution')
    plt.savefig(filepath + '_' + 'histogram' + ".png")
    plt.close()


if __name__ == "__main__":
    args = get_args()
    rule_params = h.load_json_parameter(args.project, args.version)
    filename = h.filename(args.input_file)

    logpath = os.path.join(paths.root_dir, paths.data_dir, args.project, args.version, 'log/overlap.log')
    logger = h.get_logger(logpath)

    data_df = pd.read_csv(args.input_file, header=0, index_col=None)

    # define two groups of patients. 'group1' is considered as the reference in case of asymmetric computation
    groups = get_data_subset(data_df)
    overlap_method = rule_params['overlap']['method']
    result_df = compute_overlap(data_df, groups[0], groups[1], overlap_method)

    if args.output_figure:
        plot_histogram_distribution(result_df['score_overlap'], filename, args.output_figure, 'overlap', 'proteins #', 150)

    h.export_result_to_csv(result_df, args.output_file)