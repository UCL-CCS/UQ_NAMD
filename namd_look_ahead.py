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
import os
from custom import CustomEncoder

home = os.path.abspath(os.path.dirname(__file__))
output_columns = ["binding_energy"]
work_dir = '/hppfs/work/pn72qu/di36yax3/tmp/uq_namd/campaigns'

#reload Campaign, sampler, analysis
campaign = uq.Campaign(state_file="namd_easyvvuq_state.json",
                       work_dir=work_dir)
print('========================================================')
print('Reloaded campaign', campaign.campaign_dir.split('/')[-1])
print('========================================================')
sampler = campaign.get_active_sampler()
sampler.load_state("namd_sampler_state.pickle")
campaign.set_sampler(sampler)
analysis = uq.analysis.SCAnalysis(sampler=sampler, qoi_cols=output_columns)
analysis.load_state("namd_analysis_state.pickle")

#required parameter in the case of a Fabsim run
skip = sampler.count

#look-ahead step (compute the code at admissible forward points)
sampler.look_ahead(analysis.l_norm)

#proceed as usual
campaign.draw_samples()
campaign.populate_runs_dir() # Where are these directories populated? What prevents from running Runs previously simulated? (Maxime)

#save campaign and sampler
campaign.save_state("namd_easyvvuq_state.json")
sampler.save_state("namd_sampler_state.pickle")

#run the UQ ensemble at the admissible forward points
#skip (int) = the number of previous samples: required to avoid recomputing
#already computed samples from a previous iteration
#fab.run_uq_ensemble(config, campaign.campaign_dir, script='CovidSim',
#                    machine="eagle_vecma", skip=skip, PilotJob=False)

cwd = "/hppfs/work/pn72qu/di36yax3/tmp/uq_namd" #os.getcwd()
cmd = "{}/template/prepare.sh".format(cwd)
campaign.apply_for_each_run_dir(uq.actions.ExecuteLocal(cmd, interpret='bash'))
cmd = "{}/template/sim.sh".format(cwd)
campaign.apply_for_each_run_dir(uq.actions.ExecuteLocal(cmd, interpret='sbatch'))
cmd = "{}/template/analysis.sh".format(cwd)
campaign.apply_for_each_run_dir(uq.actions.ExecuteLocal(cmd, interpret='sbatch'))
