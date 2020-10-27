import easyvvuq as uq

class SimEncoder(uq.encoders.JinjaEncoder, encoder_name='SimEncoder'):
    def encode(self, params={}, target_dir='', fixtures=None):

        params["pairlistdist"] = params["cutoff"] + 1.5
        params["switchdist"] = params["cutoff"] - 2.0
        params["run_sim1"] = int( round( params["time_sim1"] / params["timestep"], -1 ) )
        # 48 as the number of cores on a node (see anaysis.sh)
        params["dcd_freq_sim1"] = min(int(params["run_sim1"]/48), 5000)
        super().encode(params, target_dir, fixtures)

class Eq1Encoder(uq.encoders.JinjaEncoder, encoder_name='Eq1Encoder'):
    def encode(self, params={}, target_dir='', fixtures=None):

        params["pairlistdist"] = params["cutoff"] + 1.5
        params["switchdist"] = params["cutoff"] - 2.0
        params["run_eq1"] = int( round( 1.0*params["time_factor_eq"] / params["timestep"], -1 ) )
        super().encode(params, target_dir, fixtures)

class Eq2Encoder(uq.encoders.JinjaEncoder, encoder_name='Eq2Encoder'):
    def encode(self, params={}, target_dir='', fixtures=None):

        params["pairlistdist"] = params["cutoff"] + 1.5
        params["switchdist"] = params["cutoff"] - 2.0
        params["run_cycle_eq2"] = int( round( 1.0*params["time_factor_eq"] / params["timestep"], -1 ) )
        params["run_eq2"] = int( round( 20.0*params["time_factor_eq"] / params["timestep"], -1 ) )
        super().encode(params, target_dir, fixtures)
