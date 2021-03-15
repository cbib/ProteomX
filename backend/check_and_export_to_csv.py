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
    parser.add_argument("--analysis_id", "-a", type=str, help='Analysis identifier')
    # default path for following files:
    parser.add_argument("--output_file", "-o", help="output file (csv)")
    parser.add_argument("--error_file", "-er", default="import_error.json", help="error file (json)" )
    parser.add_argument("--output_sample_name", "-s", default="header.json", help="output file with sample name (json)")
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()

    logger.debug("BEGINNING IMPORT")

    sample_name = os.path.basename(args.input_file)
    errors = {}

    logger.debug("Loading excel file...")
    try:
        df = pd.read_excel(args.input_file,
                           sheet_name=1)

    except IndexError:
        errors["sheet_error"] = ["no sheet in second position found"]
        logger.debug("Loading first worksheet")
        df = pd.read_excel(args.input_file,
                           sheet_name=0)

    errors["file_name_error"] = fi.check_file_name(sample_name)
    errors["data_error"] = fi.check_data_error(df)
    logger.debug("... excel file loaded")

    path2analysis_folder = os.path.join(paths.global_data_dir, args.analysis_id)
    try:
        os.mkdir(path2analysis_folder)
        logger.debug("Creating folder for this analysis")
    except FileExistsError:
        logger.debug("Analysis folder already created")

    path2error_file = os.path.join(paths.global_data_dir, args.analysis_id, args.error_file)

    logger.debug("Exporting import_error file to: {}".format(path2error_file))
    with open(args.error_file, 'w+') as json_file:
        json.dump(errors, json_file, indent=True)

    # export header
    output_sample_name = os.path.join(paths.global_data_dir, args.analysis_id, args.output_sample_name)

    logger.debug("Exporting header file to: {}".format(output_sample_name))
    fi.get_sample_name(df, output_sample_name)

    # export data
    if args.output_file:
        output_csv = args.output_file
    else:
        output_csv = os.path.join(paths.global_data_dir, args.analysis_id, "csv/{}.csv".format(h.filename(args.input_file)))
    logger.debug("Exporting converted file to: {}".format(output_csv))
    h.export_result_to_csv(df, output_csv, index_col=True)