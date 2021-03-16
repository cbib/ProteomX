#!/usr/bin/env bash

# setup venv
while getopts "i:t:r:s:R:n:" opt; do
	case $opt in
		t)
			target=$OPTARG
			;;
		i)
			file=$OPTARG
			;;
		r)
			rerun=$OPTARG
			;;
		R)
			rule=$OPTARG
			;;
		s)
			snakefile=$OPTARG
			;;
		n)
			dryrun=$OPTARG
			;;
		\?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
	esac
done


CURRENT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACK_DIR=$CURRENT_DIR/../backend/
VENV_DIR=$CURRENT_DIR/../venv/

source ${VENV_DIR}/bin/activate
export PYTHONPATH=${BACK_DIR}:$PYTHONPATH


echo "Parameters :"
echo "------------"
echo "File ID : $file"
echo "Snakefile name : $snakefile"
echo "Rule to reach: $target"
echo "Step already done : $rerun"
echo "Dry-run : $dryrun"
echo "------------ "

if [ $dryrun == "False" ]
then
  if [ $rerun == "False" ]
  then
    echo "Command line : snakemake -j1 -p -s ${BACK_DIR}/$snakefile --config file_id="$file" target="$target" "
    snakemake -s $snakefile -j1 -p -s ${BACK_DIR}/$snakefile --config file_id="$file" target="$target"

  elif [ $rerun == "True" ]
  then
    echo "Command line : snakemake -j1 -p -s ${BACK_DIR}/$snakefile --config file_id="$file" target="$target" -R "$rule" "
    snakemake -s $snakefile -j1 -p -s ${BACK_DIR}/$snakefile --config file_id="$file" target="$target" -R "$rule"
  fi

elif [ $dryrun == "True" ]
then
  if [ $rerun == "False" ]
  then
    echo "Command line : snakemake -j1 -p -n -s ${BACK_DIR}/$snakefile --config file_id="$file" target="$target" "
    snakemake -s $snakefile -j1 -p -n -s ${BACK_DIR}/$snakefile --config file_id="$file" target="$target"

  elif [ $rerun == "True" ]
  then
    echo "Command line : snakemake -j1 -p -n -s ${BACK_DIR}/$snakefile --config file_id="$file" target="$target" -R "$rule" "
    snakemake -s $snakefile -j1 -p -n -s ${BACK_DIR}/$snakefile --config file_id="$file" target="$target" -R "$rule"
  fi
fi

