#!/usr/bin/bash
#SBATCH --account=bgmp
#SBATCH --partition=bgmp
#SBATCH --cpus-per-task=1
#SBATCH --time=10:00:00

grep -v "^@" $1 | cut -f 3 | sort -n | uniq -c > chrom_counts.txt