#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski
import os
import pathlib

global_root_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
assert os.path.exists(global_root_dir), "Global dir %s does not exists" % global_root_dir

global_backend_dir = pathlib.Path(global_root_dir, "backend")
assert global_backend_dir.exists(), "Global dir %s does not exists" % global_backend_dir

global_scripts_dir = pathlib.Path(global_root_dir, "scripts")
assert global_scripts_dir.exists(), "Global dir %s does not exists" % global_scripts_dir

global_data_dir = pathlib.Path(global_root_dir, "data_folder")
assert global_data_dir.exists(), "Global dir %s does not exists" % global_data_dir

global_resources_dir = pathlib.Path(global_root_dir, "resources")
assert global_resources_dir.exists(), "Global dir %s does not exists" % global_resources_dir

global_annotation_dir = pathlib.Path(global_root_dir, "resources/annotation_data")
assert global_annotation_dir.exists(), "Global dir %s does not exists" % global_annotation_dir

global_config_dir = pathlib.Path(global_root_dir, "config_files")
assert global_config_dir.exists(), "Global dir %s does not exists" % global_config_dir

global_logging_config_file = pathlib.Path(global_config_dir, "logging.conf")
assert global_logging_config_file.exists(), "Logging config file does not exists" % global_logging_config_file

paths = {
    'root_dir': global_root_dir,
    'config_dir': global_config_dir,
    'data_dir': global_data_dir,
    'annot_dir' : global_annotation_dir,
    'resources_dir': global_resources_dir,
    "backend_dir": global_backend_dir,
    'scripts_dir': global_scripts_dir,
    "logging_config": global_logging_config_file
}
