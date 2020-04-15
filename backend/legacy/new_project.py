#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Benjamin Dartigues, Macha Nikolski


"""
Create appropriate directories for a new project.
"""


import argparse
import paths
import helpers as h
import os
import pathlib


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project_name", "-p", type=str, help='Name of the project')

    args = parser.parse_args()
    return args


def create_folders(project_name, logger):

    folders_to_create = [paths.data_dir, paths.config_dir, paths.snakefile_dir]

    for folder in folders_to_create:

        path_to_create = os.path.join(paths.root_dir, folder, project_name)
        try:
            pathlib.Path(path_to_create).mkdir(parents=False, exist_ok=False)
            logger.info('Creating directory: ' + path_to_create)
        except FileExistsError:
            logger.info('Failure: ' + path_to_create + ' already exists.')

    return


def main():
    args = get_args()
    logpath = os.path.join(paths.root_dir, paths.logpath, 'new_project.log')
    print(logpath)
    logger = h.get_logger(logpath)

    logger.info('Creating folders for {} project'.format(args.project_name))
    create_folders(args.project_name, logger)

    logger.info('New project created')


if __name__ == "__main__":
    main()






