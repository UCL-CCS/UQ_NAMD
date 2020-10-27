"""
==============================================================================
INITIALIZATION OF A (DIMENSION-ADAPTIVE) STOCHASTIC COLLOCATION CAMPAIGN

Execute once.
==============================================================================
"""

import easyvvuq as uq
import chaospy as cp
import os, sys
import math
import json
import numpy as np
from encoders import SimEncoder, Eq1Encoder, Eq2Encoder

home = os.path.abspath(os.path.dirname(__file__))
output_columns = ["drug","binding_energy_avg"]
work_dir = '/hppfs/work/pn72qu/di36yax3/tmp/uq_namd2_wouter/campaigns'


n_replicas = 3 # number of replicas per input data point

# Set up a fresh campaign
campaign = uq.Campaign(name='namd_', work_dir=work_dir)

# Define parameter space
params = json.load(open(home + '/template/g15/replica-confs/params.json'))
#manually add some parameters
params["box_size"] = {"default": 14.0, "type": "float"}

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
}

#==================================
#create (dimension-adaptive) sampler
#=================================

sampler = uq.sampling.SCSampler(vary=vary, polynomial_order=1,
                                quadrature_rule="C",
                                sparse=False, growth=False,
                                midpoint_level1=False,
                                dimension_adaptive=False)

campaign.set_sampler(sampler)
# campaign.set_sampler(testing_sampler)
campaign.draw_samples()
campaign.populate_runs_dir()

campaign.save_state("namd_easyvvuq_state.json")
sampler.save_state("namd_sampler_state.pickle")

#run the UQ ensemble
cmd = "/hppfs/work/pn72qu/di36yax3/tmp/uq_namd2_wouter/template/full.sh"
campaign.apply_for_each_run_dir(uq.actions.ExecuteLocal(cmd, interpret='sbatch'))

