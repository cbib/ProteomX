#!/usr/bin/env python
# -*- coding: utf-8 -*-

#raw data (xlsx) en input. Génère un fichier json d'erreur.

import init_fonction
import argparse
import pandas as pd
import json

test = "ProteomX_sprint_rawData.xlsx"

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", "-i", help='Input file (xlsx)',
                        default="data/proteomX/sample/raw_data/ProteomX_sprint_rawData.xlsx")
    parser.add_argument("--config_file", "-c", help='Config file', default="config_files/config_file.json")
    parser.add_argument("--error_file", "-o", help="output file (json)", default="backend/test/error_file_exemple.json")
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = get_args()

    with open(args.config_file) as f:
        rule_params = json.load(f)

    if "/" in args.input_file:
        sample_name = (args.input_file.split("/")[-1])
    else :
        sample_name = args.input_file

    errors = []

    try:
        df = pd.read_excel(args.input_file,
                                 sheet_name=1,
                                 skiprows=rule_params["convert_to_csv"]["rows_to_skip"],
                                 index_col=rule_params["convert_to_csv"]["index_col"])

    except IndexError:
        errors.append("no sheet found")
        df = pd.read_excel(args.input_file,
                           sheet_name=0,
                           skiprows=rule_params["convert_to_csv"]["rows_to_skip"],
                           index_col=rule_params["convert_to_csv"]["index_col"])

    errors = errors + init_fonction.check_all_error(sample_name, df)

    error_dict = {}
    error_dict["errors"] = errors

    init_fonction.check_dtypes(df)

    with open(args.error_file, 'w+') as json_file:
        json.dump(error_dict, json_file, indent=True)