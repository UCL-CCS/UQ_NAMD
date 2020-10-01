#!/bin/bash

#n_drugs=2
#ldrugs="g15 lig0"
n_drugs=1
drug="g15"
n_replicas=3

# Define path to reference template for files that are not encoded nor copied
path_template=${PATH_UQNAMD}/template

# Model Builder
    cd $drug/build
    tleap -s -f tleap.in > tleap.log
    awk -f ${path_template}/$drug/build/constraint.awk complex.pdb ${path_template}/$drug/constraint/prot.pdb > ../constraint/cons.pdb
    cd ../fe/build
    ante-MMPBSA.py -p ../../build/complex.prmtop -c com.top -r rec.top -l lig.top -s :129-100000 -n :128
    cd ../../../

# Equilibration simulation
for step in {0..2}; do
        if [ -s ${drug}/build/complex.prmtop ]; then
           srun namd2 +replicas 3 ${drug}/replica-confs/eq$step-replicas.conf &
           sleep 5
        fi
    wait
done

# simulation
for step in {1..1}; do
        if [ -s ${drug}/build/complex.prmtop ]; then
           srun  namd2 +replicas 3 ${drug}/replica-confs/sim$step-replicas.conf &
           sleep 5
        fi
    wait
done

# MMPB(GB)SA
    for i in $(seq 1 $n_replicas); do
        cd $drug/fe/mmpbsa/rep$i
        srun  -N 1 MMPBSA.py.MPI -i ${path_template}/mmpbsa.in -sp ../../../build/complex.prmtop -cp ../../build/com.top -rp ../../build/rec.top -lp ../../build/lig.top -y ../../../replicas/rep$i/simulation/sim1.dcd
        sleep 3
        cd ../../../../
    done
wait

    for i in $(seq 1 $n_replicas); do
        cd $drug/fe/mmpbsa/rep$i
        xargs -d '\n' -I cmd -P 9 /bin/bash -c 'cmd'  <<EOF &
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

    for i in $(seq 1 $n_replicas); do
        cd $drug/fe/mmpbsa/rep$i
        rm _MMPBSA_*.{0..47} reference.frc *.pdb *.inpcrd *.mdin* *.out
        cd ../../../../
    done

echo "drug,replica,binding_energy_avg,binding_energy_stdev" > output.csv
    for i in $(seq 1 $n_replicas); do
        cd $drug/fe/mmpbsa/rep$i
        tmp_str=$(awk '{if(index($0, "DELTA TOTAL")> 0) {count++}; if(count>1) { print $3 "," $4; count=0}} ' ./FINAL_RESULTS_MMPBSA.dat)
        cd ../../../../
        echo "$drug,$i,$tmp_str" >> output.csv
    done
