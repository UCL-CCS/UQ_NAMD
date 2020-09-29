#!/bin/bash
# Job Name and Files (also --job-name)
#SBATCH -J mmpbsa
#Output and error (also --output, --error):
#SBATCH -o ./%x.%j.out
#SBATCH -e ./%x.%j.err
#Initial working directory (also --chdir):
#SBATCH -D ./
#Notification and type
#SBATCH --mail-type=NONE
# Wall clock limit:
#SBATCH --time=0:30:00
#SBATCH --no-requeue
#Setup of execution environment
#SBATCH --export=NONE
#SBATCH --get-user-env
#SBATCH --account=pn72qu
##SBATCH --qos=nolimit
##SBATCH --partition=tmp3
##SBATCH --partition=general
#SBATCH --partition=test
#Number of nodes and MPI tasks per node:
##SBATCH --nodes=25
#SBATCH --nodes=3
#SBATCH --ntasks-per-node=48

# Path of the UQ_NAMD project
path_uqnamd=/hppfs/work/pn72qu/di36yax3/tmp/uq_namd2

# Define path to reference template for files that are not encoded nor copied
path_template=${path_uqnamd}/template

# drug should be passed as the first argument to script, but let's just take `g15` right now
#drug=$1
drug=g15

module load slurm_setup
module load amber
source /lrz/sys/applications/amber/amber18/amber.sh

# MMPB(GB)SA
#for drug in "${drugs[@]}"; do
for i in {1..3}; do
    cd $drug/fe/mmpbsa/rep$i
    #srun -N 1 -n 48 MMPBSA.py.MPI -i ../../../../mmpbsa.in -cp ../../build/com.top -rp ../../build/rec.top -lp ../../build/lig.top -y ../../dcd/rep$i.dcd &
    srun -N 1 -n 48 MMPBSA.py.MPI -i ${path_template}/mmpbsa.in -sp ../../../build/complex.prmtop -cp ../../build/com.top -rp ../../build/rec.top -lp ../../build/lig.top -y ../../../replicas/rep$i/simulation/sim1.dcd
    sleep 3
    cd ../../../../
done
wait

for i in {1..3}; do
    cd $drug/fe/mmpbsa/rep$i
    srun -n 1 -N 1 xargs -d '\n' -I cmd -P 9 /bin/bash -c 'cmd'  <<EOF &
cat _MMPBSA_complex_gb.mdout.{0..47} > _MMPBSA_complex_gb.mdout.all
cat _MMPBSA_complex_gb_surf.dat.{0..47} > _MMPBSA_complex_gb_surf.dat.all
cat _MMPBSA_complex_pb.mdout.{0..47} > _MMPBSA_complex_pb.mdout.all
cat _MMPBSA_ligand_gb.mdout.{0..47} > _MMPBSA_ligand_gb.mdout.all
cat _MMPBSA_ligand_gb_surf.dat.{0..47} > _MMPBSA_ligand_gb_surf.dat.all
cat _MMPBSA_ligand_pb.mdout.{0..47} > _MMPBSA_ligand_pb.mdout.all
cat _MMPBSA_receptor_gb.mdout.{0..47} > _MMPBSA_receptor_gb.mdout.all
cat _MMPBSA_receptor_gb_surf.dat.{0..47} > _MMPBSA_receptor_gb_surf.dat.all
cat _MMPBSA_receptor_pb.mdout.{0..47} > _MMPBSA_receptor_pb.mdout.all
EOF

    sleep 3
    cd ../../../../
done
wait

for i in {1..3}; do
    cd $drug/fe/mmpbsa/rep$i
    rm _MMPBSA_*.{0..47} reference.frc *.pdb *.inpcrd *.mdin* *.out
    cd ../../../../
done

echo "drug,replica,binding_energy_avg,binding_energy_stdev" > output.csv
for i in {1..3}; do
    cd $drug/fe/mmpbsa/rep$i
    tmp_str=$(awk '{if(index($0, "DELTA TOTAL")> 0) {count++}; if(count>1) { print $3 "," $4; count=0}} ' ./FINAL_RESULTS_MMPBSA.dat)
    cd ../../../../
    echo "$drug,$i,$tmp_str" >> output.csv
done