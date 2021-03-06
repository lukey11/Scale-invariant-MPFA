from lxml import etree
import numpy as np
import copy
import csv
import argparse
import pdb


LINUX_CONTROLLER_LIB = "build/controllers/libiAnt_controller.so"
MAC_CONTROLLER_LIB = "build/controllers/libiAnt_controller.dylib"
LINUX_LOOP_LIB = "build/loop_functions/libiAnt_loop_functions.so"
MAC_LOOP_LIB = "build/loop_functions/libiAnt_loop_functions.dylib"
    
PARAMETER_LIMITS = {
    "X": (0, 4),
    "Y": (0, 4)
}

def load_xml_default(xml_file):
    #filename = raw_input('Choose a file name(e.g. cluster_2_mac.argos)')
    #name_and_extension = filename.split(".")
    fileFullPath = "./experiments/"+xml_file
    f= open(fileFullPath)
    content = f.readlines()
    result=""
    for line in content:
        result +=line
    #return result, name_and_extension[0]
    return result

#ARGOS_XML_DEFAULT, XML_FILE_NAME = load_xml_default() #qilu 11/20/2015

#def default_argos_xml(robots, time, system="linux"):
def default_argos_xml(xml_file, time, system="linux"):
    ARGOS_XML_DEFAULT= load_xml_default(xml_file) 
    xml = etree.fromstring(ARGOS_XML_DEFAULT)
    #xml.find("arena").find("distribute").find(
    #"entity").attrib["quantity"] = str(robots)
    #exp_att = xml.find("framework").find("experiment").attrib
    #exp_att.update({"length": str(time)})

    if system == "linux":
        return xml
    elif system == "darwin":
        xml.find("controllers").find(
            "iAnt_controller").attrib["library"] = MAC_CONTROLLER_LIB
        xml.find("loop_functions").attrib["library"] = MAC_LOOP_LIB
        return xml
    else:
        return None


def uniform_rand_argos_xml(xml_file, robots, time, system="linux"):
    #xml = default_argos_xml(robots, time, system)
    xml = default_argos_xml(xml_file, time=time, system=system)
    parameters = {}
    for key in PARAMETER_LIMITS:
        if key == "RateOfPheromoneDecay":
            parameters[key] = str(np.random.exponential(0.1))
        elif key == "RateOfInformedSearchDecay":
            parameters[key] = str(np.random.exponential(0.2))
        else:
            parameters[key] = str(np.random.uniform(PARAMETER_LIMITS[key][0], PARAMETER_LIMITS[key][1]))
    set_parameters(xml, parameters)    
    return xml


def get_parameters(argos_xml):
    framework_CPFA = argos_xml.find("loop_functions").find("CPFA")
    framework_MPFA = argos_xml.find("loop_functions").find("MPFA")

    if framework_CPFA != None:
        return framework_CPFA.attrib
    elif framework_MPFA != None:
        return framework_MPFA.attrib


def set_parameters(argos_xml, parameters_update):
    framework_CPFA = argos_xml.find("loop_functions").find("CPFA")
    framework_MPFA = argos_xml.find("loop_functions").find("MPFA")

    if framework_CPFA != None:
        attrib = framework_CPFA.attrib
    elif framework_MPFA != None:
        attrib = framework_MPFA.attrib
    attrib.update(parameters_update)

def set_seed(argos_xml, seed):
    attrib = argos_xml.find("framework").find("experiment").attrib
    attrib.update({"random_seed": str(int(seed))})


def mutate_parameters(parameters, probability):
    
    for key in PARAMETER_LIMITS:
        if np.random.uniform() < probability:
            val = parameters[key]
            val += PARAMETER_LIMITS[key][1]*np.random.normal(0, 0.02)  # It should be scaled by the range of each parameter 10/12/2015
	    while(val > PARAMETER_LIMITS[key][1] or val < PARAMETER_LIMITS[key][0]):
                if val > PARAMETER_LIMITS[key][1]:
                    val = 2*PARAMETER_LIMITS[key][1]-val
                elif val < PARAMETER_LIMITS[key][0]:
                    val = 2*PARAMETER_LIMITS[key][0]-val
            parameters[key] = val
     

