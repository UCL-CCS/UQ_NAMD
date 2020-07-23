`python namd_init.py` working on 9.6.2020 with:
- EasyVVUQ (branch: speed_up_SC_analysis, Chaospy v3.2.12)

Adaptive sampling workflow:
```
python init
python analyse
python look_ahead
python adapt
python look_ahead
python adapt
python look_ahead
python adapt
....
```

We previously used fabsim to copy jobs back and forth from remote and execute jobs.
I've left the commands in (commented) because these tasks still need to be implemented.
FabSim could still be used, but with such large data files it may be impractical(?)

/plots.ipynb/ : jupyter notebook that was used for analysing the covidsim disease parameter sweep, this analysis should be relevant for this study
python-env.txt : python conda environment for reference
/template/ : simulation files modified to template with EasyVVUQ
/campaigns/ : where easyvvuq campaigns are stored


