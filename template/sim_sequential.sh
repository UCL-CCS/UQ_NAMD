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
#SBATCH --time=00:30:00
#SBATCH --no-requeue
#Setup of execution environment
#SBATCH --export=NONE
#SBATCH --get-user-env
#SBATCH --account=pn72qu
##SBATCH --partition=general
#SBATCH --partition=test
##SBATCH --qos=nolimit
#Number of nodes and MPI tasks per node:
##SBATCH --nodes=25
#SBATCH --nodes=3
#SBATCH --ntasks-per-node=48

#constraints are optional
#--constraint="scratch&work"

module load slurm_setup
module load namd

# Path of the UQ_NAMD project
path_uqnamd=/hppfs/work/pn72qu/di36yax3/tmp/uq_namd2

# Define path to reference template for files that are not encoded nor copied
path_template=${path_uqnamd}/template

# drug should be passed as the first argument to script, but let's just take `g15` right now
#drug=$1
drug=g15

if [ -s ${drug}/build/complex.prmtop ]; then
	srun -N 3 -n $SLURM_NTASKS namd2 +replicas 3 ${drug}/replica-confs/eq0-replicas.conf
	wait
	srun -N 3 -n $SLURM_NTASKS namd2 +replicas 3 ${drug}/replica-confs/eq1-replicas.conf
	wait           
	srun -N 3 -n $SLURM_NTASKS namd2 +replicas 3 ${drug}/replica-confs/eq2-replicas.conf
	wait
	srun -N 3 -n $SLURM_NTASKS namd2 +replicas 3 ${drug}/replica-confs/sim1-replicas.conf
fi