#qilu 11/21/2015
def two_point_crossover(xml_file, p1_xml, p2_xml, system="linux"):
    p1_parameters = copy.deepcopy(get_parameters(p1_xml))
    # Initialize child to parent 2
    child_parameters = copy.deepcopy(get_parameters(p2_xml))
    point1 = np.random.randint(0, len(p1_parameters))
    point2 = np.random.randint(0, len(p1_parameters))
    if point1< point2: 
        minPoint = point1
        maxPoint = point2
    else:
        minPoint = point2
        maxPoint = point1
    from_p1 = False
    count = 0
    for key in PARAMETER_LIMITS:
        #if from_p1:
        if count>= minPoint and count<=maxPoint:
            child_parameters[key] = p1_parameters[key]
        count += 1 
        from_p1 = not from_p1
    parent_time = p1_xml.find("framework").find("experiment").attrib["length"] # do we need these two lines? qilu 07/27
    parent_robots = p1_xml.find("arena").find("distribute").find(
        "entity").attrib["quantity"]
    #child = default_argos_xml(system=system, time=parent_time, robots=parent_robots)
    child = default_argos_xml(xml_file, system=system, time=parent_time)
    set_parameters(child, child_parameters)
    return child

def uniform_crossover(p1_xml, p2_xml, rate, system="linux"):
    p1_parameters = copy.deepcopy(p1_xml)
    p2_parameters = copy.deepcopy(p2_xml)
    # initialize children
    child1_parameters = copy.deepcopy(p1_xml)
    child2_parameters = copy.deepcopy(p2_xml)
    
    flag=False
    for key in PARAMETER_LIMITS:
        if np.random.uniform()<rate:
            flag =True
            child1_parameters[key] = p2_parameters[key]
            child2_parameters[key] = p1_parameters[key]

    if flag:
        return [child1_parameters, child2_parameters]
    else:
        # no cross over
        return [p1_xml, p2_xml]
    

#def uniform_crossover(p1_xml, p2_xml, system="linux"):
#    p1_parameters = copy.deepcopy(get_parameters(p1_xml))
#    # Initialize child to parent 2
#    child_parameters = copy.deepcopy(get_parameters(p2_xml))
#    from_p1 = False
#    for key in PARAMETER_LIMITS:
#        if from_p1:
#            child_parameters[key] = p1_parameters[key]
#        from_p1 = not from_p1
#    parent_time = p1_xml.find("framework").find("experiment").attrib["length"]
#    parent_robots = p1_xml.find("arena").find("distribute").find(
#        "entity").attrib["quantity"]
#    #child = default_argos_xml(system=system, time=parent_time, robots=parent_robots)
#    child = default_argos_xml(system=system, time=parent_time)
#    set_parameters(child, child_parameters)    
#    return child

def read_pop_from_csv(filename):
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        return list(reader)

def xml_string_parameter_chunk(parameters):
    #xml = default_argos_xml(6, 3600)
    xml = default_argos_xml(xml_file, time = 3600)

    framework_CPFA = xml.find("loop_functions").find("CPFA")
    framework_MPFA = xml.find("loop_functions").find("MPFA")
    if framework_CPFA != None:
        framework_CPFA.attrib.update(parameters)
        return etree.tostring(framework_CPFA)
    elif framework_MPFA != None:
        framework_MPFA.attrib.update(parameters)
        return etree.tostring(framework_MPFA)


def create_argos_from_paramters(parameters, searchRadius, robots, length, system):
    #xml = default_argos_xml(robots, length, system)
    xml = default_argos_xml(xml_file, time =length, system =system)
    framework_CPFA = xml.find("loop_functions").find("CPFA")
    framework_MPFA = xml.find("loop_functions").find("MPFA")
    if framework_CPFA != None:
        framework_CPFA.attrib.update(parameters)
        framework_CPFA.attrib["searchRadius"] = searchRadius

    elif framework_MPFA != None:
        framework_MPFA.attrib.update(parameters)
        framework_MPFA.attrib["searchRadius"] = searchRadius

    return etree.tostring(xml, pretty_print=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Parameters XML printer')
    parser.add_argument('-f', '--gen_file', action='store', dest='gen_file', required=True)
    parser.add_argument('-a', '--all', action='store', dest='all')
    parser.add_argument('-s', '--searchradius', action='store', dest='sradius')
    parser.add_argument('-r', '--robots', action="store", dest="robots")
    parser.add_argument('-l', '--length', action='store', dest='length')
    parser.add_argument('-c', '--create', action="store_true", dest="create")
    parser.add_argument('--system', action='store', dest='system')

    args = parser.parse_args()

    gen_file = args.gen_file
    robots='10'
    length='300'
    sradius='1'
    system='linux'

    pop = read_pop_from_csv(gen_file)
    
    if args.create:
        if args.length:
            length=args.length
        if args.sradius:
            sradius=args.sradius
        if args.robots:
            robots=args.robots
        if args.system:
            system = args.system
        print create_argos_from_paramters(pop[0], sradius, robots, length, system)
    elif args.all:
        for p in pop:
            print "Fitness:", p["fitness"]
            print xml_string_parameter_chunk(p)
    else:
        print "Fitness:", pop[0]["fitness"]
        print xml_string_parameter_chunk(pop[0])
