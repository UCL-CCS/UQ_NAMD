"""
==============================================================================
THE LOOK-AHEAD STEP

Takes the current configuration of points, computes so-called adimissble
points in the look_forward subroutine. These points are used in
the adaptation step to decide along which dimension to place more samples.

The look-ahead step and the adaptation step can be executed multiple times:
look ahead, adapt, look ahead, adapt, etc
==============================================================================
"""

import easyvvuq as uq
import os, sys
from utils import SimEncoder, Eq1Encoder, Eq2Encoder

output_columns = ["binding_energy_avg"]
#EDIT: changed to home dir
# path_uqnamd = os.environ['PATH_UQNAMD']
path_uqnamd = os.path.abspath(os.path.dirname(__file__))
#EDIT changed to tmp
# work_dir = path_uqnamd+ "/campaigns"
work_dir = '/tmp'

# Set iteration count of the adaptive algorithm
iteration = int(sys.argv[1])

#reload Campaign, sampler, analysis
campaign = uq.Campaign(state_file="./states/namd_easyvvuq_state.{}.json".format(iteration-1),
                       work_dir=work_dir)
print('========================================================')
print('Reloaded campaign', campaign.campaign_dir.split('/')[-1], ' at iteration: ', iteration)
print('========================================================')
sampler = campaign.get_active_sampler()
sampler.load_state("./states/namd_sampler_state.{}.pickle".format(iteration-1))
campaign.set_sampler(sampler)
analysis = uq.analysis.SCAnalysis(sampler=sampler, qoi_cols=output_columns)
analysis.load_state("./states/namd_analysis_state.{}.pickle".format(iteration-1))

#required parameter in the case of a Fabsim run
skip = sampler.count

#look-ahead step (compute the code at admissible forward points)
sampler.look_ahead(analysis.l_norm)

#proceed as usual
campaign.draw_samples()
campaign.populate_runs_dir() # Where are these directories populated? What prevents from running Runs previously simulated? (Maxime)

#save campaign and sampler
campaign.save_state("./states/namd_easyvvuq_state.{}.json".format(iteration))
sampler.save_state("./states/namd_sampler_state.{}.pickle".format(iteration))
analysis.save_state("./states/namd_analysis_state.{}.pickle".format(iteration))

# #run the UQ ensemble
cmd = path_uqnamd + "/template/dummy_full.py"
# vinterpret = "sbatch --export=path_uq={}".format(path_uqnamd)
campaign.apply_for_each_run_dir(uq.actions.ExecuteLocal(cmd))
