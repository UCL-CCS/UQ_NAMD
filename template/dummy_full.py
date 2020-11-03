#!/home/wouter/anaconda3/bin/python

import numpy as np
import chaospy as cp

def search_string_in_file(file_name, string_to_search):
    """Search for the given string in file and return lines containing that string,
    along with line numbers"""
    line_number = 0
    list_of_results = []
    # Open the file in read only mode
    with open(file_name, 'r') as read_obj:
        # Read all lines in the file one by one
        for line in read_obj:
            # For each line, check if line contains the string
            line_number += 1
            if string_to_search in line:
                # If yes, then add the line number & line as a tuple in the list
                list_of_results.append((line_number, line.rstrip()))
 
    # Return list of tuples containing line numbers and lines where string is found
    return list_of_results

def poly_model(theta):
    """
    The 'model' that is evaluated
    """
    
    sol = 1.0
    for i in range(d):
        print(theta[i]/default_vals[i])
        sol *= 3 * a[i] * (theta[i]/default_vals[i])**2 + 1.0
    return sol/2**d

#'default' values of the parameters, used in the poly_model to normalize the inpust
default_vals = np.array([3.00000e+02, 1.01325e+00, 
        1.20000e+01, 2.00000e+00, 1.00000e-05, 1.00000e+02,
        1.00000e+01, 1.00000e+00, 1.00000e+03, 5.00000e+01, 1.00000e+02,
        1.00000e+00, 5.00000e+00, 4.57000e-05, 1.00000e+02])

d = default_vals.size
#the a cofficients are set up is such a way that the 1st parameter is the most important, then
#the second, then the third etc
a = np.ones(d)
for i in range(1, d):
    a[i] = a[i-1]/2
    
#PARAMETERS WITH SOME DISCRETE DISTRIBUTIONS

# vary = {
#   "langevinTemp": cp.Uniform(300.0*0.85,300.0*1.15),
#   # "time_factor_eq": cp.Uniform(60000.0*0.85,60000.0*1.15),
#   # "run_stepcount_factor": cp.DiscreteUniform(30000*0.85,30000*1.15),
#   "BerendsenPressureTarget": cp.Uniform(1.01325*0.85,1.01325*1.15),
#   # "time_sim1": cp.Uniform(10000000.0*0.85,10000000.0*1.15),
#   # "box_size": cp.Uniform(14.0*0.85,14.0*1.15),
#   "cutoff": cp.Uniform(12.0*0.85,12.0*1.15),
#   # "switching": ["on", "off"],
#   "timestep": cp.Uniform(2.0*0.85,2.0*1.15),
#   # "rigidBonds": ["none", "water", "all"],
#   "rigidtolerance": cp.Uniform(0.00001*0.85,0.00001*1.15),
#   "rigidIterations": cp.DiscreteUniform(100*0.85,100*1.15),
#   #Below will only sample 1, is not a proper distribution
#   # "nonbondedFreq": cp.DiscreteUniform(1*0.85,1*1.15),
#   #Below will only sample 2, is not a proper distribution
#   # "fullElectFrequency": cp.DiscreteUniform(2*0.85,2*1.15),
#   "stepspercycle": cp.DiscreteUniform(10*0.85,10*1.15),
#   "PMEGridSpacing": cp.Uniform(1.0*0.85,1.0*1.15),
#   "minimize": cp.DiscreteUniform(1000*0.85,1000*1.15),
#   "temperature": cp.Uniform(50.0*0.85,50.0*1.15),
#   "reassignFreq": cp.DiscreteUniform(100*0.85,100*1.15),
#   "reassignIncr": cp.Uniform(1.0*0.85,1.0*1.15),
#   "langevinDamping": cp.Uniform(5.0*0.85,5.0*1.15),
#   # "langevinHydrogen": ["yes", "no"],
#   # "useGroupPressure": ["yes", "no"],
#   "BerendsenPressureCompressibility": cp.Uniform(0.0000457*0.85,0.0000457*1.15),
#   "BerendsenPressureRelaxationTime": cp.Uniform(100.0*0.85,100.0*1.15),
#   #Below will only sample 2, is not a proper distribution
#   # "BerendsenPressureFreq": cp.DiscreteUniform(2*0.85,2*1.15),  
# }

#PARAMETERS WITH NO DISCRETE DISTRIBUTIONS
vary = {
  "langevinTemp": cp.Uniform(300.0*0.85,300.0*1.15),
  # "time_factor_eq": cp.Uniform(60000.0*0.85,60000.0*1.15),
  # "run_stepcount_factor": cp.DiscreteUniform(30000*0.85,30000*1.15),
  "BerendsenPressureTarget": cp.Uniform(1.01325*0.85,1.01325*1.15),
  # "time_sim1": cp.Uniform(10000000.0*0.85,10000000.0*1.15),
  # "box_size": cp.Uniform(14.0*0.85,14.0*1.15),
  "cutoff": cp.Uniform(12.0*0.85,12.0*1.15),
  # "switching": ["on", "off"],
  "timestep": cp.Uniform(2.0*0.85,2.0*1.15),
  # "rigidBonds": ["none", "water", "all"],
  "rigidtolerance": cp.Uniform(0.00001*0.85,0.00001*1.15),
  "rigidIterations": cp.Uniform(100*0.85,100*1.15),
  #Below will only sample 1, is not a proper distribution
  # "nonbondedFreq": cp.DiscreteUniform(1*0.85,1*1.15),
  #Below will only sample 2, is not a proper distribution
  # "fullElectFrequency": cp.DiscreteUniform(2*0.85,2*1.15),
  "stepspercycle": cp.Uniform(10*0.85,10*1.15),
  "PMEGridSpacing": cp.Uniform(1.0*0.85,1.0*1.15),
  "minimize": cp.DiscreteUniform(1000*0.85,1000*1.15),
  "temperature": cp.Uniform(50.0*0.85,50.0*1.15),
  "reassignFreq": cp.Uniform(100*0.85,100*1.15),
  "reassignIncr": cp.Uniform(1.0*0.85,1.0*1.15),
  "langevinDamping": cp.Uniform(5.0*0.85,5.0*1.15),
  # "langevinHydrogen": ["yes", "no"],
  # "useGroupPressure": ["yes", "no"],
  "BerendsenPressureCompressibility": cp.Uniform(0.0000457*0.85,0.0000457*1.15),
  "BerendsenPressureRelaxationTime": cp.Uniform(100.0*0.85,100.0*1.15),
  #Below will only sample 2, is not a proper distribution
  # "BerendsenPressureFreq": cp.DiscreteUniform(2*0.85,2*1.15),  
}

fnames = ['./g15/replica-confs/eq0.conf',
          './g15/replica-confs/eq1.conf',
          './g15/replica-confs/eq2.conf',
          './g15/replica-confs/sim1.conf']

xi = []
for param in vary:
    found = False
    for fname in fnames:
        location = search_string_in_file(fname, param.replace('_', ' '))
        # xi.append(float(lines[location[0][0]]))
        if location != []:
            param = location[0][1].split()[1]
            xi.append(np.float(param))
            break
        
result = poly_model(xi)

# output csv file
header = 'binding_energy_avg'
np.savetxt('output.csv', np.array([result]),
           delimiter=",", comments='',
           header=header)