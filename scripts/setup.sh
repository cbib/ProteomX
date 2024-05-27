#!/usr/bin/env bash

usage ()
{
  echo 'Usage : setup.sh --verbose --conda_update --conda_install'
  exit
}

POSITIONAL=()
while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    -v|--verbose)
    VERBOSE=YES
    shift # past argument
    ;;
    -cu|--conda_update)
    CONDA_UPDATE=YES
    shift # past argument
    ;;
    *)    # unknown option
    POSITIONAL+=("$1") # save it in an array for later
    shift # past argument
    ;;
esac
done


if [[ "$VERBOSE" = "" ]]; then
    VERBOSE=NO
fi

if [ "$CONDA_UPDATE" = "" ]
then
    CONDA_UPDATE=NO
fi


if [[ -n $1 ]]; then
    echo "Last line of file specified as non-opt/last argument:"
    tail -1 "$1"
fi

logs_dir="$(pwd)/logs"
echo $logs_dir
if [ ! -d "${logs_dir}" ]; then
  mkdir $logs_dir
fi
LOG_FILE="install.log"
exec 3>&1 1>>$logs_dir"/"${LOG_FILE} 2>&1

check_dir_and_exit() {
  dir=$1
  step=$2
  if [ ! -d "${dir}" ]; then
	  echo "$(date)""|${step} => ERROR : missing directory ${dir} ... program exiting" | tee /dev/fd/3
	  exit 1
	else
	  echo "$(date)""|${step} => FOUND dir  ${dir}" | tee /dev/fd/3
	fi
}

check_file_and_exit() {
  file=$1
  step=$2
  if [ ! -f "${file}" ]; then
	  echo "$(date)""|${step} => ERROR : missing file ${file} ... program exiting" | tee /dev/fd/3
	  exit 1
	else
	  echo "$(date)""|${step} => FOUND file ${file}" | tee /dev/fd/3
	fi
}


check_resources() {
  root_dir=$1
  echo "$(date)""|CHECK RESOURCES => SEARCH for resources in ${root_dir}" | tee /dev/fd/3

  #check scripts dir
  check_dir_and_exit  "${root_dir}/scripts/" "CHECK RESOURCES"
  check_file_and_exit "${root_dir}/scripts/analyze_test_dataset.sh" "CHECK RESOURCES"
  check_file_and_exit "${root_dir}/scripts/analyze_test_dataset_docker.sh" "CHECK RESOURCES"
  check_file_and_exit "${root_dir}/scripts/retrieve_test_dataset.sh" "CHECK RESOURCES"
  check_file_and_exit "${root_dir}/scripts/retrieve_test_dataset_docker.sh" "CHECK RESOURCES"
  check_file_and_exit "${root_dir}/scripts/Docker_run.sh" "CHECK RESOURCES"
  check_file_and_exit "${root_dir}/scripts/Conda_run.sh" "CHECK RESOURCES"
  check_file_and_exit "${root_dir}/scripts/run_tests.sh" "CHECK RESOURCES"

  #check config dir
  check_dir_and_exit  "${root_dir}/config_files/" "CHECK RESOURCES"
  check_dir_and_exit  "${root_dir}/config_files/conda" "CHECK RESOURCES"
  check_file_and_exit "${root_dir}/config_files/conda/template_39.yml" "CHECK RESOURCES"

  #check config dir
  check_dir_and_exit  "${root_dir}/data/" "CHECK RESOURCES"

  #check backend dir
  check_dir_and_exit  "${root_dir}/backend/" "CHECK RESOURCES"
  check_file_and_exit "${root_dir}/backend/ACP.R" "CHECK RESOURCES"
  check_file_and_exit "${root_dir}/backend/CV.py" "CHECK RESOURCES"
  check_file_and_exit "${root_dir}/backend/Snakefile" "CHECK RESOURCES"
  check_file_and_exit "${root_dir}/backend/Snakefile_docker" "CHECK RESOURCES"
  check_file_and_exit "${root_dir}/backend/analyse_exploratoire.R" "CHECK RESOURCES"
  check_file_and_exit "${root_dir}/backend/clean_na.py" "CHECK RESOURCES"
  check_file_and_exit "${root_dir}/backend/divide.py" "CHECK RESOURCES"
  check_file_and_exit "${root_dir}/backend/enrichment_gprofiler.R" "CHECK RESOURCES"
  check_file_and_exit "${root_dir}/backend/excel_to_csv.py" "CHECK RESOURCES"
  check_file_and_exit "${root_dir}/backend/export_files_for_biologists.py" "CHECK RESOURCES"
  check_file_and_exit "${root_dir}/backend/filter_data.py" "CHECK RESOURCES"
  check_file_and_exit "${root_dir}/backend/functions_analysis.py" "CHECK RESOURCES"
  check_file_and_exit "${root_dir}/backend/functions_preprocessing.py" "CHECK RESOURCES"
  check_file_and_exit "${root_dir}/backend/functions_quality_check.py" "CHECK RESOURCES"
  check_file_and_exit "${root_dir}/backend/gene_name.py" "CHECK RESOURCES"
  check_file_and_exit "${root_dir}/backend/heatmaps.R" "CHECK RESOURCES"
  check_file_and_exit "${root_dir}/backend/helpers.py" "CHECK RESOURCES"
  check_file_and_exit "${root_dir}/backend/mapping.py" "CHECK RESOURCES"
  check_file_and_exit "${root_dir}/backend/overlap.py" "CHECK RESOURCES"
  check_file_and_exit "${root_dir}/backend/paths.py" "CHECK RESOURCES"
  check_file_and_exit "${root_dir}/backend/preprocessing.py" "CHECK RESOURCES"
  check_file_and_exit "${root_dir}/backend/ratio.py" "CHECK RESOURCES"
  check_file_and_exit "${root_dir}/backend/reduce.py" "CHECK RESOURCES"
  check_file_and_exit "${root_dir}/backend/set_comparison.py" "CHECK RESOURCES"
  check_file_and_exit "${root_dir}/backend/statistical_test.py" "CHECK RESOURCES"
  check_file_and_exit "${root_dir}/backend/volcano_plot.R" "CHECK RESOURCES"

  echo $(date)"|CHECK RESOURCES => All resources found in ${root_dir}" | tee /dev/fd/3

}

