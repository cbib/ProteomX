#!/usr/bin/env bash

# setup venv
while getopts "i:t:r:s:" opt; do
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
		s)
			snakefile=$OPTARG
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

echo "Command line : snakemake -p -s ${BACK_DIR}/$snakefile --config file_id="$file" target="$target" "
echo "------------ SNAKEMAKE"
if [ $rerun = "False" ]
then
	snakemake -s $snakefile -p -s ${BACK_DIR}/$snakefile --config file_id="$file" target="$target"

elif [ $rerun = "True" ]
then
	snakemake -s $snakefile -p -s ${BACK_DIR}/$snakefile --config file_id="$file" target="$target" -R "$target"
fi

