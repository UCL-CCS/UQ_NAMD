"""
=============================================================================
Create a Jinja templates for the eq0, eq1, eq2 and sim1.conf NAMD input files

Stores all parameters in a single JSON input file (params.json) and generates
template_[input_file]
=============================================================================
"""

def make_template(param_file):
    """
    Make the template for param_file

    param_file: string
         the name of the input file
    """
    print(param_file)
    #original file
    fp = open(param_file, 'r')
    #template file
    fp_template = open('template_' + param_file, 'w')
    #read all lines of original
    lines = fp.readlines()
    #some input files contain 'while' code segments, skip these parts
    skip_start, skip_end = skip_code_segments(lines)
    skip_intervals = np.array([skip_start, skip_end]).T
    idx = 0
    for line in lines:
        #strip away all white space of a line
        line = line.strip()
        #check if we're in a while code segment
        skip = False
        for skip_interval in skip_intervals:
            if idx >= skip_interval[0] and idx <= skip_interval[1]:
                skip = True
                break
        #empty line, write as is
        if len(line) == 0:
            fp_template.write(line + '\n')
        #comment line, write as is
        elif line[0] == '#':
            fp_template.write(line + '\n')
        #line in while segment, write as is
        elif skip:
            fp_template.write(line + '\n')
        #actual parameter line
        else:
            #while if there is an inline comment
            tmp = line.split('#')
            if len(tmp) > 1:
                comment = tmp[1]
            else:
                comment = ''
            #what remains is: parameter_name  parameter_value
            input_var = tmp[0].split()
            #normal case: input value
            if not 'set' in input_var:
                #parameter_name
                input_name = input_var[0]
                #parameter_value
                default_value = input_var[1]
            #set case: set input value
            else:
                input_name = input_var[0] + ' ' + input_var[1]
                default_value = input_var[2]

            #this is the name that goes in params.json, which will be used
            #in the 'vary' dict in EasyVVUQ. Because different input file can share
            #parameter name, the name of the input file is added to the parameter name
            #For instance 'amber_eq0'
            easyvvuq_name = input_name + '_' + param_file.split('.')[0]
            #names should not start with a number: add _ in front
            #also, replace - with _ in an easyvvuq name
            if easyvvuq_name[0].isnumeric():
                easyvvuq_name = '_' + easyvvuq_name
            easyvvuq_name = easyvvuq_name.replace('-', '_')
            easyvvuq_name = easyvvuq_name.replace(' ', '_')

            #determine the type of the input parameter
            try:
                test = eval(default_value)
                test_type = type(test)
                #integer 
                if test_type is int:
                    type_ = 'integer'
                    #type_ = 'float'     #write integers as float as well
                elif test_type is float:
                    type_ = 'float'
                else:
                    type_ = 'string'  
            except:
                type_ = 'string'

            #add the parameter to params.json
            add_param(easyvvuq_name, type_, default_value)
            #Jinja formatting {{ parameter name }}
            easyvvuq_value = '{{ ' + easyvvuq_name + ' }}'
            #write the template file
            fp_template.write('%s\t\t\t%s\t\t; #%s\n' % (input_name, easyvvuq_value, comment))
        idx += 1

    fp.close()
    fp_template.close()

def add_param(name, typ, default):
    """
    Add the current parameter to the global JSON parameter file params.json

    Parameters
    ----------
    name : string
        Easyvvuq parameter name
    typ : string
        parameter type
    default : string
        Default value of the parameter.

    Returns
    -------
    None.

    """
    params[name] = {}
    if typ == 'string':
        params[name]['default'] = default
    elif typ == 'float':
        params[name]['default'] = np.float(default)
    elif typ == 'integer':
        params[name]['default'] = np.int(default)

    params[name]['type'] = typ

def skip_code_segments(lines):
    """
    Basically this just finds the start and end line number of the 'while' code segments
    which are found in some of the input files.

    Parameters
    ----------
    lines : list of strings
        the contents of the parameter file.

    Returns
    -------
    skip_start : list of integers
        line numbers of start of code segments.
    skip_end : list of integers
        line numbers of end of code segments.

    """
    skip_start = []
    skip_end = []
    for i in range(len(lines)):
        #start while
        if 'while' in lines[i]:
            skip_start.append(i)
        #end while
        if lines[i] == '}\n':
            skip_end.append(i)
    return skip_start, skip_end

import numpy as np
import sys
import json

params = {}
#Loop over all parameter input files specified at the command prompt:
#python3 create_jinja_template.py eq0.conf eq1.conf eq2.conf sim1.conf 
for param_file in sys.argv[1:]:
    make_template(param_file)
    json.dump(params, open('params.json','w'))
