#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski
import os
import pathlib


global_root_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
assert os.path.exists(global_root_dir), "Global dir %s does not exists" % global_root_dir

print(global_root_dir)
global_backend_dir = pathlib.Path(global_root_dir, "backend")
assert global_backend_dir.exists(), "Global dir %s does not exists" % global_backend_dir

global_data_dir = pathlib.Path(global_root_dir, "data")
assert global_data_dir.exists(), "Global dir %s does not exists" % global_data_dir

global_logging_config_file = pathlib.Path(global_root_dir, "logging.conf")
print(global_logging_config_file)
assert global_logging_config_file.exists(), "Logging config file does not exists" % global_logging_config_file

paths = {
    'root_dir': global_root_dir,
    'data_dir': global_data_dir,
    "backend_dir": global_backend_dir,
    "logging_config": global_logging_config_file
}
