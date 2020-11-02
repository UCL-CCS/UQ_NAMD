"""
==============================================================================
INITIALIZATION OF A (DIMENSION-ADAPTIVE) STOCHASTIC COLLOCATION CAMPAIGN

Execute once.
==============================================================================
"""

import os
import json
import numpy as np
import chaospy as cp
import easyvvuq as uq
# Specific encoders
from encoders import SimEncoder, Eq1Encoder, Eq2Encoder
# QCG-PJ wrapper
import easypj
from easypj import TaskRequirements, Resources
from easypj import Task, TaskType, SubmitOrder

namd_dir = os.environ['PATH_UQNAMD']
temp_dir = os.environ['SCRATCH']
work_dir = temp_dir + '/campaigns'

output_columns = ["drug","replica","binding_energy_avg","binding_energy_stdev"]

# number of replicas per input data point
n_replicas = 3

# Set up a fresh campaign
campaign = uq.Campaign(name='namd_', work_dir=work_dir)

# Define parameter space for the cannonsim app
params = {
          "timestep":{"default": 2, "type": "float"},
          "simulation_time_power":{"default": 3, "type": "float"}, # 10 ns
          "cutoff": {"default": 12, "type": "float"},
          "langevinDamping": {"default": 5, "type": "float"},
          "temperature": {"default": 300, "type": "float"},
          "pressure": {"default": 1.01325, "type": "float"},
          "compressibility": {"default": 4.57e-5, "type": "float"},
          "pressure_relaxation_time": {"default": 100, "type": "float"},
          "box_size": {"default": 14, "type": "float"},
          "equilibration1_time_power":{"default": 5, "type": "float"}, #100ps
          "equilibration2_time_power":{"default": 6, "type": "float"}, #1ns
          }

# tell the campaign the directory structure required
directory_tree = {'g15':
                    {'build': None,
                     'constraint': None,
                     'fe':
                        {'build': None,
                         'dcd': None,
                         'mmpbsa': {'rep'+str(i):None for i in range(1,n_replicas+1)},
                        },
                     'par': None,
                     'replica-confs': None,
                     'replicas':
                        {'rep'+str(i):
                            {'equilibration': None,
                             'simulation': None}
                             for i in range(1,n_replicas+1)
                            },
                        }
                    }

# Build the encoders
# i've only implemented some md-engine parameters in the sim1.conf file.
# Every requried input file needs to be listed as an encoder even if no substitutions
# are to be made, this is a bit of a fudge
multiencoder = uq.encoders.MultiEncoder(
    uq.encoders.DirectoryBuilder(tree=directory_tree),
    uq.encoders.CopyEncoder(
        source_filename=namd_dir + '/template/g15/replica-confs/eq0.conf',
        target_filename='g15/replica-confs/eq0.conf'),
    uq.encoders.CopyEncoder(
        source_filename=namd_dir + '/template/g15/replica-confs/eq0-replicas.conf',
        target_filename='g15/replica-confs/eq0-replicas.conf'),
    Eq1Encoder(
        template_fname=namd_dir + '/template/g15/replica-confs/eq1.conf',
        target_filename='g15/replica-confs/eq1.conf'),
    uq.encoders.CopyEncoder(
        source_filename=namd_dir + '/template/g15/replica-confs/eq1-replicas.conf',
        target_filename='g15/replica-confs/eq1-replicas.conf'),
    Eq2Encoder(
        template_fname=namd_dir + '/template/g15/replica-confs/eq2.conf',
        target_filename='g15/replica-confs/eq2.conf'),
    uq.encoders.CopyEncoder(
        source_filename=namd_dir + '/template/g15/replica-confs/eq2-replicas.conf',
        target_filename='g15/replica-confs/eq2-replicas.conf'),
    SimEncoder(
        template_fname=namd_dir + '/template/g15/replica-confs/sim1.conf',
        target_filename='g15/replica-confs/sim1.conf'),
    uq.encoders.CopyEncoder(
        source_filename=namd_dir + '/template/g15/replica-confs/sim1-replicas.conf',
        target_filename='g15/replica-confs/sim1-replicas.conf'),
    uq.encoders.GenericEncoder(
        delimiter='$',
        template_fname=namd_dir + '/template/g15/build/tleap.in',
        target_filename='g15/build/tleap.in')
)

# will have to wriet something in the analysis step which collects replicas output
# into a useful file, prefereable csv
decoder = uq.decoders.SimpleCSV(
    target_filename='output.csv',
    output_columns=output_columns, header=0, delimiter=',')

collater = uq.collate.AggregateSamples(average=False)

# Add the app
campaign.add_app(name="uq_for_namd",
                 params=params,
                 encoder=multiencoder,
                 collater=collater,
                 decoder=decoder)
# Set the active app to be cannonsim (this is redundant when only one app
# has been added)
campaign.set_app("uq_for_namd")

#parameters to vary
# for a lot of the parameters its hard to define a useful range to sample
# we could choose +/- 10%
# or choose ranges that are typically found in the literature
vary = {
        # "timestep": cp.Uniform(0.1,2),
        # "simulation_time_power":  cp.Uniform(5,7),
        # "cutoff": cp.Uniform(8,15),
        # "langevinDamping": cp.Uniform(1,10),
        # "temperature": cp.Uniform(270, 330),
        # "pressure": cp.Uniform(0.8, 1.2),
        # "compressibility": cp.Uniform(4e-5, 5.5e-5),
        # "pressure_relaxation_time": cp.Exponential(100,0),
        "box_size": cp.Uniform(4,6),
        "equilibration1_time_power":  cp.Uniform(2,4),
        "equilibration2_time_power": cp.Uniform(2,4),
}

#=================================
#create dimension-adaptive sampler
#=================================
#sparse = use a sparse grid (required)
#growth = use a nested quadrature rule (not required)
#midpoint_level1 = use a single collocation point in the 1st iteration (not required)
#dimension_adaptive = use a dimension adaptive sampler (required)

sampler = uq.sampling.SCSampler(vary=vary, polynomial_order=1,
                                quadrature_rule="C",
                                sparse=True, growth=True,
                                midpoint_level1=True,
                                dimension_adaptive=True)

# # swap to this for a simple test of the substitutions
# testing_sampler = uq.sampling.BasicSweep(sweep={
#                     "box_size": [5.0, 10.0, 20.0],
#                     })

campaign.set_sampler(sampler)
# campaign.set_sampler(testing_sampler)
campaign.draw_samples()
campaign.populate_runs_dir()

campaign.save_state("namd_easyvvuq_state.json")
sampler.save_state("namd_sampler_state.pickle")

# run the UQ ensemble

cmd = namd_dir + "/template/full_pj.sh"
#campaign.apply_for_each_run_dir(uq.actions.ExecuteLocal(cmd, interpret='sbatch'))
print("Starting Pilot Job execution ... \n")
qcgpjexec = easypj.Executor()
qcgpjexec.create_manager(dir=campaign.campaign_dir, log_level='info')

qcgpjexec.add_task(Task(
    TaskType.EXECUTION,
    TaskRequirements(),
    application=cmd
))

qcgpjexec.run(
    campaign=my_campaign,
    submit_order=SubmitOrder.EXEC_ONLY
)

qcgpjexec.terminate_manager()

# Collate, Analysis et get results here? (Jalal)