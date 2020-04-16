#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Fonction backend à l'initialisation

import json
import pandas as pd

def get_sample_name(input="data/proteomX/csv/ProteomX_sprint_rawData.csv", output="test/sample_name.json"):
    # load df header, extract sample name from "Normalized" column. Write json.
    df = pd.read_csv(input, nrows=0)

    all_col = [i for i in df.columns]
    sample_name = {}
    sample_name["header"] = []

    for i in all_col:
        if "Normalized" in i:
            sample_name["header"].append(i.replace("Abundances (Normalized): ", ""))

    # If no "Normalized" column detected, return all column
    if len(sample_name["header"]) == 0:
        sample_name["header"] = all_col
        sample_name["error"] = "No Normalized column found"

    # write new file
    with open(output, 'w+') as json_file:
        json.dump(sample_name, json_file, indent=True)


def write_config_file(input="test/config_file.json", organism="hsapien", group=["group1", "group2"], max_na=33,
                      sheet_index=1, reference=0, output="test/new_config_file.json"):
    ### Take pre-write json file (input) . Rewrite json file (output) with given arguments
    with open(input) as json_file:
        data_template = json.load(json_file)

    # rename group in overlap & boxplot_abundances
    data_template["overlap"]["subset"][0] = group[0]
    data_template["overlap"]["subset"][1] = group[1]
    data_template["boxplot_abundances"]["subset"][0] = group[0]
    data_template["boxplot_abundances"]["subset"][1] = group[1]

    # rename organism
    data_template["gene_name"]["organism"] = organism

    # sheet index
    data_template["convert_to_csv"]["worksheet"] = sheet_index

    # replace max_na_percent value
    data_template["clean_na"]["max_na_percent"] = max_na

    # rename reference groupe
    data_template["ratio"]["reference"] = group[reference]

    # make new json_file
    with open(output, 'w+') as json_file:
        json.dump(data_template, json_file, indent=True)
