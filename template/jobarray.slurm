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
##SBATCH --time=00:30:00
#SBATCH --no-requeue
#Setup of execution environment
#SBATCH --export=NONE
#SBATCH --get-user-env
#SBATCH --account=pn72qu
#SBATCH --partition=general
##SBATCH --partition=micro
#Number of nodes and MPI tasks per node:
#SBATCH --nodes=25
##SBATCH --nodes=1
#SBATCH --ntasks-per-node=48
#constraints are optional
#--constraint="scratch&work"
##SBATCH --array=25-29
#same program but different input data

#PATH_UQNAMD="/hppfs/work/pn72qu/di36yax3/tmp/uq_namd2/uq_namd2_continuous"
echo "Path of the UQ NAMD project: "$path_uq

bash $path_uq/template/full.jobarray.sh $SLURM_ARRAY_TASK_ID $path_uq