create_env(){
    env=$1
    yaml=$2
    template_yaml=$3
    conda_dir_path=$4
    env_exist="$(echo "$(conda env list)" | awk -v env_name="${env}" '{if ($1==env_name){print $1}}')"
    if [[ -z $env_exist ]]; then
      echo "$(date)""|CONDA INSTALL   => CREATE environment = ${env}"  | tee /dev/fd/3
      ####################################################################################################################
      ## 6.1 - check conda environment yaml file exists else create it based on template minimal form#######################
      ####################################################################################################################
      echo "$(date)""|CONDA INSTALL   => BUILD conda environment YAML file based on ${template_yaml}"  | tee /dev/fd/3
      if [[ ! -f $yaml ]]; then
          touch "$yaml"
          prefix="${conda_dir_path}/envs/${env}"
          echo "$(date)""|CONDA INSTALL   => CREATE environment YAML file = ${yaml}"  | tee /dev/fd/3
          awk -v env_name="${env}"  -v prefix="$prefix" '{ sub(/name:/, "name: "env_name); sub(/prefix:/, "prefix: "prefix); print }' "$template_yaml" > "$yaml"
      else
        echo "$(date)""|CONDA INSTALL   => FOUND ${env} conda environment YAML file = ${yaml}"  | tee /dev/fd/3
      fi
      conda env create --file "${yaml}"
    else
      echo "$(date)""|CONDA INSTALL   => FOUND ${env_exist} conda environment"  | tee /dev/fd/3

    fi

}

unameOut="$(uname -s)"
machine=""
case "${unameOut}" in
    Linux*)     machine="Linux";;
    Darwin*)    machine="Mac";;
    CYGWIN*)    machine="Cygwin";;
    MINGW*)     machine="MinGw";;
    *)          machine="UNKNOWN:${unameOut}"
esac

if [[ ${VERBOSE} == YES ]]; then
  echo "$(date)""|WORKING SYSTEM   => FOUND ${machine} environment"  | tee /dev/fd/3
fi

####PROGRAM START TO INSTALL

ROOT_DIR="$(cd "$(pwd)/" && pwd)"
CONFIG_DIR="$(cd "$(pwd)/config_files" && pwd)"
SCRIPTS_DIR="$(cd "$(pwd)/scripts" && pwd)"
#source "$CURRENT_DIR/scripts/utils.sh"
ENV_NAME="proteomx"

check_resources "$ROOT_DIR"


