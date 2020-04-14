#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski


# TODO : paths non hardcodés
# !!! if it start with a slash = considerate as an absolute path and disturb results with os.path.join


root_dir = "/home/clescoat/Documents/"
logpath = "ProteomX_sprint/log"

config_dir = "ProteomX_sprint/config_files"
data_dir = "ProteomX_sprint/data"
templates_dir = "ProteomX_sprint/templates"
snakefile_dir = "ProteomX_sprint/snakefiles"

paths = {
    'root_dir': "/home/clescoat/Documents",
    'config_dir': "ProteomX_sprint/config_files",
    'data_dir': "ProteomX_sprint/data",
    'snakefile_dir': "ProteomX_sprint/snakefiles",
    'templates_dir': "ProteomX_sprint/templates"
}
