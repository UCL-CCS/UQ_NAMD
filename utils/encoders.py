import easyvvuq as uq


class SimEncoder(uq.encoders.JinjaEncoder, encoder_name='SimEncoder'):
    def encode(self, params={}, target_dir='', fixtures=None):
        simulation_time = 10**params["simulation_time_power"]
        params["n_steps"] = int( round( simulation_time / params["timestep"] ) )
        # 48 as the number of cores on a node (see anaysis.sh)
        params["dcd_freq"] = min(int(params["n_steps"]/48), 5000)
        super().encode(params, target_dir, fixtures)


class Eq1Encoder(uq.encoders.JinjaEncoder, encoder_name='Eq1Encoder'):
    def encode(self, params={}, target_dir='', fixtures=None):
        simulation_time = 10**params["equilibration1_time_power"]
        params["n_steps"] = int( round( simulation_time / params["timestep"] ) )
        super().encode(params, target_dir, fixtures)


class Eq2Encoder(uq.encoders.JinjaEncoder, encoder_name='Eq2Encoder'):
    def encode(self, params={}, target_dir='', fixtures=None):
        simulation_time = 10**params["equilibration2_time_power"]
        params["n_steps"] = int( round( simulation_time / params["timestep"] ) )
        super().encode(params, target_dir, fixtures)
