#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Pour les arguments renseigné, réécrit dans le mapping file les nouvelles valeurs.
Dans le même temps, permet de créer le mapping file si l'argument "write_mapping = True"

To run :
python ./backend/script_interface.py
"""

import argparse
import functions_import as fi
import helpers
import subprocess
import paths
import pathlib
import os
import helpers as h
import logging.config
import json


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--analysis_ID", "-f", type=str, required=True, help="Unique ID of downloaded file")

    # Create mapping file
    parser.add_argument('--write_mapping', "-wm", type=bool, default=False)

    # Mandatory if write_mapping=True
    parser.add_argument("--group", "-gr", nargs="+")
    parser.add_argument('--group1', nargs='+', help='A list of columns corresponding to the first group')
    parser.add_argument('--group2', nargs='+', help='A list of columns corresponding to the second group')
    parser.add_argument('--json_samples', '-js', help="Path to json with sample kept/discarded by user")

    # Update config file
    parser.add_argument("--update_config_file", "-upc", action='store_true')

    parser.add_argument("--organism", "-org", type=str, choices=["hsapiens", "mmusculus"], help="Choose organism")
    parser.add_argument("--max_na_percent_protein", "-nap", type=int,
                        help="remove protein with less than max_na_percent")
    parser.add_argument("--max_na_percent_sample", "-nas", type=int,
                        help="remove samples with less than max_na_percent")
    parser.add_argument("--reference", "-ref", type=int, help="give the index of reference group")

    # type of analysis
    parser.add_argument("--several_conditions", "-sc", action='store_true',
                        help="True if there is more than two conditions to analyse")
    parser.add_argument("--contrast_matrix", "-cm",
                        help="Contrast matrix to compare several groups of samples")

    # Snakemake
    parser.add_argument("--run", "-r", action='store_true')
    parser.add_argument("--step", "-s", choices=["preprocessing", "quality_check", "diff_analysis"], type=str,
                        help="step that need to be (re)run")
    parser.add_argument("--rerun", "-re", action='store_true', help="True if the step has already been computed")
    parser.add_argument("--dryrun", "-n", action='store_true', help="True for snakemake dryrun")

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = get_args()
    path_analysis = h.path_to_analysis(args.analysis_ID)

    pathlib.Path('data_folder/{}/log/'.format(args.analysis_ID)).mkdir(parents=True, exist_ok=True)
    logger = h.get_logger(args.analysis_ID, 'interface')

    logging.info("Analysis for {} project.".format(args.analysis_ID))

    # First step : create or find the file describing the analysis.
    try:
        path_to_json = os.path.join(paths.global_data_dir, args.analysis_ID, "analysis.json")
        with open(path_to_json) as f:
            analysis_description = json.load(f)
    except FileNotFoundError:
        path_to_json = os.path.join(paths.global_resources_dir, "analysis_template.json")
        with open(path_to_json) as f:
            analysis_description = json.load(f)
        analysis_description = {}


    # Create mapping file
    if args.write_mapping:
        logging.info("Creating mapping file.")
        headers = ['group', 'sample', 'original column label']
        df = helpers.create_mapping(headers, args.group1, args.group[0], args.group2, args.group[1])

        out_mapping_file = path_analysis + '/mapping_{}.csv'.format(args.analysis_ID)
        df.to_csv(out_mapping_file, sep='\t', index=False)

    # Update config_file
    if args.update_config_file:
        logging.info("Updating config_file.")
        path_to_json = path_analysis + '/config_file.json'
        fi.write_config_file(json_file=path_to_json, organism=args.organism, group=args.group,
                             max_na_prot=args.max_na_percent_protein,
                             max_na_sample=args.max_na_percent_sample,
                             reference=args.reference)

    # Run analysis
    if args.run:
        logging.info("Running analysis.")

        if args.several_conditions:
            snakefile = "Snakefile_multiple"

            target = {"preprocessing": ["mapped", "divided"],
                      "quality_check": ["missing_values", "CV"],
                      "diff_analysis": ["log2FC", "gene_name"]}

        elif not args.several_conditions:
            snakefile = "Snakefile"

            target = {"preprocessing": ["mapped", "data_reduction"],
                      "quality_check": ["missing_values", "CV"],
                      "diff_analysis": ["log2FC", "gene_name"]}

        else:
            snakefile = "Snakefile"

            target = {"preprocessing": ["mapped", "data_reduction"],
                      "quality_check": ["missing_values", "CV"],
                      "diff_analysis": ["log2FC", "gene_name"]}

        script = 'analyze_test_dataset_target_rule.sh'
        path_to_script = os.path.join(paths.global_scripts_dir, script)
        logging.info("Script: {}".format(script))

        # Parts of analysis. To be updated for longer or more complex snakefile

        rerun = str(args.rerun)
        dry_run = str(args.dryrun)

        print(dry_run)
        # TODO: stdout/stderr ?
        # Venv + snakemake ?
        p = subprocess.Popen(
            [path_to_script, '-i', args.analysis_ID, '-t', target[args.step][1], '-R', target[args.step][0], '-r',
             rerun, '-s', snakefile, '-n', dry_run],
            shell=False)
        p.wait()
        p.terminate()

        logging.info("Analysis finished.")
