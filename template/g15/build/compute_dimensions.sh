#!/bin/bash
path_dim0="../replica-confs/dim0.conf"
xbox=`grep "O   WAT" complex.pdb | awk '{print $6}' | awk -f /hppfs/work/pn72qu/di36yax3/tmp/uq_namd2_wouter/template/g15/build/max-min.awk | awk '{print $NF}'`
ybox=`grep "O   WAT" complex.pdb | awk '{print $7}' | awk -f /hppfs/work/pn72qu/di36yax3/tmp/uq_namd2_wouter/template/g15/build/max-min.awk | awk '{print $NF}'`
zbox=`grep "O   WAT" complex.pdb | awk '{print $8}' | awk -f /hppfs/work/pn72qu/di36yax3/tmp/uq_namd2_wouter/template/g15/build/max-min.awk | awk '{print $NF}'`
x0=`grep "O   WAT" complex.pdb | awk '{print $6}' | awk -f /hppfs/work/pn72qu/di36yax3/tmp/uq_namd2_wouter/template/g15/build/max-min.awk | awk '{print ($1+$2)/2}'`
y0=`grep "O   WAT" complex.pdb | awk '{print $7}' | awk -f /hppfs/work/pn72qu/di36yax3/tmp/uq_namd2_wouter/template/g15/build/max-min.awk | awk '{print ($1+$2)/2}'`
z0=`grep "O   WAT" complex.pdb | awk '{print $8}' | awk -f /hppfs/work/pn72qu/di36yax3/tmp/uq_namd2_wouter/template/g15/build/max-min.awk | awk '{print ($1+$2)/2}'`
printf "cellBasisVector1\t %6.3f 0.000 0.000\n" $xbox > $path_dim0
printf "cellBasisVector2\t 0.000 %6.3f 0.000\n" $ybox >> $path_dim0
printf "cellBasisVector3\t 0.000 0.000 %6.3f\n" $zbox >> $path_dim0
printf "cellOrigin\t\t %6.3f %6.3f %6.3f\n" $x0 $y0 $z0 >> $path_dim0
