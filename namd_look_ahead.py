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

class SimEncoder(uq.encoders.JinjaEncoder, encoder_name='SimEncoder'):
    def encode(self, params={}, target_dir='', fixtures=None):

        simulation_time = 10**params["simulation_time_power"]
        params["n_steps"] = int( round( simulation_time / params["timestep"], -1 ) )
        # 48 as the number of cores on a node (see anaysis.sh)
        params["dcd_freq"] = min(int(params["n_steps"]/48), 5000)
        super().encode(params, target_dir, fixtures)

class Eq1Encoder(uq.encoders.JinjaEncoder, encoder_name='Eq1Encoder'):
    def encode(self, params={}, target_dir='', fixtures=None):

        simulation_time = 10**params["equilibration1_time_power"]
        params["n_steps"] = int( round( simulation_time / params["timestep"], -1 ) )
        super().encode(params, target_dir, fixtures)

class Eq2Encoder(uq.encoders.JinjaEncoder, encoder_name='Eq2Encoder'):
    def encode(self, params={}, target_dir='', fixtures=None):

        simulation_time = 10**params["equilibration2_time_power"]
        params["n_steps_loop"] = int( round( simulation_time / params["timestep"], -1 ) )
        params["n_steps"] = 15*int( round( simulation_time / params["timestep"], -1 ) )
        super().encode(params, target_dir, fixtures)

home = os.path.abspath(os.path.dirname(__file__))
output_columns = ["drug","binding_energy_avg"]
work_dir = '/hppfs/work/pn72qu/di36yax3/tmp/uq_namd2/campaigns'

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

cmd = "/hppfs/work/pn72qu/di36yax3/tmp/uq_namd2/template/full.sh"
campaign.apply_for_each_run_dir(uq.actions.ExecuteLocal(cmd, interpret='sbatch'))
