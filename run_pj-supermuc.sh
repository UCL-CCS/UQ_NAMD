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
#SBATCH --time=00:30:00
#SBATCH --no-requeue
#Setup of execution environment
#SBATCH --export=NONE
#SBATCH --get-user-env
#SBATCH --account=pn72qu
##SBATCH --partition=general
#SBATCH --partition=micro
##SBATCH --partition=test
##SBATCH --qos=nolimit
#Number of nodes and MPI tasks per node:
##SBATCH --nodes=25
#SBATCH --nodes=3
#SBATCH --ntasks-per-node=48

#constraints are optional
#--constraint="scratch&work"

module load slurm_setup
module load amber
source /lrz/sys/applications/amber/amber18/amber.sh
module load namd

# Path of the UQ_NAMD project (the CODE), Campaign in SCRATCH
export PATH_UQNAMD=/hppfs/work/pn72wa/ga89wen3/UQ_NAMD
export PYTHONPATH=$PYTHONPATH:$PATH_UQNAMD/utils

# For QCG-PilotJob usage
ENCODER_MODULES="encoders"
export ENCODER_MODULES
#export EASYPJ_CONFIG=conf.sh

# Run the UQ code
python3 namd_init_pj.py > namd_init_pj.${SLURM_JOBID}.log
