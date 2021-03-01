#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Fonction backend à l'initialisation

import json
import pandas as pd
import re


def get_sample_name(df, output):
    # load df header, extract sample name from "Normalized" column. Write json.

    sample_name = {}
    sample_name["header"] = []

    for i in df.columns:
        if "Normalized" in i:
            sample_name["header"].append(i.replace("Abundances (Normalized): ", ""))

    # If no "Normalized" column detected, return all column
    if len(sample_name["header"]) == 0:
        # @Cedric it doesn't wiht the line below
        # sample_name["header"] = df.columns
        # @Cedric this line below works !
        [sample_name["header"].append(col) for col in df.columns.values]
        sample_name["error"] = "No Normalized column found"

    # write new file
    with open(output, 'w+') as json_file:
        json.dump(sample_name, json_file, indent=True)


def write_config_file(json_file, organism, group, max_na_prot,
                      max_na_sample, reference):
    # Take pre-write json file (input) . Rewrite json file (output) with given arguments
    with open(json_file) as f:
        data_parameters = json.load(f)

    # rename organism
    if organism:
        data_parameters["gene_name"]["organism"] = organism

    # replace max_na_percent value
    if max_na_prot:
        data_parameters["missing_values"]["max_na_percent_proteins"] = max_na_prot

    if max_na_prot:
        data_parameters["missing_values"]["max_na_percent_samples"] = max_na_sample

    # rename reference groupe
    # Attention !! Si reference est un argument, group doit être en argument aussi.
    if type(reference) is int:
        data_parameters["all"]["reference"] = group[reference]
    elif type(reference) is str:
        data_parameters["all"]["reference"] = reference

    # save json file
    with open(json_file, 'w+') as f:
        json.dump(data_parameters, f, indent=True)


# Error
def is_good_format(input_file):
    # Check for .xlsx or .xls extension
    if input_file[-4:] != "xlsx":
        return "wrong file format"
    else:
        return True


def check_for_special_character(input_file):
    # find special character or space in file name.
    regex = re.compile('[@_!#$%^&*<>?/\|}{~:] ')
    if regex.search(input_file) == None:
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


def find_accession(table):
    if "Accession" not in table.columns:
        return "no accession column found"
    else:
        return True


def check_dtypes(table):
    for i in table.columns:
        if "Abundances" in i:
            if table[i].dtypes != float:
                return "Abundance column values are not float"
            else:
                return True


def check_file_name(input_file):
    all_error = []
    check_func = [is_good_format(input_file), check_for_special_character(input_file)]

    for i in check_func:
        if type(i) == str:
            all_error.append(i)
    return all_error


def check_data_error(table):
    all_error = []

    check_func = [is_file_empty(table),
                  is_abondance_col(table), enough_prot(table), find_accession(table), check_dtypes(table)]

    for i in check_func:
        if type(i) == str:
            all_error.append(i)

    return all_error