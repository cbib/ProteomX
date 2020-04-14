#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski


"""
Create a new study inside a already existing project.
Takes as input : raw data (one or more files), config file

Create a new project from user input with templates for :
- snakemake
- config file
(according to the type of project)
(- data folders)

1. Créer dossiers
2. Récupérer templates
3. Copier templates au bon endroit
4. Si rawdata/mapping file : créer dossiers au bon endroit
"""


import argparse
import analysis_variable as paths
import os
import helpers as h
import shutil
import pathlib


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project_name", "-p", help='Name of the project')
    parser.add_argument("--study_name", "-s")
    parser.add_argument("--data_type", "-o", help='Data type: proteomic, nanostring.')

    parser.add_argument("--raw_files", "-rf", nargs='+', help='Path to a file or directory')
    parser.add_argument("--mapping_files", "-mf", nargs='+', help='Path or directory to mapping files')

    args = parser.parse_args()
    return args


def check_already_existing(*args):

    folders_to_check = [paths.data_dir, paths.config_dir, paths.snakefile_dir]
    path_boolean = True

    for folder in folders_to_check:
        sub_path_to_check = os.path.join(*args)
        whole_path = os.path.join(paths.root_dir, folder, sub_path_to_check)

        if os.path.isdir(whole_path):
            logger.debug('Path :' + whole_path + ' already exists.')
        else:
            logger.debug('Path :' + whole_path + ' doesn\'t exists.')
            path_boolean = False

    return path_boolean


def create_study_folder(project_name, study_name):
    study_path = os.path.join(project_name, study_name)

    folders_to_create = [paths.data_dir, paths.config_dir, paths.snakefile_dir]

    for folder in folders_to_create:

        path_to_create = os.path.join(paths.root_dir, folder, study_path)
        try:
            pathlib.Path(path_to_create).mkdir(parents=True, exist_ok=False)
            logger.info('Creating directory: ' + path_to_create)
        except FileExistsError:
            logger.info('Failure: ' + path_to_create + ' already exists.')

    return study_path


def get_templates(datatype, study_name):

    template_dir = os.path.join(paths.root_dir, paths.templates_dir)

    # snakemake
    snakefile_template_dir = os.path.join(template_dir, 'snakefiles')
    snakefile_name = "Snakefile_" + str(datatype)

    # config file
    configfile_template_dir = os.path.join(template_dir, 'config_files')
    config_file_name = "config_file" + str(datatype)

    # copy file to new destination
    path_to_config = os.path.join(paths.root_dir, paths.config_dir, args.project_name)

    destination_folders = [paths.config_dir, paths.snakefile_dir]

    #for folder in destination_folders:

    source_path = os.path.join(snakefile_template_dir, snakefile_name)
    destination_path = os.path.join(paths.root_dir, paths.snakefile_dir, study_name)

    shutil.copyfile(source_path, destination_path)

    source_path = os.path.join(snakefile_template_dir, config_file_name)
    destination_path = os.path.join(paths.root_dir, paths.config_dir, study_name)

    shutil.copyfile(source_path, destination_path)

    return





if __name__ == "__main__":
    args = get_args()
    logpath = os.path.join(paths.logpath, 'new_study')
    logger = h.get_logger(logpath)

    # check if project exists
    if check_already_existing(args.project_name):

        # check if study already exists
        if not check_already_existing(args.project_name, args.study_name):
            pass

        # create new study folders
        logger.info('Creating folders for {} study inside the {} project'.format(args.study_name, args.project_name))
        study_directory = create_study_folder(args.project_name, args.study_name)

        # get templates
        logger.info('Retrieve templates for {} data.'.format(args.data_type))
        get_templates(args.data_type, study_directory)

        # copy templates to appropriate folders
        copy_files()

    else:
        logger.info('Project :' + args.project_name + ' doesn\'t exists')
        new_project = input('Do you want to create a project with this name ? yes/no: ')

        if new_project == 'yes':
            pass
        else:
            pass


    # If metadata/raw files : copy them to appropriate folders
    if args.raw_files:
        pass

    if args.mapping_files:
        pass