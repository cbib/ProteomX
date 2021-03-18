#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

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

    parser.add_argument("--analysis_ID", "-a", type=str, required=True, help="Unique ID of downloaded file")

    # Create mapping file
    parser.add_argument('--mapping_info', "-mi", help="csv file from frontend")

    # Update config file
    parser.add_argument("--update_config_file", "-upc", action='store_true')

    parser.add_argument("--organism", "-org", type=str, choices=["hsapiens", "mmusculus"], help="Choose organism")
    parser.add_argument("--max_na_percent_protein", "-nap", type=int,
                        help="remove protein with less than max_na_percent")
    parser.add_argument("--max_na_percent_sample", "-nas", type=int,
                        help="remove samples with less than max_na_percent")
    parser.add_argument("--reference", "-ref", help="give the name of reference group")
    parser.add_argument("--variation_coefficient", "-cv", type=float,
                        help="Threshold value to apply after CV computations")
    parser.add_argument("--specific_proteins", "-sp", choices=[0, 1], help="0 if discard specific proteins, 1 else")
    parser.add_argument("--contrast_matrix", "-cm", help="Contrast matrix to compare several groups of samples")

    # Snakemake
    parser.add_argument("--run", "-r", action='store_true')
    parser.add_argument("--step", "-s",
                        choices=["preprocessing", "quality_check", "differential_analysis", "post_treatment"], type=str,
                        help="step that need to be (re)run")
    parser.add_argument("--rerun", "-re", action='store_true', help="True if the step has already been computed")
    parser.add_argument("--dryrun", "-n", action='store_true', help="True for snakemake dryrun")

    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    path_analysis = h.path_to_analysis(args.analysis_ID)

    pathlib.Path('data_folder/{}/log/'.format(args.analysis_ID)).mkdir(parents=True, exist_ok=True)
    logger = h.get_logger(args.analysis_ID, 'interface')

    # Create mapping file
    if args.mapping_info:
        logging.info("Creating mapping file.")
        map = helpers.create_mapping_from_csv_file(args.mapping_info)

        out_mapping = os.path.join(path_analysis, 'mapping')
        pathlib.Path(out_mapping).mkdir(parents=True, exist_ok=True)

        file_name = os.listdir(os.path.join(path_analysis, "csv"))[0]
        out_mapping_file = os.path.join(out_mapping, "mapping_{}".format(file_name))

        logging.info("Exporting mapping file to: {}".format(out_mapping_file))
        map.to_csv(out_mapping_file, sep='\t', index=False)

    # Update config_file
    if args.update_config_file:
        path_to_json = path_analysis + '/config_file.json'
        try:
            with open(path_to_json) as f:
                data_parameters = json.load(f)
            logging.info("Updating config_file.")
        except FileNotFoundError:
            path_to_json_template = os.path.join(paths.global_resources_dir, 'TEMPLATE_config_file.json')
            with open(path_to_json_template) as f:
                data_parameters = json.load(f)
            logging.info("Loading new config_file for this analysis.")

        parameters_to_update = {"organism": args.organism,
                                "max NAN per protein": args.max_na_percent_protein,
                                "max NAN per sample": args.max_na_percent_sample,
                                "CV": args.variation_coefficient,
                                "Specific proteins": args.specific_proteins,
                                "Reference": args.reference}

        list_parameters = [v for v in parameters_to_update.values()]

        if any(v is not None for v in list_parameters):
            data_parameters = fi.update_config(data_parameters=data_parameters, organism=args.organism,
                                               max_na_prot=args.max_na_percent_protein,
                                               max_na_sample=args.max_na_percent_sample,
                                               reference=args.reference,
                                               cv=args.variation_coefficient,
                                               specific_proteins=args.specific_proteins)
            logging.info("New parameters:")
            [logging.info("... {} : {}".format(k, v)) for k, v in parameters_to_update.items() if v]
        else:
            logging.info("No parameters changed")

        # save json file
        with open(path_to_json, 'w+') as f:
            json.dump(data_parameters, f, indent=True)

    # Run analysis
    if args.run:
        logging.info("Running analysis.")

        # Following if / else loop : choose Snakefile depending on the experimental design. Two conditions ? basic
        # "Snakefile". More than two conditions ? Handled by "Snakefile_multiple".
        # target dictionary list for each step (preprocessing, quality_check, etc) the first AND the last rule to run.
        # That way, analysis is done by telling Snakemake to run until last rule. But if one step is to be rerun,
        # the script "force" Snakemake to re-create all the files by rerunning the first rule of the step : since
        # upstream snakemake timestamps and files have been modified, it forces the rerun of (already done once)
        # downstream pipeline.
        if args.contrast_matrix:
            # TODO
            snakefile = "Snakefile_multiple"

            target = {"preprocessing": ["mapped", "divided"],
                      "quality_check": ["missing_values", "CV"],
                      "differential_analysis": ["log2FC", "ttest"],
                      "post_treatment": ["gene_name", "enrichment"]}

        elif args.reference:
            snakefile = "Snakefile"

            target = {"preprocessing": ["mapped", "data_reduction"],
                      "quality_check": ["missing_values", "CV"],
                      "differential_analysis": ["log2FC", "ttest"],
                      "post_treatment": ["gene_name", "enrichment"]}

        else:
            snakefile = "Snakefile"

            target = {"preprocessing": ["mapped", "data_reduction"],
                      "quality_check": ["missing_values", "CV"],
                      "differential_analysis": ["log2FC", "ttest"],
                      "post_treatment": ["gene_name", "enrichment"]}

        script = 'analyze_test_dataset_target_rule.sh'
        path_to_script = os.path.join(paths.global_scripts_dir, script)
        logging.info("Script: {}".format(script))

        rerun = str(args.rerun)
        dry_run = str(args.dryrun)

        # TODO: stdout/stderr ?
        # Venv + snakemake ?
        p = subprocess.Popen(
            [path_to_script, '-i', args.analysis_ID, '-t', target[args.step][1], '-R', target[args.step][0], '-r',
             rerun, '-s', snakefile, '-n', dry_run],
            shell=False)
        p.wait()
        p.terminate()

        logging.info("Analysis finished.")
