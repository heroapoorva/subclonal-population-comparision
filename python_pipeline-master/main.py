import argparse
import shutil

import yaml

from input_utils.ccf_input import MutationData
from input_utils.dir_manager import DirectoryManager
from input_utils.input_identifier import *

P = os.path

KEEP_INTERMEDIATES_DIR = True


def run_pipeline(config):

    input_dir = P.abspath(P.join(os.getcwd(), config['input_dir']))
    if not P.isdir(input_dir):
        raise "Couldn't find input directory at '%s'!" % input_dir

    out_dir = P.abspath(P.join(os.getcwd(), config['output_dir']))
    if not P.isdir(out_dir):
        os.makedirs(out_dir)

    DirectoryManager.reset_out_dir(out_dir)
    intermediates_dir = DirectoryManager.get_intermediates_dir()

    input_reader = identify_input_reader(input_dir)
    ccf_analysis = identify_ccf_analysis(config['ccf_algorithm'], config)
    classifier = identify_classifier(config)
    topic_modeler = identify_topic_modeler(config)

    sample_names = input_reader.get_sample_names()
    for sample_name in sample_names:
        sample = input_reader.read_sample_data(sample_name)
        ccf_analysis.run_analysis(sample)
        out_file = P.join(intermediates_dir, "%s%s" % (sample_name, MutationData.OUT_FILE_EXT))
        MutationData.save_mutation_data(sample, out_file)

    classifier.classify_all_mutation_files(intermediates_dir)
    classifier.write_classified_data_tsv(P.join(out_dir, "classified_data.tsv"))

    topic_modeler.extract_topics_from_classified_data(classifier)
    topic_modeler.write_output(out_dir)

    if not KEEP_INTERMEDIATES_DIR:
        shutil.rmtree(intermediates_dir)

    return


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", type=str, help="Path for pipeline config file", default='./yaml/pipeline_config.yml')
    args = parser.parse_args() 

    with open(args.config) as f:
        doc = yaml.safe_load(f)

    run_pipeline(doc)

    return


if __name__ == "__main__":
    main()
