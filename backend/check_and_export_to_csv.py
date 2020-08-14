#!/usr/bin/env python
# -*- coding: utf-8 -*-

# input : xlsx
# output : log d'erreur (-er), sample name (-s), fichier au format xls (-o)

import argparse
import pandas as pd
import json
import os
import helpers as h
import functions_import as fi


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", "-i", help='Input file (xlsx)',
                        default="data/proteomX/sample/raw_data/ProteomX_sprint_rawData.xlsx")
    parser.add_argument("--config_file", "-c", help='Config file', default="config_files/config_file.json")
    parser.add_argument("--error_file", "-er", help="error file (json)",
                        default="data/proteomX/sample/log/error_file_exemple.json")
    parser.add_argument("--output_file", "-o", help="output file (csv)",
                        default="data/proteomX/sample/csv/ProteomX_sprint_rawData.csv")
    parser.add_argument("--output_sample_name", "-s", help="output file with sample name (json)",
                        default="data/proteomX/sample/log/sample_name.json")
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = get_args()

    with open(args.config_file) as f:
        rule_params = json.load(f)

    sample_name = os.path.basename(args.input_file)

    errors = {}

    try:
        df = pd.read_excel(args.input_file,
                           sheet_name=1,
                           skiprows=rule_params["convert_to_csv"]["rows_to_skip"],
                           index_col=rule_params["convert_to_csv"]["index_col"])

    except IndexError:
        errors["sheet_error"] = ["no sheet in second position found"]
        df = pd.read_excel(args.input_file,
                           sheet_name=0,
                           skiprows=rule_params["convert_to_csv"]["rows_to_skip"],
                           index_col=rule_params["convert_to_csv"]["index_col"])

    errors["file_name_error"] = init_fonction.check_file_name(sample_name)
    errors["data_error"] = init_fonction.check_data_error(df)

    with open(args.error_file, 'w+') as json_file:
        json.dump(errors, json_file, indent=True)

    fi.get_sample_name(df, args.output_sample_name)
    h.export_result_to_csv(df, args.output_file)
