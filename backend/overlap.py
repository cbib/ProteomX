#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski


"""
Compute overlap for each protein :the 'overlap' is defined as the distance between values interval of each groups.
TODO :better explanation + logs

Two methods:
- symmetric overlap: proteins from both groups are of interest
- asymmetric overlap : only proteins from one group are of interest

Works only if two groups of samples are present in the input_file dataframe (as it should be at this step)
"""


import argparse
import pandas as pd
import helpers as h
import os
import paths
import functions_analysis as fa


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", "-i", help='Input file (csv)')
    parser.add_argument("--output_file", "-o", help='Output file (csv)')
    parser.add_argument("--project", "-p", help='Project name')
    parser.add_argument("--version", "-v", help='Analysis version name')

    args = parser.parse_args()
    return args



if __name__ == "__main__":
    args = get_args()
    rule_params = h.load_json_parameter(args.project, args.version)
    filename = h.filename(args.input_file)

    logpath = os.path.join(paths.global_root_dir, paths.global_data_dir, args.project, args.version, 'log/overlap.log')
    logger = h.get_logger(logpath)

    data_df = pd.read_csv(args.input_file, header=0, index_col=None)

    # define two groups of patients
    # 'group1' (group[0]) is regarded as the reference in case of asymmetric computation
    # TODO: "reference" in rule "ratio" in the config file => move to rule "all"
    groups = h.get_data_subset(data_df, rule_params['all']['values_cols_prefix'], rule_params['ratio']['reference'])

    # Compute overlap per protein
    overlap_method = rule_params['overlap']['method']
    result_df = fa.compute_overlap(data_df, groups[0], groups[1], overlap_method)

    h.export_result_to_csv(result_df, args.output_file)