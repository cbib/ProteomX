#!/usr/bin/env python
# -*- coding: utf-8 -*-

# input : xlsx
# output : errors log (-er), sample name (-s), xlsx file (-o)

import argparse
import pandas as pd
import json
import os
from loguru import logger
import helpers as h
import paths
import functions_import as fi


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", "-i", help='Input file (xlsx)')
    parser.add_argument("--analysis_id", "-a", help='Input file (xlsx)')
    parser.add_argument("--config_file", "-c", help='Config file', default="resources/config_file_template.json")
    parser.add_argument("--error_file", "-er", help="error file (json)", default="error_import.json")
    parser.add_argument("--output_file", "-o", help="output file (csv)")
    parser.add_argument("--output_sample_name", "-s", help="output file with sample name (json)",
                        default="sample_name.json")
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()

    logger.debug("BEGINNING IMPORT")
    logger.debug("Loading parameters")
    with open(args.config_file) as f:
        rule_params = json.load(f)

    sample_name = os.path.basename(args.input_file)

    errors = {}

    logger.debug("Loading excel file...")
    try:
        df = pd.read_excel(args.input_file,
                           sheet_name=1,
                           skiprows=rule_params["convert_to_csv"]["rows_to_skip"],
                           index_col=rule_params["convert_to_csv"]["index_col"])

    except IndexError:
        errors["sheet_error"] = ["no sheet in second position found"]
        logger.debug("WARNING: loading first worksheet")
        df = pd.read_excel(args.input_file,
                           sheet_name=0,
                           skiprows=rule_params["convert_to_csv"]["rows_to_skip"],
                           index_col=rule_params["convert_to_csv"]["index_col"])

    errors["file_name_error"] = fi.check_file_name(sample_name)
    errors["data_error"] = fi.check_data_error(df)

    logger.debug("Exporting errors")
    path2error_file = os.path.join(paths.global_data_dir, args.error_file)
    with open(args.error_file, 'w+') as json_file:
        json.dump(errors, json_file, indent=True)

    logger.debug("Exporting files")

    # export errors
    output_sample_name = os.path.join(paths.global_data_dir, args.analysis_id, args.output_sample_name)
    fi.get_sample_name(df, output_sample_name)

    # export data
    h.export_result_to_csv(df, args.output_file, index_col=True)

    # save config file
    path2config = os.path.join(paths.global_data_dir, args.analysis_id, "config_file.json")
    with open(path2config, 'w+') as f:
        json.dump(rule_params, f, indent=True)