####################################################################################################################
## 1 - Detect if anaconda is installed else install it##############################################################
####################################################################################################################
echo "$(date)""|CONDA INSTALL   => SEARCH CONDA INSTALL" | tee /dev/fd/3
#anaconda_path=$(which anaconda)
conda_dir_path=$(echo "$(conda info)"|awk  '/root environment : *|base environment : */{print $4}')
#anaconda_dir_path=$(echo $anaconda_path | sed 's/\(.*\)\/bin\/anaconda$/\1/')
if [[ -z $conda_dir_path ]]; then
  # install Anaconda
  conda_dir_path="$HOME/miniconda3/"
  echo "$(date)""|CONDA INSTALL   => CONDA NOT FOUND  = ${conda_dir_path}" | tee /dev/fd/3
  #wget https://repo.anaconda.com/archive/Anaconda3-2020.07-Linux-x86_64.sh
  #sh -b Anaconda3-2020.07-Linux-x86_64.sh
  echo "$(date)""|CONDA INSTALL   => INSTALL CONDA AT= https://repo.anaconda.com/archive/Anaconda3-2020.07-Linux-x86_64.sh" | tee /dev/fd/3
  exit 1
#  wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
#  chmod +x Miniconda3-latest-Linux-x86_64.sh
#  bash Miniconda3-latest-Linux-x86_64.sh -p "${conda_dir_path}"
else
  echo "$(date)""|CONDA INSTALL   => CONDA FOUND  = ${conda_dir_path}" | tee /dev/fd/3
fi

####################################################################################################################
## 2 - Detect if anaconda is installed so load and update ############################################################
####################################################################################################################
conda_dir_path=$(echo "$(conda info)"|awk  '/base environment : *|root environment : */{print $4}')
if [[ -z $conda_dir_path ]]; then
  echo "$(date)""|ERRORS => NO CONDA INSTALL !!! DID YOU RUN INSTALL.SH ?" | tee /dev/fd/3
  exit 1
fi
echo "$(date)""|CONDA INSTALL   => CONDA PATH = ${conda_dir_path}" | tee /dev/fd/3
echo "$(date)""|CONDA INSTALL   => LOAD CONDA  = $(which conda)" | tee /dev/fd/3
source "$conda_dir_path"/etc/profile.d/conda.sh
if [[ ${CONDA_UPDATE} == YES ]]; then
  echo "$(date)""|CONDA INSTALL   => UPDATE conda" | tee /dev/fd/3
  conda_update_output=$(conda update -y conda)
  echo "$(date)""|CONDA INSTALL   => UPDATE conda OUTPUT START"
  echo "#####"
  echo "${conda_update_output}"
  echo "#####"
  echo "$(date)""|CONDA INSTALL   => UPDATE conda OUTPUT END"
fi


####################################################################################################################
## 3 - check proteomix python 3.9.18 environment exists else create it using yaml file ######################
####################################################################################################################
conda_env="${ENV_NAME}_39"
echo "$(date)""|CONDA INSTALL   => CHECK conda environment = ${conda_env}"  | tee /dev/fd/3


conda_yaml="${ROOT_DIR}/config_files/conda/${ENV_NAME}_39.yml"
conda_template_yaml="${ROOT_DIR}/config_files/conda/template_39.yml"
if [ ! -f "${conda_template_yaml}" ]; then
  echo "$(date)""|CONDA INSTALL   => ERROR : missing file ${conda_template_yaml} ... program exiting" | tee /dev/fd/3
  exit 1
else
  echo "$(date)""|CONDA INSTALL   => FOUND file ${conda_template_yaml}"
  create_env "$conda_env" "$conda_yaml" "$conda_template_yaml" "$conda_dir_path"

  env_exist="$(echo "$(conda env list)" | awk -v env_name="${env}" '{if ($1==env_name){print $1}}')"
  if [[ -n $env_exist ]]; then
     echo "$(date)""|CONDA INSTALL   => environment ${conda_env} was successfully created"  | tee /dev/fd/3
  fi
fi


R_VERSION=$(echo "$(R --version)"|awk  '/R version */{print $3}')
if [[ -z $R_VERSION ]]; then
    echo "$(date)""|R INSTALL   => R NOT FOUND" | tee /dev/fd/3
    exit 1
else
    echo "$(date)""|R INSTALL   => R FOUND VERSION ${R_VERSION}" | tee /dev/fd/3
    echo "$(date)""|R INSTALL   => INSTALLING PACKAGES for R ${R_VERSION}" | tee /dev/fd/3
    # shellcheck disable=SC2164
    cd "${SCRIPTS_DIR}" || exit
    ./setup.R | tee /dev/fd/3
    cd "${ROOT_DIR}" || exit
fi