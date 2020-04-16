#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Prends le fichier csv en input et génère un fichier json contenant le nom des échantillons en output.

import argparse
import init_fonction


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", "-i", help='Input file (csv)',
                        default="data/proteomX/sample/csv/ProteomX_sprint_rawData.csv")
    parser.add_argument("--output_file", "-o", help="output file (json)", default="backend/test/sample_name_exemple.json")
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = get_args()
    init_fonction.get_sample_name(args.input_file, args.output_file)
