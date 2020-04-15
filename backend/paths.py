#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski
import os
import pathlib

global_root_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
assert os.path.exists(global_root_dir), "Global dir %s do not exists" % global_root_dir

global_backend_dir = pathlib.Path(global_root_dir, "backend")
assert global_backend_dir.exists(), "Global dir %s do not exists" % global_backend_dir

global_data_dir = pathlib.Path(global_root_dir, "data")
assert global_data_dir.exists(), "Global dir %s do not exists" % global_data_dir

global_config_dir = pathlib.Path(global_root_dir, "config_files")
assert global_config_dir.exists(), "Global dir %s do not exists" % global_config_dir

paths = {
    'root_dir': global_root_dir,
    'config_dir': global_config_dir,
    'data_dir': global_data_dir,
    "backend_dir": global_backend_dir
}
