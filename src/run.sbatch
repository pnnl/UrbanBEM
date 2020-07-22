#!/bin/bash

#SBATCH -A urbanbem
#SBATCH -N 10
#SBATCH -p slurm7
#SBATCH -t 10:00:00
#SBATCH --exclusive
#SBATCH -o run.out
#SBATCH -e run.err
#SBATCH --job-name scratch

module unload python
module load python/anaconda3.2019.3
source /share/apps/python/anaconda3.2019.3/etc/profile.d/conda.sh
module load singularity/3.2.0

make simulate
