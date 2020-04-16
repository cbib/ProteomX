#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Fonction backend à l'initialisation

import json
import pandas as pd
import re


def get_sample_name(input,output):
    # load df header, extract sample name from "Normalized" column. Write json.
    df = pd.read_csv(input, nrows=0)

    sample_name = {}
    sample_name["header"] = []

    for i in df.columns:
        if "Normalized" in i:
            sample_name["header"].append(i.replace("Abundances (Normalized): ", ""))

    # If no "Normalized" column detected, return all column
    if len(sample_name["header"]) == 0:
        sample_name["header"] = all_col
        sample_name["error"] = "No Normalized column found"

    # write new file
    with open(output, 'w+') as json_file:
        json.dump(sample_name, json_file, indent=True)


def write_config_file(input, output, organism="hsapien", group=["group1", "group2"], max_na=33,
                      sheet_index=1, reference=0):
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


##Error
def is_good_format(input_file):
    # Check for .xlsx or .xls extension
    if input_file[-4:] != "xlsx":
        return "wrong file format"
    else:
        return True

def check_for_special_character(input_file):
    # find special character or space in file name.
    regex = re.compile('[@_!#$%^&*<>?/\|}{~:] ')
    if (regex.search(input_file) == None):
        return True
    else:
        return "special character in file name"

def is_file_empty(table):
    if table.empty:
        return "empty file"
    else:
        return True

def is_abondance_col(table):
    for i in table.columns:
        if "Abundances" in i:
            return True
    return "no abundances column found"

def enough_prot(table):
    if table.shape[0] < 2:
        return "no protein in file"
    else:
        return True


def check_all_error(input_file, table):
    all_error = []

    check_func = [is_good_format(input_file), check_for_special_character(input_file), is_file_empty(table),
                  is_abondance_col(table), enough_prot(table)]

    for i in check_func:
        if type(i) == str:
            all_error.append(i)
    return all_error
