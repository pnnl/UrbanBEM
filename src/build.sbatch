#!/bin/csh

#SBATCH -A urbanbem
#SBATCH -N 1
#SBATCH -p slurm7
#SBATCH -t 05:00:00
#SBATCH --exclusive
#SBATCH -o run.out
#SBATCH -e run.err
#SBATCH --job-name scratch

module load singularity/3.2.0

singularity build --remote ../../../_singularity_img/openstudio_python.sif Singularity.recipe