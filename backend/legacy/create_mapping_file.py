#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski, Benjamin Dartigues, Cedric Usureau, Aurélien Barré, Hayssam Soueidan

import argparse
import helpers

def get_args():
    example_text = "Usage example: " \
                   "python create_mapping_file.py --group1 P1 P2 P3, --group1_name foo, " \
                   "--group2 P11 P12 P13 --group2_name bar --out foobar.csv"
    parser = argparse.ArgumentParser(epilog=example_text)
    parser.add_argument('--group1', nargs='+', required=True, help='A list of columns corresponding to the first group')
    parser.add_argument('--group1_name', type=str, required=False, default = 'group1', help='Name of the first group')
    parser.add_argument('--group2', nargs='+', required=True, help='A list of columns corresponding to the second group')
    parser.add_argument('--group2_name', type=str, required=False, default = 'group2', help='Name of the second group')
    parser.add_argument('--out', '-o', required=True, help='Output file in csv format')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = get_args()
    headers = ['group', 'sample', 'original column label']
    df = helpers.create_mapping(args.group1, args.group1_name, args.group2, args.group2_name)
    df.to_csv(args.out, sep='\t', index=False)
