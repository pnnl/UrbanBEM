#!/bin/bash

#SBATCH -A urbanbem
#SBATCH -N 12
#SBATCH -p slurm7
#SBATCH -t 10:00:00
#SBATCH --exclusive
#SBATCH -o run.out
#SBATCH -e run.err
#SBATCH --job-name scratch

module unload python
module load python/miniconda3.9
source /share/apps/python/miniconda3.9/etc/profile.d/conda.sh

python standard_excel_processor.py

module load singularity/3.2.0

make simulate
