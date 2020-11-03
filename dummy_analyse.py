"""
==============================================================================
ANALYSIS OF THE INITIAL (DIMENSION-ADAPTIVE) STCOHASTIC COLLOCATION CAMPAIGN

Execute once.
==============================================================================
"""

import easyvvuq as uq
import os
from utils import SimEncoder, Eq1Encoder, Eq2Encoder

output_columns = ["binding_energy_avg"]
#EDIT: changed to home dir
# path_uqnamd = os.environ['PATH_UQNAMD']
path_uqnamd = os.path.abspath(os.path.dirname(__file__))
#EDIT changed to tmp
# work_dir = path_uqnamd+ "/campaigns"
work_dir = '/tmp'

campaign = uq.Campaign(state_file="./states/namd_easyvvuq_state.0.json",
                       work_dir=work_dir)
print('========================================================')
print('Reloaded campaign', campaign.campaign_dir.split('/')[-1])
print('========================================================')
sampler = campaign.get_active_sampler()
sampler.load_state("./states/namd_sampler_state.0.pickle")
campaign.set_sampler(sampler)

#get results
#fab.get_uq_samples(config, campaign.campaign_dir, sampler._number_of_samples,
#                   machine='eagle_vecma')
campaign.collate()

# Post-processing analysis
analysis = uq.analysis.SCAnalysis(
    sampler=campaign._active_sampler,
    qoi_cols=output_columns
)

campaign.apply_analysis(analysis)

#this is a temporary subroutine which saves the entire state of
#the analysis in a pickle file. The proper place for this is the database
analysis.save_state("./states/namd_analysis_state.0.pickle")
