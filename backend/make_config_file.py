#!/usr/bin/env python
# -*- coding: utf-8 -*-


### Script permettant de réécrire le config_file en fonction des arguments renseigné : nom des groupes, nom de l'organisme, index de la feuille de calcul,
### max_na_percent, groupe de référence.
import json
import argparse

with open("config_files/config_file.json") as json_file:
    data_template = json.load(json_file)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", "-i", help='Input file (xlsx)')
    parser.add_argument("--organism", "-org", type=str, choices=["hsapiens", "mmusculus"], help="Choose organism", default="hsapiens")
    parser.add_argument("--group", "-gr", nargs="+", required=True, default="group1 group2")
    parser.add_argument("--max_na_percent", "-na", type=int, help="remove protein with less than max_na_percent", default=33)
    parser.add_argument("--sheet_name_index", "-sh", type=str, help="sheetname index from xlsx file", default=1)
    parser.add_argument("--reference", "-ref", type=int, help="give the index of reference group", default=0)
    args = parser.parse_args()
    return args

args = get_args()

#rename group in overlap & boxplot_abundances
data_template["overlap"]["subset"][0]= args.group[0]
data_template["overlap"]["subset"][1]= args.group[1]
data_template["boxplot_abundances"]["subset"][0] = args.group[0]
data_template["boxplot_abundances"]["subset"][1] = args.group[1]

# rename organism
data_template["gene_name"]["organism"] = args.organism

# sheet index
data_template["convert_to_csv"]["worksheet"] = args.sheet_name_index

# replace max_na_percent value
data_template["clean_na"]["max_na_percent"] = args.max_na_percent

#rename reference groupe
data_template["ratio"]["reference"] = args.group[args.reference]

with open("config_files/test_tmp_config_file.json", 'w+') as json_file:
    json.dump(data_template, json_file, indent=True)