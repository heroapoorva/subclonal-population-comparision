import argparse
import yaml
from multiprocessing.dummy import Pool
from multiprocessing import cpu_count

from input_utils.ccf_input import MutationData
from input_utils.dir_manager import DirectoryManager
from input_utils.input_identifier import *
from input_utils.logging import PipelineLog

from ccf_analysis.error_analysis import ErrorAnalysis, ComputingErrors

P = os.path
Log = PipelineLog(0)

# This file is the main entrypoint of the pipeline. It will parse the command line parameters, and then execute the
# actions specified by the user.


# Gets absolute path to output directory from config file.
def get_out_dir(config):
    out_dir = P.abspath(P.join(os.getcwd(), config['output_dir']))
    if not P.isdir(out_dir):
        os.makedirs(out_dir)
    return out_dir


# Runs error analysis and outputs results to output directory.
def do_error_analysis(ccube_intermediates_dir,
                      pyclone_intermediates_dir,
                      phylowgs_intermediates_dir,
                      in_reader,
                      out_dir):

    if not P.isdir(ccube_intermediates_dir):
        print "Error, CCube intermediates dir given at '%s' does not exist" % ccube_intermediates_dir
        return

    if not P.isdir(pyclone_intermediates_dir):
        print "Error, PyClone intermediates dir given at '%s' does not exist" % pyclone_intermediates_dir
        return

    if not P.isdir(phylowgs_intermediates_dir):
        print "Error, PhyloWGS intermediates dir given at '%s' does not exist" % phylowgs_intermediates_dir
        return

    error1 = ComputingErrors(ccube_intermediates_dir, in_reader, out_dir)
    error2 = ComputingErrors(pyclone_intermediates_dir, in_reader, out_dir)
    error3 = ComputingErrors(phylowgs_intermediates_dir, in_reader, out_dir)

    ComputingErrors.boxplot_classes(error1.bins_errors, out_dir, error1.name)
    ComputingErrors.boxplot_classes(error2.bins_errors, out_dir, error2.name)
    ComputingErrors.boxplot_classes(error3.bins_errors, out_dir, error3.name)

    ErrorAnalysis.compare_all_ccfs(error1, error2, error3, out_dir)

    return


# Due to our use of multiprocessing, and the fact that you cannot pass more than one parameter to functions executed
# by the multiprocessing thread pool, these input parameters to the function are passed in as global variables.
input_reader = None
ccf_analysis = None


# Run error analysis using given intermediate directories. There must be at least 3 intermediate directories for CCube,
# PyClone, and PhyloWGS respectively.
def run_error_analysis(config, intermediate_dirs_list):
    if len(intermediate_dirs_list) != 3:
        print "Error: Please pass in the 3 paths for the intermediate data folders for all 3 CCF analysis"
        return

    ccube_dir = intermediate_dirs_list[0]
    pyclone_dir = intermediate_dirs_list[1]
    phylowgs_dir = intermediate_dirs_list[2]

    input_dir = P.abspath(P.join(os.getcwd(), config['input_dir']))
    if not P.isdir(input_dir):
        print "Couldn't find input directory at '%s'!" \
              " Please make sure a valid input directory is specified in 'pipeline_config.yml'" % input_dir
        return

    global input_reader
    input_reader = identify_input_reader(input_dir)

    out_dir = get_out_dir(config)

    do_error_analysis(ccube_dir, pyclone_dir, phylowgs_dir, input_reader, out_dir)
    return


# Run a CCF analysis on a sample with the given name. In a multithreaded analysis run, this function will be called
# in parallel by multiprocessing's map() function. Results of the CCF analysis are saved to the 'intermediates' folder in
# the output folder.
def run_single_analysis(sample_name):
    global input_reader, ccf_analysis
    intermediates_dir = DirectoryManager.get_intermediates_dir()
    sample = input_reader.read_sample_data(sample_name)
    ccf_analysis.run_analysis(sample)
    out_file = P.join(intermediates_dir, "%s%s" % (sample_name, MutationData.OUT_FILE_EXT))
    MutationData.save_mutation_data(sample, out_file)
    Log.incrementSams()
    print(Log.progress())
    return sample_name


