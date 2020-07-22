"""
==============================================================================
THE ADAPTATION STEP

Execute the look ahead step first

Takes the admissble points computed in the look ahead step to decide along
which dimension to place more samples. See adapt_dimension subroutine.

The look-ahead step and the adaptation step can be executed multiple times:
look ahead, adapt, look ahead, adapt, etc
==============================================================================
"""

import easyvvuq as uq
import os
import matplotlib.pyplot as plt
import numpy as np
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
sampler.load_state("_sampler_state.pickle")
campaign.set_sampler(sampler)
analysis = uq.analysis.SCAnalysis(sampler=sampler, qoi_cols=output_columns)
analysis.load_state("namd_analysis_state.pickle")

# fetch results
#fab.get_uq_samples(config, campaign.campaign_dir, sampler._number_of_samples,
#                   machine='eagle_vecma')
campaign.collate()

#compute the error at all admissible points, select direction with
#highest error and add that direction to the grid
data_frame = campaign.get_collation_result()
data_frame.to_csv('results.csv')
analysis.adapt_dimension(output_columns[0], data_frame)

#save everything
campaign.save_state("namd_easyvvuq_state.json")
sampler.save_state("namd_sampler_state.pickle")
analysis.save_state("namd_analysis_state.pickle")

#apply analysis
#campaign.apply_analysis(analysis)
#results = campaign.get_last_analysis()

#sobols_first = results["sobols_first"][output_columns[0]]
#for param in sobols_first.keys():
#    print(sobols_first[param][-1],param)

# Outdated (not for covidsim) to be replaced by the analysis of binding energy vs ?? (but not 'days') (Maxime)
# #plot mean +/- std dev
# fig = plt.figure()
# ax = fig.add_subplot(111, xlabel="days", ylabel=output_columns[0])
# #mean = results["statistical_moments"][output_columns[0]]["mean"]
# #std = results["statistical_moments"][output_columns[0]]["std"]
# #ax.plot(mean)
# #ax.plot(mean + std, '--r')
# #ax.plot(mean - std, '--r')
# plt.tight_layout()

#plot max quad order per dimension. Gives an idea of which
#variables are important
analysis.adaptation_histogram()
analysis.plot_stat_convergence()
print(analysis.get_adaptation_errors())
