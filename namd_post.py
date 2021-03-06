"""
==============================================================================
THE POSTPROCESSING STEP
Analyse results after all sampling has completed
==============================================================================
"""
       
import easyvvuq as uq
import os
import matplotlib.pyplot as plt
import numpy as np

#from custom import CustomEncoder
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

plt.close('all')
home = os.path.abspath(os.path.dirname(__file__))
output_columns = ["binding_energy_avg"]
work_dir = '/hppfs/work/pn72qu/di36yax3/tmp/uq_namd2/campaigns'

#reload Campaign, sampler, analysis
campaign = uq.Campaign(state_file="namd_easyvvuq_state.json", work_dir=work_dir)
print('========================================================')
print('Reloaded campaign', campaign.campaign_dir.split('/')[-1])
print('========================================================')
sampler = campaign.get_active_sampler()
sampler.load_state("namd_sampler_state.pickle")
campaign.set_sampler(sampler)
analysis = uq.analysis.SCAnalysis(sampler=sampler, qoi_cols=output_columns)
analysis.load_state("namd_analysis_state.pickle")

#apply analysis
campaign.apply_analysis(analysis)
analysis.save_state("post_analysis_state.pickle")
results = campaign.get_last_analysis()
sobols_first = results["sobols_first"][output_columns[0]]

for param in sobols_first.keys():
    print(sobols_first[param][-1],param)

for qoi in analysis.qoi_cols:
    print(qoi,analysis.get_sobol_indices(qoi,'all'))


#########################
# plot mean +/- std dev #
#########################

fig = plt.figure()
ax = fig.add_subplot(111, xlabel="days", ylabel=output_columns[0])
mean = results["statistical_moments"][output_columns[0]]["mean"]
std = results["statistical_moments"][output_columns[0]]["std"]
ax.plot(mean)
ax.plot(mean + std, '--r')
ax.plot(mean - std, '--r')
plt.tight_layout()

#################################
# Plot some convergence metrics #
#################################

analysis.adaptation_histogram()
analysis.plot_stat_convergence()
surplus_errors = analysis.get_adaptation_errors()
fig = plt.figure()
ax = fig.add_subplot(111, xlabel = 'refinement step', ylabel='max surplus error')
ax.plot(range(1, len(surplus_errors) + 1), surplus_errors, '-b*')
plt.tight_layout()

#####################################
# Plot the random surrogate samples #
#####################################
fig = plt.figure(figsize=[12, 4])
ax = fig.add_subplot(131, xlabel='days', ylabel=output_columns[0],
                     title='Surrogate samples')
ax.plot(analysis.get_sample_array(output_columns[0]).T, 'ro', alpha = 0.5)

#generate n_mc samples from the input distributions
n_mc = 20
xi_mc = np.zeros([n_mc,sampler.xi_d.shape[1]])
idx = 0
for dist in sampler.vary.get_values():
    xi_mc[:, idx] = dist.sample(n_mc)
    idx += 1
xi_mc = sampler.xi_d
n_mc = sampler.xi_d.shape[0]
    
# evaluate the surrogate at these values
print('Evaluating surrogate model', n_mc, 'times')
for i in range(n_mc):
    ax.plot(analysis.surrogate(output_columns[0], xi_mc[i]), 'g')
print('done')

##################################
# Plot first-order Sobol indices #
##################################

ax = fig.add_subplot(132, title=r'First-order Sobols indices',
                      xlabel="days", ylabel=output_columns[0], ylim=[0,1])
sobols_first = results["sobols_first"][output_columns[0]]
for param in sobols_first.keys():
    ax.plot(sobols_first[param], label=param)
leg = ax.legend(loc=0, fontsize=8)
leg.set_draggable(True)
plt.tight_layout()

plt.show()

#save everything
analysis.save_state("post_analysis_state.pickle")

