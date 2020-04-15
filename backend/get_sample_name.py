#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import argparse
import pandas as pd

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", "-i", help='Input file (csv)')
    args = parser.parse_args()
    return args

args = get_args()

data = pd.read_csv(args.input_file, nrows=0)

all_col = [i for i in data.columns]

sample_name["header"] = []
for i in all_col:
    if "Normalized" in i:
        sample_name["header"].append(i.replace("Abundances (Normalized): ", ""))

if len(sample_name["header"]) == 0:
    sample_name["header"] = all_col

with open("./config_files/samples_names.json", 'w+') as json_file:
    json.dump(sample_name, json_file, indent=True)

