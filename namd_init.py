"""
==============================================================================
INITIALIZATION OF A (DIMENSION-ADAPTIVE) STOCHASTIC COLLOCATION CAMPAIGN

Execute once.
==============================================================================
"""

import easyvvuq as uq
import chaospy as cp
import os
import json
import numpy as np


class SimEncoder(uq.encoders.JinjaEncoder, encoder_name='SimEncoder'):
    def encode(self, params={}, target_dir='', fixtures=None):

        simulation_time = 10**params["simulation_time_power"]
        params["run_sim1"] = int( round( simulation_time / params["timestep_sim1"] ) )
        # 48 as the number of cores on a node (see anaysis.sh)
        params["dcd_freq_sim1"] = min(int(params["run_sim1"]/48), 5000)
        super().encode(params, target_dir, fixtures)

class Eq1Encoder(uq.encoders.JinjaEncoder, encoder_name='Eq1Encoder'):
    def encode(self, params={}, target_dir='', fixtures=None):

        simulation_time = 10**params["equilibration1_time_power"]
        params["run_eq1"] = int( round( simulation_time / params["timestep_eq1"] ) )
        super().encode(params, target_dir, fixtures)

class Eq2Encoder(uq.encoders.JinjaEncoder, encoder_name='Eq2Encoder'):
    def encode(self, params={}, target_dir='', fixtures=None):

        simulation_time = 10**params["equilibration2_time_power"]
        params["run_eq2"] = int( round( simulation_time / params["timestep_eq2"] ) )
        super().encode(params, target_dir, fixtures)

home = os.path.abspath(os.path.dirname(__file__))
output_columns = ["binding_energy"]
work_dir = '/tmp'

n_replicas = 3 # number of replicas per input data point

# Set up a fresh campaign
campaign = uq.Campaign(name='namd_', work_dir=work_dir)

# Define parameter space
params = json.load(open(home + '/template/g15/replica-confs/params.json'))
#manually add some parameters
params["simulation_time_power"]  = {"default": 3, "type": "float"} # 10 ns
params["equilibration1_time_power"] = {"default": 5, "type": "float"} #100ps
params["equilibration2_time_power"] = {"default": 6, "type": "float"} #1ns
params["box_size"] = {"default": 14, "type": "float"}

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
multiencoder = uq.encoders.MultiEncoder(
    uq.encoders.DirectoryBuilder(tree=directory_tree),
    uq.encoders.JinjaEncoder(
        template_fname=home + '/template/g15/replica-confs/template_eq0.conf',
        target_filename='g15/replica-confs/eq0.conf'),
    uq.encoders.CopyEncoder(
        source_filename=home + '/template/g15/replica-confs/eq0-replicas.conf',
        target_filename='g15/replica-confs/eq0-replicas.conf'),
    Eq1Encoder(
        template_fname=home + '/template/g15/replica-confs/template_eq1.conf',
        target_filename='g15/replica-confs/eq1.conf'),
    uq.encoders.CopyEncoder(
        source_filename=home + '/template/g15/replica-confs/eq1-replicas.conf',
        target_filename='g15/replica-confs/eq1-replicas.conf'),
    Eq2Encoder(
        template_fname=home + '/template/g15/replica-confs/template_eq2.conf',
        target_filename='g15/replica-confs/eq2.conf'),
    uq.encoders.CopyEncoder(
        source_filename=home + '/template/g15/replica-confs/eq2-replicas.conf',
        target_filename='g15/replica-confs/eq2-replicas.conf'),
    SimEncoder(
        template_fname=home + '/template/g15/replica-confs/template_sim1.conf',
        target_filename='g15/replica-confs/sim1.conf'),
    uq.encoders.CopyEncoder(
        source_filename=home + '/template/g15/replica-confs/sim1-replicas.conf',
        target_filename='g15/replica-confs/sim1-replicas.conf'),
    uq.encoders.GenericEncoder(
        delimiter='$',
        template_fname=home + '/template/g15/build/tleap.in',
        target_filename='g15/build/tleap.in')
)

# will have to write something in the analysis step which collects replicas output
# into a useful file, prefereable csv
decoder = uq.decoders.SimpleCSV(
    target_filename='output.csv',
    output_columns=output_columns, header=0, delimiter='\t')

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
        "BerendsenPressureTarget_eq2": cp.Uniform(0.8, 1.2),
        "BerendsenPressureRelaxationTime_eq2": cp.Normal(100,5),
        "box_size": cp.Uniform(14, 16),
        "equilibration1_time_power":  cp.Uniform(2,4),
        "equilibration2_time_power": cp.Uniform(2,4),
}

#==================================
#create (dimension-adaptive) sampler
#=================================
#sparse = use a sparse grid
#growth = use a nested quadrature rule
#midpoint_level1 = use a single collocation point in the 1st iteration
#dimension_adaptive = use a dimension adaptive sampler

sampler = uq.sampling.SCSampler(vary=vary, polynomial_order=1,
                                quadrature_rule="C",
                                sparse=False, growth=False,
                                midpoint_level1=False,
                                dimension_adaptive=False)

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

#run the UQ ensemble
# # cwd = "/hppfs/work/pn72qu/di36yax3/tmp/uq_namd2" #os.getcwd()
# cwd = os.getcwd()
# cmd = "{}/template/prepare.sh".format(cwd)
# campaign.apply_for_each_run_dir(uq.actions.ExecuteLocal(cmd, interpret='bash'))
# cmd = "{}/template/sim.sh".format(cwd)
# campaign.apply_for_each_run_dir(uq.actions.ExecuteLocal(cmd, interpret='sbatch'))
# cmd = "{}/template/analysis.sh".format(cwd)
# campaign.apply_for_each_run_dir(uq.actions.ExecuteLocal(cmd, interpret='sbatch'))

# Ready to replace the LocalExecution above with execution from PJM, how? Using fabsim? (Maxime)
#import fabsim3_cmd_api as fab
#fab.run_uq_ensemble(config??, campaign.campaign_dir, script='??',
#                    machine="supermuc??_vecma", PilotJob = True)
