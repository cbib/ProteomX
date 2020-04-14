#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski


""""
Return excel file from csv file
"""


import argparse
import pandas as pd
import os
from os.path import isfile, join


def get_args():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-i', '--input_files', nargs='+', type=str)
    group.add_argument('-d', '--directory', type=str)
    parser.add_argument('-o', '--output_dir', type=str)

    args = parser.parse_args()
    return args


def export_files_to_excel(files_list):
    for file in files_list:
        df = pd.read_csv(file, header=0, index_col=None)
        filename = os.path.basename(file).split('.')[0] + '.xlsx'
        output_df = join(args.output_dir, filename)

        df.to_excel(output_df, index=False)


if __name__ == "__main__":
    args = get_args()

    if args.input_files:
        export_files_to_excel(args.input_files)

    elif args.directory:
        files = [join(args.directory, f) for f in os.listdir(args.directory) if isfile(join(args.directory, f)) and '.csv' in f]
        print(files)
        export_files_to_excel(files)
