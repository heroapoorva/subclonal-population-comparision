import os

from ccf_analysis.ccube_analysis import CCubeAnalysis
from ccf_analysis.phylowgs_analysis import PhylowgsAnalysis
from ccf_analysis.pyclone_analysis import PycloneAnalysis
from classifiers.bin10_classifier import Bin10Classifier
from topic_modeling.nmf import NMFModeler
from input_utils.simulation_input_reader import SimulationInputReader
from input_utils.realdata500_input_reader import RealData500InputReader

P = os.path

SIMULATIONS_FOLDERS = {
    SimulationInputReader: {"Segments", "Truth_Values", "VCFs"},
    RealData500InputReader: {"BB", "Segments", "VCF"}
}


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


def identify_ccf_analysis(alg, config):
    if alg == 'pyclone':
        return PycloneAnalysis(config['pyclone_params'])
    if alg == 'ccube':
        return CCubeAnalysis(config['ccube_params'])
    if alg == 'phylowgs':
        return PhylowgsAnalysis(config['phylowgs_params'])


# Based on args supplied via user input, identify which classifier to use to sort mutation CCF's into different classes.
def identify_classifier(args):
    return Bin10Classifier(args)


def identify_topic_modeler(args):
    return NMFModeler(args)