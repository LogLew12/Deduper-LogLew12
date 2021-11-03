#!/usr/bin/bash
#SBATCH --account=bgmp
#SBATCH --partition=bgmp
#SBATCH --cpus-per-task=8
#SBATCH --mail-user='llewis3@uoregon.edu'
#SBATCH --mail-type=END,FAIL
#SBATCH --time=10:00:00

samtools sort -o "Sorted_${1}" -O sam $1
python Deduper.py -f Sorted_${1} -u STL96.txt