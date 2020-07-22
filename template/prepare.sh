#!/bin/bash
# Job Name and Files (also --job-name)
#SBATCH -J tleap
#Output and error (also --output, --error):
#SBATCH -o ./%x.%j.out
#SBATCH -e ./%x.%j.err
#Initial working directory (also --chdir):
#SBATCH -D ./
#Notification and type
#SBATCH --mail-type=NONE
# Wall clock limit:
#SBATCH --time=0:10:00
#SBATCH --no-requeue
#Setup of execution environment
#SBATCH --export=NONE
#SBATCH --get-user-env
#SBATCH --account=pn72qu
##SBATCH --qos=nolimit
##SBATCH --partition=tmp3
#SBATCH --partition=test
#Number of nodes and MPI tasks per node:
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=48

module load slurm_setup
module load amber
source /lrz/sys/applications/amber/amber18/amber.sh

# Path of the UQ_NAMD project
path_uqnamd=/hppfs/work/pn72qu/di36yax3/tmp/uq_namd

# Define path to reference template for files that are not encoded nor copied
path_template=${path_uqnamd}/template

# Model Builder
for drug in g15; do
    cd $drug/build
    tleap -s -f tleap.in > tleap.log
    awk -f ${path_template}/$drug/build/constraint.awk complex.pdb ${path_template}/$drug/constraint/prot.pdb > ../constraint/cons.pdb
    cd ../..
done
