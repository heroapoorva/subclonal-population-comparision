import os
import copy
import csv
import subprocess
import time
import yaml

from collections import Counter

from input_utils.dir_manager import *
from input_utils.utils import *

P = os.path

INPUT_TSV_HEADER = ["mutation_id", "ref_counts", "var_counts", "normal_cn", "minor_cn", "major_cn"]
OUTPUT_TSV_NAME = "%s.cellular_prevalence.tsv"
OUTPUT_BZ2_NAME = OUTPUT_TSV_NAME + ".bz2"

# Will use cached output from previous PyClone runs when this is true.
DEBUG = False
# Will cache output of PyClone for future runs when this is set to True. To use cached output, set DEBUG flag to True.
SAVE_OUTPUT = False


# Class to run PyClone on a given CCFInputSample, make PyClone input, and read PyClone output.
class PycloneAnalysis:

    # args is a dictionary holding PyClone parameters from pipeline_config.yml
    def __init__(self, args):
        self.args = args
        self.verify_args()
        return

    # TODO: Write code to verify args to PyClone passed via config file
    def verify_args(self):
        return

    # Make a PyClone specific mutation name string.
    @staticmethod
    def mutation_name_to_string(sample, mutation):
        return "%s:chr%s:%s" % (sample.name, mutation.chromosome, mutation.position)

    # Create input TSV for PyClone
    def create_input_tsv(self, sample):
        DirectoryManager.clean_temp_dir(sample.name)
        temp_dir = DirectoryManager.get_temp_dir(sample.name)
        input_tsv_name = "pyclone_input_%s.tsv" % sample.name
        input_tsv_path = P.abspath(P.join(temp_dir, input_tsv_name))
        with open(input_tsv_path, "wb+") as tsv_file:
            writer = csv.writer(tsv_file, delimiter='\t')
            writer.writerow(INPUT_TSV_HEADER)

            for segment in sample.chromosome_segments:
                for mutation in segment.mutations:
                    row = [
                        self.mutation_name_to_string(sample, mutation),
                        mutation.ref_count,
                        mutation.var_count,
                        segment.copy_number,
                        segment.minor_cn,
                        segment.major_cn
                    ]
                    writer.writerow(row)

        return input_tsv_path

    # Run PyClone on input TSV using given config. PyClone output can be cached to speed up debugging. See DEBUG and
    # SAVE_OUTPUT flags.
    @staticmethod
    def run_pyclone(input_tsv_path, pyclone_config):

        out_dir = pyclone_config['working_dir']
        sample_name = pyclone_config['samples'].keys()[0]

        out_tsv_name = OUTPUT_TSV_NAME % sample_name
        out_bz2_name = OUTPUT_BZ2_NAME % sample_name

        # test_file is used in debugging only. It just lets us cache the output somewhere where we can reuse it, instead
        # of rerunning PyClone all the time, which is a lengthy process.
        test_file = P.join(__file__, os.pardir)
        test_file = P.join(test_file, "../sample_output/pyclone/trace/" + out_bz2_name)
        test_file = P.realpath(test_file)

        print(test_file)

        if DEBUG:
            print "DEBUG CODE ACTIVE, SKIPPING PYCLONE"

            if not P.isfile(test_file):
                raise Exception("Missing %s from sample output. Debug data is incomplete." % out_bz2_name)

            trace_dir = P.abspath(P.join(out_dir, "trace"))
            if not P.isdir(trace_dir):
                os.makedirs(trace_dir)
            trace_file = P.join(trace_dir, out_bz2_name)

            shutil.copy(test_file, trace_file)

        else:
            mutations_file = P.abspath(P.join(out_dir, "mutations.yml"))
            print(mutations_file)
            print(input_tsv_path)

            subprocess.call([
                "PyClone",
                "build_mutations_file",
                "--in_file",
                input_tsv_path,
                "--out_file",
                mutations_file
            ], shell=False)

            pyclone_config_file = P.abspath(P.join(out_dir, "pyclone_config.yml"))
            pyclone_config['samples'][sample_name]['mutations_file'] = mutations_file

            with open(pyclone_config_file, 'w') as o:
                yaml.dump(pyclone_config, o)

            subprocess.call([
                "PyClone",
                "run_analysis",
                "--config_file",
                pyclone_config_file
            ], shell=False)

        trace_file_zip = P.join(P.abspath(P.join(out_dir, "trace")), out_bz2_name)
        trace_file_tsv = P.join(P.abspath(P.join(out_dir, "trace")), out_tsv_name)

        if SAVE_OUTPUT:
            shutil.copy(trace_file_zip, test_file)

        decompress_bz2(trace_file_zip, trace_file_tsv)
        return trace_file_tsv

    # Read output of PyClone, and assign each mutation its estimated CCF.
    def read_pyclone_output(self, sample, output_tsv):
        with open(output_tsv, "r") as tsv_file:
            reader = csv.reader(tsv_file, delimiter='\t')
            columns = next(reader)

            columns_dict = {}
            for column in columns:
                columns_dict[column] = []

            for row in reader:
                for i in range(0, len(columns)):
                    columns_dict[columns[i]].append(float(row[i]))

            modes_dict = {}

            # take the mode of every column to find the cellular prevalence for that column
            for mutation_name, cellular_prevalences in columns_dict.iteritems():
                cellular_prevalences_counter = Counter(cellular_prevalences)
                cellular_prevalence = cellular_prevalences_counter.most_common(1)[0][0]
                modes_dict[mutation_name] = cellular_prevalence

            for segment in sample.chromosome_segments:
                for mutation in segment.mutations:
                    mutation_name = self.mutation_name_to_string(sample, mutation)
                    mutation.cellular_prevalence = modes_dict[mutation_name]
        return

    # Run a PyClone analysis on given CCFInputSample
    def run_analysis(self, sample):
        input_tsv_path = self.create_input_tsv(sample)
        temp_dir = DirectoryManager.get_temp_dir(sample.name)

        pyclone_config = copy.deepcopy(self.args)
        pyclone_config['samples'][sample.name] = pyclone_config['samples']['SAMPLE_NAME']
        pyclone_config['samples'].pop('SAMPLE_NAME', None)
        pyclone_config['samples'][sample.name]['tumour_content']['value'] = float(sample.purity)
        pyclone_config['working_dir'] = temp_dir

        start = time.time()
        print "PyClone Started at %s" % str(start)

        output_tsv = self.run_pyclone(input_tsv_path, pyclone_config)
        self.read_pyclone_output(sample, output_tsv)

        end = time.time()
        print "Ended at %s" % str(end)
        print "Elapsed: %s" % str(end - start)

        return
