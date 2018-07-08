import os

from ccf_analysis.ccube_analysis import CCubeAnalysis
from ccf_analysis.phylowgs_analysis import PhylowgsAnalysis
from ccf_analysis.pyclone_analysis import PycloneAnalysis
from classifiers.bin10_classifier import Bin10Classifier
from topic_modeling.nmf import NMFModeler
from topic_modeling.lda import LDAModeler
from input_utils.simulation_input_reader import SimulationInputReader
from input_utils.realdata500_input_reader import RealData500InputReader

P = os.path

SIMULATIONS_FOLDERS = {
    SimulationInputReader: {"Segments", "Truth_Values", "VCFs", "BB"},
    RealData500InputReader: {"data", "truth"}
}


# This function will identify the input type based on the input directory structure, and will return a class capable
# of parsing the input. Note that all classes returned must have a constructor which accepts a path to the input dir
# as an argument, and must have a function called get_sample_names() to return a list of all sample names, and
# a function called 'read_sample_data(sample_name)' which returns a CCFInputSample object.
def identify_input_reader(input_path):
    for input_reader in SIMULATIONS_FOLDERS:
        input_folders = SIMULATIONS_FOLDERS[input_reader]
        input_identified = True
        for f in input_folders:
            if not P.isdir(P.join(input_path, f)):
                input_identified = False
                break
        if input_identified:
            return input_reader(input_path)
    return ""


# Identify CCF analysis to use based on user input.
def identify_ccf_analysis(alg, config):
    if alg == 'pyclone':
        return PycloneAnalysis(config['pyclone_params'])
    if alg == 'ccube':
        return CCubeAnalysis(config['ccube_params'])
    if alg == 'phylowgs':
        return PhylowgsAnalysis(config['phylowgs_params'])


# Based on args supplied via user input, identify which classifier to use to sort mutation CCF's into different classes.
def identify_classifier(args):
    # Always use Bin10Classifier
    return Bin10Classifier(args)


def identify_topic_modelers(args):
    # Always run both NMF and LDA on classified data to do topic modeling.
    return [NMFModeler(args), LDAModeler(args)]
