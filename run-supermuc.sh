#!/bin/bash

# Job Name and Files (also --job-name)
#SBATCH -J ADRP+MMPBSA
#Output and error (also --output, --error):
#SBATCH -o ./%x.%j.out
#SBATCH -e ./%x.%j.err
#Initial working directory (also --chdir):
#SBATCH -D ./
#Notification and type
#SBATCH --mail-type=NONE
# Wall clock limit:
#SBATCH --time=20:00:00
#SBATCH --no-requeue
#Setup of execution environment
#SBATCH --export=NONE
#SBATCH --get-user-env
#SBATCH --account=pn72qu
#SBATCH --partition=general
##SBATCH --partition=micro
##SBATCH --partition=test
##SBATCH --qos=nolimit
#Number of nodes and MPI tasks per node:
#SBATCH --nodes=500
##SBATCH --nodes=3
#SBATCH --ntasks-per-node=48

#constraints are optional
#--constraint="scratch&work"

module load slurm_setup
source /lrz/sys/applications/amber/amber18/amber.sh

# Activate Python environment featuring EasyVVUQ, EQI, QCG-PJ, Chaospy
source /path/to/python/env/uq/bin/activate

# Path of the UQ_NAMD project (the CODE), Campaign in SCRATCH
export PATH_UQNAMD=/path/to/UQ_NAMD
export PYTHONPATH=$PYTHONPATH:$PATH_UQNAMD/utils

# For EQI
export EASYPJ_CONFIG=conf.sh

# Run the UQ code
python3 namd_init.py > namd_init.${SLURM_JOBID}.log
