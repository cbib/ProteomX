#!/usr/bin/env bash
# setup venv
CURRENT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACK_DIR=$CURRENT_DIR/../backend/
VENV_DIR=$CURRENT_DIR/../venv/

source ${VENV_DIR}/bin/activate
export PYTHONPATH=${BACK_DIR}:$PYTHONPATH
snakemake -s ${BACK_DI}/Snakefile