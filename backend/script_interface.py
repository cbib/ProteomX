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
import os
import helpers as h
import logging.config


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

    logpath = os.path.join(paths.global_data_dir, args.analysis_ID, 'interface_frontend.log')
    logger = h.get_logger(logpath)
    logging.info("Analysis for {} project.".format(args.analysis_ID))

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

        script = 'analyze_test_dataset_target_rule.sh'
        path_to_script = os.path.join(paths.global_scripts_dir, script)
        logging.info("Script: {}".format(script))

        # Parts of analysis. To be updated for longer or more complex snakefile
        target = {"preprocesing": ["mapped", "gene_name"],
                  "quality_check": ["missing_values", "CV"],
                  "diff_analysis": ["log2FC", "ttest"]}
        rerun = str(args.rerun)
        dry_run = str(args.rerun)

        # TODO: stdout/stderr ?
        # Venv + snakemake ?
        p = subprocess.Popen(
            [path_to_script, '-i', args.analysis_ID, '-t', target[args.step][1], '-R', target[args.step][0], '-r',
             rerun, '-s', 'Snakefile', '-n', dry_run],
            shell=False)
        p.wait()
        p.terminate()

        logging.info("Analysis finished.")
