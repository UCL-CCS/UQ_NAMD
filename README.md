`python namd_init.py` working on 9.6.2020 with:
- EasyVVUQ (branch: speed_up_SC_analysis, Chaospy v3.2.12)
- EQI
- QCG-PJ

Specify paths in the SLURM job toward Python environment and UQ directory:
```
source /path/to/python/env/uq/bin/activate
...
export PATH_UQNAMD=/path/to/UQ_NAMD
```

Execute submitting SLURM job:
```
sbatch run-supermuc.sh
```

Template generation:
```
cd make_templates
python create_jinja_template.py eq0.conf eq1.conf eq2.conf sim1.conf
cp params.json template_eq0.conf template_eq1.conf template_eq2.conf template_sim1.conf ../template/g15/replica-confs/
cd ..
```

Set the parameters variability in `namd_init.py`, in the `vary` dictionary, such as:
```
vary = {
        "langevinTemp": cp.Gaussian(300.,100.), # not sure about normal distirbution of float parameter
        "rigidBonds": cp.categorical(["none", "water", "all"]), # not sure how to draw categorical string parameters
        "box_size": cp.Uniform(14, 16),
        "equilibration1_time_power":  cp.Uniform(2,4),
        "equilibration2_time_power": cp.Uniform(2,4),
}
```

Adaptive sampling workflow:
```
python namd_init.py
python namd_analyse.py
python namd_look_ahead.py 1
python namd_adapt.py 1
python namd_look_ahead.py 2
python namd_adapt.py 2
...
python namd_look_ahead.py iteration
python namd_adapt.py iteration
python namd_look_ahead.py iteration+1
python namd_adapt.py iteration+1
```
The execution of namd_init.py and namd_analyse.py constitutes the iteration '0' of the adaptive sampling method (or the unique iteration of the non-adaptive sampling method). Subsequent iterations are executed using namd_look_ahead.py and namd_adapt.py, which require the specification of the iteration number (integer) to store the analysis and sampler data individually for each iteration.


We previously used fabsim to copy jobs back and forth from remote and execute jobs.
I've left the commands in (commented) because these tasks still need to be implemented.
FabSim could still be used, but with such large data files it may be impractical(?)

/plots.ipynb/ : jupyter notebook that was used for analysing the covidsim disease parameter sweep, this analysis should be relevant for this study
python-env.txt : python conda environment for reference
/template/ : simulation files modified to template with EasyVVUQ
/campaigns/ : where easyvvuq campaigns are stored


