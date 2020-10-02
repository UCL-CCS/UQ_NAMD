#!/bin/bash

## job name
#SBATCH --job-name=uq_namd

## stdout file
#SBATCH --output=log-out.%j

## stderr file
#SBATCH --error=log-err.%j

## wall time in format MINUTES:SECONDS
#SBATCH --time=01:00:00

## number of nodes
#SBATCH --nodes=1

## tasks per node
#SBATCH --tasks-per-node=28

## queue name
#SBATCH --partition=fast

## grant
#SBATCH --account=vecma2020
#SBATCH --mail-user=jalal.lakhlili@ipp.mpg.de


export MODULEPATH=$MODULEPATH:/home/plgrid-groups/plggvecma/.qcg-modules

# Path of the UQ_NAMD project (the CODE), Campaign in SCRATCH
export PATH_UQNAMD=/hppfs/work/pn72wa/ga89wen3/UQ_NAMD
export PYTHONPATH=$PYTHONPATH:$PATH_UQNAMD/utils

# For EQI
export EASYPJ_CONFIG=conf.sh

module load slurm_setup
module load amber
source /lrz/sys/applications/amber/amber18/amber.sh
module load namd

# Run the UQ code
python3 namd_init_pj.py > namd_init_pj.${SLURM_JOBID}.log
