#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski


"""
Take an excel file as input and convert it to csv file
"""


import argparse
import pandas as pd
import json
import os
import helpers as h
import paths


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", "-i", help='Input file (csv)')
    parser.add_argument("--output_file", "-o", help='Output file (csv)')
    parser.add_argument("--project", "-p", help='Project name')
    parser.add_argument("--version", "-v", help='Analysis version name')
    parser.add_argument("--config_file", "-c", help='Config file')

    args = parser.parse_args()
    return args


def log_info_df():
    logger.info('Starting converting excel file: ' + args.input_file)
    logger.info('Reading: ' + rule_params["convert_to_csv"]["worksheet"] + ' worksheet.')
    if rule_params["convert_to_csv"]["rows_to_skip"]:
        logger.info('Skipping: ' + str(rule_params["convert_to_csv"]["rows_to_skip"]) + ' rows.')
    else:
        logger.info("Reading all rows.")

    if rule_params["convert_to_csv"]["index_col"]:
        logger.info('Column used as index: ' + str(rule_params["convert_to_csv"]["index_col"]))
    else:
        logger.info('Column used as index: none.')


# TODO : function to replace null values (from list/dictionary ?)
def replace_special_values(df, null_values):
    if rule_params["convert_to_csv"]["values_to_replace"]:
        logger.info("Values replaced in the dataframe.")
        df = df.replace(null_values)
    else:
        logger.info("No values to replace in the dataframe.")

    return df


if __name__ == "__main__":
    args = get_args()

    if not args.config_file:
        rule_params = h.load_json_parameter(args.project, args.version)
    else:
        with open(args.config_file) as f:
            rule_params = json.load(f)

    logpath = os.path.join(paths.global_root_dir, paths.global_data_dir, args.project, args.version, 'log/convert_to_csv.log')
    logger = h.get_logger(logpath)
    log_info_df()

    input_df = pd.read_excel(args.input_file,
                             sheet_name=rule_params["convert_to_csv"]["worksheet"],
                             skiprows=rule_params["convert_to_csv"]["rows_to_skip"],
                             index_col=rule_params["convert_to_csv"]["index_col"])
    logger.info("Dataframe loaded.")

    input_df = replace_special_values(input_df, rule_params["convert_to_csv"]["values_to_replace"])

    logger.info('{}'.format(len(input_df)) + ' features ready to be analysed.')

    h.export_result_to_csv(input_df, args.output_file)

