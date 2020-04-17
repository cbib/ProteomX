#!/usr/bin/env bash
# setup venv
CURRENT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACK_DIR=$CURRENT_DIR/../backend/
snakemake -d / -p -s ${BACK_DIR}/Snakefile --config project="proteomX" analysis_name="sample"