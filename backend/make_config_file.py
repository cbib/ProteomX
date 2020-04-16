#!/usr/bin/env python
# -*- coding: utf-8 -*-
### Script permettant de réécrire le config_file en fonction des arguments renseigné : nom des groupes, nom de l'organisme, index de la feuille de calcul,
### max_na_percent, groupe de référence.

import argparse
import init_fonction
import json


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json_template", "-i", help='Template of json_file', default="config_files/config_file.json")
    parser.add_argument("--organism", "-org", type=str, choices=["hsapiens", "mmusculus"], help="Choose organism",
                        default="hsapiens")
    parser.add_argument("--group", "-gr", nargs="+", default="group1 group2")
    parser.add_argument("--max_na_percent", "-na", type=int, help="remove protein with less than max_na_percent",
                        default=33)
    parser.add_argument("--sheet_name_index", "-sh", type=str, help="sheetname index from xlsx file", default=1)
    parser.add_argument("--reference", "-ref", type=int, help="give the index of reference group", default=0)
    parser.add_argument("--output_file", "-o", help='output json file', default="backend/test/new_config_file.json")
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = get_args()
    init_fonction.write_config_file(input=args.json_template, organism=args.organism, group=args.group,
                                    max_na=args.max_na_percent, sheet_index=args.sheet_name_index,
                                    reference=args.reference, output=args.output_file)
