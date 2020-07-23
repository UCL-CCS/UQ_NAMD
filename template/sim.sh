#!/bin/bash
# Job Name and Files (also --job-name)
#SBATCH -J ADRP
#Output and error (also --output, --error):
#SBATCH -o ./%x.%j.out
#SBATCH -e ./%x.%j.err
#Initial working directory (also --chdir):
#SBATCH -D ./
#Notification and type
#SBATCH --mail-type=NONE
# Wall clock limit:
#SBATCH --time=10:00:00
#SBATCH --no-requeue
#Setup of execution environment
#SBATCH --export=NONE
#SBATCH --get-user-env
#SBATCH --account=pn72qu
#SBATCH --partition=general
##SBATCH --qos=nolimit
#Number of nodes and MPI tasks per node:
#SBATCH --nodes=25
#SBATCH --ntasks-per-node=48

#constraints are optional
#--constraint="scratch&work"

module load slurm_setup
module load namd

n_drugs=1

# Path of the UQ_NAMD project
path_uqnamd=/hppfs/work/pn72qu/di36yax3/tmp/uq_namd2

# Define path to reference template for files that are not encoded nor copied
path_template=${path_uqnamd}/template

for step in {0..2}; do
    for drug in `ls -d g15`; do
        if [ -s ${drug}/build/complex.prmtop ]; then
           srun -N 25 -n $((1*$SLURM_NTASKS/$n_drugs)) namd2 +replicas 25 ${drug}/replica-confs/eq$step-replicas.conf &
           sleep 5
        fi
    done
    wait
done

# simulation
for step in {1..1}; do
    for drug in `ls -d g15`; do
        if [ -s ${drug}/build/complex.prmtop ]; then
           srun -N 25 -n $((1*$SLURM_NTASKS/$n_drugs)) namd2 +replicas 25 ${drug}/replica-confs/sim$step-replicas.conf &
           sleep 5
        fi
    done
    wait
done
