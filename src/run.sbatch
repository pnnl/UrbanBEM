#!/bin/bash

#SBATCH -A urbanbem
#SBATCH -N 10
#SBATCH -p slurm7
#SBATCH -t 10:00:00
#SBATCH --exclusive
#SBATCH -o run.out
#SBATCH -e run.err
#SBATCH --job-name scratch

module load singularity/3.2.0

make clean

make all
