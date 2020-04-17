#!/usr/bin/env python
# -*- coding: utf-8 -*-
### Pour les arguments renseigné, réécrit dans le mapping file les nouvelles valeurs.
### Dans le même temps, permet de créer le mapping file si l'argument "write_mapping = True"

import argparse
import init_fonction
import helpers


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json_template", "-i", help='Template of json_file', default="config_files/config_file.json")
    parser.add_argument("--organism", "-org", type=str, choices=["hsapiens", "mmusculus"], help="Choose organism")

    #à renseigner si write_mapping=True
    parser.add_argument("--group", "-gr", nargs="+")

    parser.add_argument("--max_na_percent_prot", "-nap", type=int, help="remove protein with less than max_na_percent")
    parser.add_argument("--max_na_percent_sample", "-nas", type=int,
                        help="remove samples with less than max_na_percent")
    parser.add_argument("--reference", "-ref", type=int, help="give the index of reference group")
    parser.add_argument("--output_file", "-o", help='output json file',
                        default="data/proteomX/sample/log/new_conf_file.json")
    #args for create_mapping_file
    parser.add_argument('--write_mapping', "-wm", type=bool, default=False)

    #à renseigner si write_mapping=True
    parser.add_argument('--group1', nargs='+', help='A list of columns corresponding to the first group')
    parser.add_argument('--group2', nargs='+', help='A list of columns corresponding to the second group')
    parser.add_argument('--mapping_file', '-map', help='Output file in csv format')

    args = parser.parse_args()
    return args


if __name__ == '__main__':

    #update config_file
    args = get_args()
    init_fonction.write_config_file(input=args.json_template, organism=args.organism, group=args.group,
                                    max_na_prot=args.max_na_percent_prot, max_na_sample=args.max_na_percent_sample,
                                    reference=args.reference, output=args.output_file)

    #créer le fichier de mapping
    if args.write_mapping:
        headers = ['group', 'sample', 'original column label']
        df = helpers.create_mapping(headers, args.group1, args.group[0], args.group2, args.group[1])
        df.to_csv(args.mapping_file, sep='\t', index=False)

