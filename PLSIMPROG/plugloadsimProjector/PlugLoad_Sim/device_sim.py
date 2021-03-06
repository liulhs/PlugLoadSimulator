from PlugLoad_Sim.graph_data import make_graph,show_graph
'''
Simulates the device using a file that denotes whether a device is on or off at any given time with
with intervals designated in a csv file that follows the format

    device,state,on/off
    
    ie
    
    tv,on,111111010101111110000011111
'''
#from test.test_wsgiref import IntegrationTests #Likely Extraneous - turned off
import csv


def write_to_ifile(file_name: str, integration_period:int, input_generators: list):
    '''writes the strings generated by the string generators onto the input csv'''
    with open(file_name, 'w') as outfile:
        to_write = 'sample_rate:{}\n'.format(integration_period)
        for input_generator in input_generators:
            to_write += input_generator.generate_str()
        outfile.write(to_write)
        
def make_integral_array(power_array: list, integration_period: int):
    '''
    creates the array that represents the energy at each integration period
    
    can be thought of as a signal f[x] where the gaps interval between each
    x is the integration period.
    '''
    to_return = [0]
    for i in range(len(power_array)-1):
        to_return.append(energy_used(power_array[i:i+2], integration_period) + to_return[-1])
    return to_return

def write_to_csv(file_name, power_array: list, integral_array: list, integration_time):
    '''
    writes the graphs data onto a csv file with the following format
    
    time,power,energy
    0,0,0
    x,y,z
    . . .
    . . .
    . . .
    '''
    time_array = list(range(0, len(power_array)*integration_time, integration_time))
    with open(file_name, 'w+', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
#         csv_file.write('time,')
#         csv_writer.writerow(time_array)
#         csv_file.write('power,')
#         csv_writer.writerow(power_array)
#         csv_file.write('energy,')
#         csv_writer.writerow(integral_array)
    
        csv_writer.writerow(['time', 'power', 'energy'])
        for t,p,e in zip(time_array, power_array, integral_array):
            csv_writer.writerow([t,p,e])
            
        csv_file.close()
        
def analyze_data(file_name: str, integration_period: int, device_map: dict):
    '''    
    a function that takes it all together, takes the csv file and from it makes all the necessary
    calculations.
    
        + calculates the power
        + graphs the power vs the time
        + graphs the energy used vs time
        + writes the graphs onto csvs
    '''
    power_map = parse_inputfile(file_name, device_map)
    power_matrix = list(power_map.values())       
    power_array = flatten_cols(power_matrix)
    integral_array = make_integral_array(power_array, integration_period)
    
    print('\nEnergy Used: ', integral_array[-1], 'Watt-hours')
    make_graph(power_array, integration_period,'', 'Power (W)', 'Power Consumed',sub=211)
    make_graph(integral_array, integration_period, 'Time (hr)', 'Energy (W*hr)', 'Energy Used',sub=212)
    write_to_csv('outputs/graph_file.csv', power_array, integral_array, integration_period)
    show_graph()
    
def analyze_data_nograph(file_name: str, integration_period: int, device_map: dict):
    power_map = parse_inputfile(file_name, device_map)
    power_matrix = list(power_map.values())       
    power_array = flatten_cols(power_matrix)
    integral_array = make_integral_array(power_array, integration_period)
    
    return (power_map, power_matrix, power_array, integral_array)
    
def energy_used(power_array, int_period: int):
    '''trapezoidal riemman sum estimate of the amount of power used'''
    return (sum(power_array[1:])/3600*int_period + sum(power_array[:len(power_array)-1])/3600*int_period)/2

def make_int_array(size, start_value=0):
    '''returns an int list of length size with values start_value, default being 0'''
    to_return = []
    for i in range(size):
        to_return.append(0)
    
    return to_return

def flatten_cols(matrix: [list])->list:
    '''flatten a matrix by m by n into a array of size m by adding columns together
    ie
        | a_00 a_10 ... a_m0 |
        | a_01 ............. |
        |  ................. |  = [a_00 + a_01 + .. + a_0n, a_10 + a_11 + ... + a_1n, a_m0 + a_m1 + ... + a_mn]
        | a_0n ........ a_mn |
    '''
    
    to_return = []
    size = len(matrix[0])
    
    for j in range(size):
        to_append = 0
        for i in range(len(matrix)):
            assert(len(matrix[i]) == size)
            to_append += matrix[i][j]
        to_return.append(to_append)
        
    return to_return

def parse_inputstring(device, state, device_map, i_string:str, to_write:list)->list:
    '''an input string is a string of 1s and 0s that represent whether or not the device,state is on at
    a given time interval
    '''
    assert(len(to_write) == len(i_string))
    for i in range(len(i_string)):
        inst_st = int(i_string[i])
        if inst_st == 1:
            assert(to_write[i] == 0) # assert that to_write is already empty
        to_write[i] += int(inst_st)* device_map[device][state]
    
    return to_write

def parse_inputfile(file, device_map)-> dict:
    '''parses the device input file which is a csv file with format
    device, state, on/off string
    
    on/off string denotes with a 1 or a 0 whether or not a device is on during that time
    '''
    to_return = {}
    
    with open(file, 'r') as i_file:
        for line in i_file:
            if line[:11] == 'sample_rate':
                pass #lol beautiful code right here ima keep this for kicks
            else:
                info = line.rstrip().split(',')
                device, state, i_string = info[0], info[1], info[2]
                
                if(not device in to_return):
                    to_return[device] = make_int_array(len(i_string))
                
                parse_inputstring(device, state, device_map, i_string, to_return[device])
    
    return to_return

def mapval_to_matrix(map: dict)->list:

    # maybe do some error checking here?
    
    return list(map.values())
            
    
    
if __name__ == '__main__':
    # rudimentary testing
    
    # test flatten_cols
    assert(flatten_cols([[1,3,4],
                         [2,3,4],
                         [5,6,7]]) == [8,12,15])
    
    # test parse_input_srting
    power_array = [0,0,0,0,0,0,0,0,0,0]
    dev_map = {'television': {'on':100, 'off':0, 'standby':25}, 'xbox': {'on':70, 'off':0, 'standby':20}}
    input_str_tv = '1110000111'
    input_str_stndby = '0001111000'
    
    parse_inputstring('television', 'on', dev_map, input_str_tv, power_array)
    parse_inputstring('television', 'standby', dev_map, input_str_stndby, power_array)
    assert(power_array == [100, 100, 100, 25, 25, 25, 25, 100, 100, 100])
    print(energy_used(power_array, 1800))
    print(make_integral_array(power_array, 1800))
    
    # test parse_inputfile
    
    #d = parse_inputfile('test_input.csv', dev_map)
    #print(d)
    
    