# Run the full pipeline, including CCF analysis, classification, and topic modeling. CCF analysis results will be saved
# to the 'intermediates' folder in the output directory. They can later be reused by the user using command line option
# --use-intermediate-data
def run_pipeline(config):
    input_dir = P.abspath(P.join(os.getcwd(), config['input_dir']))
    if not P.isdir(input_dir):
        raise "Couldn't find input directory at '%s'!" % input_dir

    num_threads = 1
    if 'multicore' in config and config['multicore']:
        if 'num_cpu' in config:
            num_threads = config['num_cpu']
        else:
            num_threads = cpu_count()
    thread_pool = Pool(num_threads)

    out_dir = get_out_dir(config)

    DirectoryManager.reset_out_dir(out_dir)
    DirectoryManager.clean_all_temp_data()
    intermediates_dir = DirectoryManager.get_intermediates_dir()

    global input_reader, ccf_analysis
    input_reader = identify_input_reader(input_dir)
    ccf_analysis = identify_ccf_analysis(config['ccf_algorithm'], config)

    classifier = identify_classifier(config)
    topic_modelers = identify_topic_modelers(config)

    sample_names = input_reader.get_sample_names()
    Log.setTotalSamples(len(sample_names))
    if num_threads == 1:
        for sample_name in sample_names:
            run_single_analysis(sample_name)
    else:
        thread_pool.map(run_single_analysis, sample_names)

    print(Log.completedCCF())

    classifier.classify_all_mutation_files(intermediates_dir)
    classifier.write_classified_data_tsv(P.join(out_dir, "classified_data.tsv"))

    print(Log.completedClass())

    if input_reader.has_truth_dir():
        if 'error_analysis' in config and config['error_analysis']:
            ErrorAnalysis.run_error_analysis(intermediates_dir, input_reader, out_dir)

    for topic_modeler in topic_modelers:
        topic_modeler.extract_topics_from_classified_data(classifier)
        topic_modeler.write_output(out_dir)

    print(Log.completedTM())

    return


# Run classification and topic modelling on given intermediate data. This function corresponds to the
#  --use-intermediate-data command line parameter.
def run_intermediates(config, intermediates_dir):
    input_dir = P.abspath(P.join(os.getcwd(), config['input_dir']))
    if not P.isdir(input_dir):
        raise "Couldn't find input directory at '%s'!" % input_dir
    if not P.isdir(intermediates_dir):
        raise "Couldn't find given intermediates directory at '%s'!" % intermediates_dir

    global input_reader
    out_dir = get_out_dir(config)
    input_reader = identify_input_reader(input_dir)
    classifier = identify_classifier(config)
    topic_modelers = identify_topic_modelers(config)

    print(Log.completedCCF())

    classifier.classify_all_mutation_files(intermediates_dir)
    classifier.write_classified_data_tsv(P.join(out_dir, "classified_data.tsv"))

    print(Log.completedClass())

    if input_reader.has_truth_dir():
        if 'error_analysis' in config and config['error_analysis']:
            ErrorAnalysis.run_error_analysis(intermediates_dir, input_reader, out_dir)

    for topic_modeler in topic_modelers:
        topic_modeler.extract_topics_from_classified_data(classifier)
        topic_modeler.write_output(out_dir)

    print(Log.completedTM())

    return


# Run topic modeling on the given TSV of classified data. This function corresponds to the --use-classified-data
#  command line parameter.
def run_classified(config, classified_data_tsv):
    if not P.isfile(classified_data_tsv):
        raise "Couldn't find given classified data TSV file at '%s'!" % classified_data_tsv

    out_dir = get_out_dir(config)

    classifier = identify_classifier(config)

    print(Log.completedCCF())
    print(Log.completedClass())

    topic_modelers = identify_topic_modelers(config)

    classifier.read_classified_data_tsv(classified_data_tsv)

    for topic_modeler in topic_modelers:
        topic_modeler.extract_topics_from_classified_data(classifier)
        topic_modeler.write_output(out_dir)

    print(Log.completedTM())

    return


# main entrypoint of the program. Parses command line options and runs functions for pipeline and analysis.
def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-c", "--config", type=str,
                        help="Path for pipeline config file", default='./yaml/pipeline_config.yml')
    parser.add_argument("-i", "--use-intermediate-data", type=str,
                        help="Specifies folder of intermediate data files to use. Skips running CCF analysis. Only runs bin10 classification and topic modeling.", default=None)
    parser.add_argument("-a", "--use-classified-data", type=str,
                        help="Specifies TSV of classified data to use. Skips running CCF analysis and bin10 classification. Only runs topic modeling.", default=None)
    parser.add_argument("-e", "--error-analysis", nargs='*',
                        help="Runs error analysis on given folders of intermediate data. \n"
                                "3 arguments must be passed in the following order: \n"
                                "- The path to the CCube Intermediate Data folder \n"
                                "- The path to the PyClone Intermediate Data folder. \n"
                                "- The path to the PhyloWGS Intermediate Data folder. \n"
                                "Please note that this option also requires that a valid input directory be specified in 'pipeline_config.yml'",
                        default=None)
    args = parser.parse_args()

    if not P.isfile(args.config):
        print "Invalid config file specified! Config file does not exist."
        return

    with open(args.config) as f:
        doc = yaml.safe_load(f)

    if args.use_intermediate_data is not None:
        run_intermediates(doc, args.use_intermediate_data)
    elif args.use_classified_data is not None:
        run_classified(doc, args.use_classified_data)
    elif args.error_analysis is not None:
        run_error_analysis(doc, args.error_analysis)
    else:
        run_pipeline(doc)

    DirectoryManager.clean_all_temp_data()

    return


if __name__ == "__main__":
    main()
