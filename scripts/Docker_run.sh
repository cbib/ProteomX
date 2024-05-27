#!/usr/bin/env bash

usage ()
{
  echo ' Usage : Docker_run.sh -i <project_folder> --verbose'
  echo " Options:"
  echo "            -i|--project_folder     Project folder name (same as for xlsx file)."
  echo "            -v|--verbose            Verbose mode."
  echo
  exit
}

POSITIONAL=()
while [[ $# -gt 0 ]]; do
  key="$1"

  case $key in
  -i | --project_folder)
    PROJECT_FOLDER="$2"
    shift # past argument
    shift # past value
    ;;
  --verbose)
    VERBOSE=YES
    shift # past argument
    ;;
  *)                   # unknown option
    POSITIONAL+=("$1") # save it in an array for later
    shift              # past argument
    ;;
  esac
done

if [ "$PROJECT_FOLDER" = "" ]; then
  usage
fi



verbose=""
if [[ ${VERBOSE} ]]; then
  verbose="--verbose"
fi
if [[ -n $1 ]]; then
  echo "Last line of file specified as non-opt/last argument:"
  tail -1 "$1"
fi

## 1 - check project structure (log file, data dir, etc)

BACKEND_DIR="$(cd "/backend" && pwd)"
DATA_DIR="$(cd "/data" && pwd)"

declare -A errors_detected
#### CHECK CONSISTENCY OF THE PROJECT FOLDER
if [ ! -d "${DATA_DIR}/${PROJECT_FOLDER}" ]; then
     errors_detected["project_folder"]="$(date)""|  Directory not found => ${DATA_DIR}/${PROJECT_FOLDER}"
fi

if [ ! -d "${DATA_DIR}/${PROJECT_FOLDER}/mapping" ]; then
     errors_detected["mapping_dir_error"]="$(date)""|  Directory not found => ${DATA_DIR}/${PROJECT_FOLDER}/mapping"
fi

if [ ! -f "${DATA_DIR}/${PROJECT_FOLDER}/mapping/mapping_${PROJECT_FOLDER}.csv" ]; then
     errors_detected["mapping_file_error"]="$(date)""|  Input file not found => ${DATA_DIR}/${PROJECT_FOLDER}/mapping/mapping_${PROJECT_FOLDER}.csv"
fi

if [ ! -f "${DATA_DIR}/${PROJECT_FOLDER}/mapping/comparison_${PROJECT_FOLDER}.csv" ]; then
     errors_detected["mapping_comparison_file_error"]="$(date)""|  Input file not found => ${DATA_DIR}/${PROJECT_FOLDER}/mapping/comparison_${PROJECT_FOLDER}.csv"
fi

if [ ! -d "${DATA_DIR}/${PROJECT_FOLDER}/xlsx" ]; then
     errors_detected["xlsx_dir_error"]="$(date)""|  Directory not found => ${DATA_DIR}/${PROJECT_FOLDER}/xlsx/"
fi
if [ ! -f "${DATA_DIR}/${PROJECT_FOLDER}/xlsx/${PROJECT_FOLDER}.xlsx" ]; then
     errors_detected["xlsx_file_error"]="$(date)""|  Input file not found => ${DATA_DIR}/${PROJECT_FOLDER}/xlsx/${PROJECT_FOLDER}.xlsx"
fi

if [ ! -f "${DATA_DIR}/${PROJECT_FOLDER}/config_file.json" ]; then
     errors_detected["config_file_error"]="$(date)""|  Configuration file not found => ${DATA_DIR}/${PROJECT_FOLDER}/config_file.json"
fi

error_accepted=0
if [ "${#errors_detected[@]}" -eq "${error_accepted}" ]; then
    echo   "$(date)"" - SUCCESS - Everything looks good - Analysis Starting...."

    snakemake -s "${BACKEND_DIR}"/Snakefile_docker -p --cores 1 --config analysis="${PROJECT_FOLDER}" target=divided &&
    snakemake -s "${BACKEND_DIR}"/Snakefile_docker -p --cores 1 --config analysis="${PROJECT_FOLDER}" target=filtered_data &&
    snakemake -s "${BACKEND_DIR}"/Snakefile_docker -p --cores 1 --config analysis="${PROJECT_FOLDER}" target=analyse_exploratoire_tous_echantillons &&
    snakemake -s "${BACKEND_DIR}"/Snakefile_docker -p --cores 1 --config analysis="${PROJECT_FOLDER}" target=heatmaps_exploratoire &&
    snakemake -s "${BACKEND_DIR}"/Snakefile_docker -p --cores 1 --config analysis="${PROJECT_FOLDER}" target=acp_exploratoire &&
    snakemake -s "${BACKEND_DIR}"/Snakefile_docker -p --cores 1 --config analysis="${PROJECT_FOLDER}" target=heatmaps_post_treatment &&
    snakemake -s "${BACKEND_DIR}"/Snakefile_docker -p --cores 1 --config analysis="${PROJECT_FOLDER}" target=acp_post_treatment &&
    snakemake -s "${BACKEND_DIR}"/Snakefile_docker -p --cores 1 --config analysis="${PROJECT_FOLDER}" target=enrichment &&
    snakemake -s "${BACKEND_DIR}"/Snakefile_docker -p --cores 1 --config analysis="${PROJECT_FOLDER}" target=volcano_plot &&
    snakemake -s "${BACKEND_DIR}"/Snakefile_docker -p --cores 1 --config analysis="${PROJECT_FOLDER}" target=set_comparison &&
    snakemake -s "${BACKEND_DIR}"/Snakefile_docker -p --cores 1 --config analysis="${PROJECT_FOLDER}" target=export/stats &&
    snakemake -s "${BACKEND_DIR}"/Snakefile_docker -p --cores 1 --config analysis="${PROJECT_FOLDER}" target=export/selection_from_stats --report report.html&&
    rm -f Rplots.pdf

else
    echo   "$(date)"" - ERROR - There are problems in your project folder!"
    for K in "${!errors_detected[@]}"; do
      echo "$K : ${errors_detected[$K]}"
    done
    exit
fi