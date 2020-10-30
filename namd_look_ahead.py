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
from encoders import SimEncoder, Eq1Encoder, Eq2Encoder

output_columns = ["drug","binding_energy_avg"]
path_uqnamd = os.environ['PATH_UQNAMD']
work_dir = path_uqnamd+ "/campaigns"

# Set iteration count of the adaptive algorithm
iteration = int(sys.argv[1])

#reload Campaign, sampler, analysis
campaign = uq.Campaign(state_file="namd_easyvvuq_state.{}.json".format(iteration-1),
                       work_dir=work_dir)
print('========================================================')
print('Reloaded campaign', campaign.campaign_dir.split('/')[-1], ' at iteration: ', iteration)
print('========================================================')
sampler = campaign.get_active_sampler()
sampler.load_state("namd_sampler_state.{}.pickle".format(iteration-1))
campaign.set_sampler(sampler)
analysis = uq.analysis.SCAnalysis(sampler=sampler, qoi_cols=output_columns)
analysis.load_state("namd_analysis_state.{}.pickle".format(iteration-1))

#required parameter in the case of a Fabsim run
skip = sampler.count

#look-ahead step (compute the code at admissible forward points)
sampler.look_ahead(analysis.l_norm)

#proceed as usual
campaign.draw_samples()
campaign.populate_runs_dir() # Where are these directories populated? What prevents from running Runs previously simulated? (Maxime)

#save campaign and sampler
campaign.save_state("namd_easyvvuq_state.{}.json".format(iteration))
sampler.save_state("namd_sampler_state.{}.pickle".format(iteration))
analysis.save_state("namd_analysis_state.{}.pickle".format(iteration))

#run the UQ ensemble at the admissible forward points
#skip (int) = the number of previous samples: required to avoid recomputing
#already computed samples from a previous iteration
#fab.run_uq_ensemble(config, campaign.campaign_dir, script='CovidSim',
#                    machine="eagle_vecma", skip=skip, PilotJob=False)

#run the UQ ensemble
cmd = path_uqnamd + "/template/full.sh"
vinterpret = "sbatch --export=path_uq={}".format(path_uqnamd)
campaign.apply_for_each_run_dir(uq.actions.ExecuteLocal(cmd, interpret=vinterpret))
