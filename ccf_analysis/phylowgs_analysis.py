import os
import csv
import subprocess
import time
import json

from input_utils.dir_manager import *
from input_utils.utils import *

P = os.path


# Class to run PhyloWGS on a sample, feed it input, and read the output.
class PhylowgsAnalysis:

    # args are config arguments taken from pipeline_config.yml
    def __init__(self, args):
        self.args = args
        self.verify_args()
        return

    # TODO: Write code to verify args to PhyloWGS passed via config file
    def verify_args(self):
        return

    # Compute the string name of a mutation
    @staticmethod
    def mutation_name_to_string(mutation):
        return "%s_%s" % (mutation.chromosome, mutation.position)

    # Read the output of PhyloWGS, and store each mutation's CCF in the corresponding MutationData object in
    # CCFInputSample.
    def read_phylowgs_output(self, sample, working_dir):

        # First read map of mutation IDs to SSM IDs.
        mutation_ssm_map = {}
        ssm_data_path = P.join(working_dir, "ssm_data.txt")
        with open(ssm_data_path, "r") as ssm_data_file:
            reader = csv.reader(ssm_data_file, delimiter='\t')
            reader.next()

            for row in reader:
                ssm_id = row[0]
                mutation_id = row[1]
                mutation_ssm_map[ssm_id] = mutation_id

        # Next read log of MCMC samples, and find the iteration which has the highest score.
        mcmc_samples_path = P.join(working_dir, "mcmc_samples.txt")
        best_iteration_score = -999999.0
        best_iteration = -1
        with open(mcmc_samples_path, "r") as mcmc_samples_file:
            reader = csv.reader(mcmc_samples_file, delimiter='\t')
            reader.next()

            for row in reader:
                iteration_num = int(row[0])

                # Only consider iterations 0 and above. Iterations below 0 are just MCMC burnin.
                if iteration_num >= 0:
                    iteration_score = float(row[1])

                    if iteration_score > best_iteration_score:
                        best_iteration = iteration_num

        if best_iteration == -1:
            raise "Could not find any MCMC sample iterations with a good score. (sample: %s)" % sample.name

        best_iteration = str(best_iteration)
        best_iteration_filename = best_iteration + ".json"

        # Next read all clusters from zipped file sample1_data.summ.json
        clusters = {}
        clusters_file_name = "sample1_data.summ.json"
        clusters_file_path = P.join(working_dir, clusters_file_name)
        clusters_zip_path = P.join(working_dir, clusters_file_name + ".gz")
        decompress_gzip(clusters_zip_path, clusters_file_path)

        with open(clusters_file_path, "r") as cluster_file:
            cluster_json = json.load(cluster_file)

            cluster_populations = cluster_json["trees"][best_iteration]["populations"]
            for i in range(0, len(cluster_populations)):
                cluster_num = str(i)
                cluster_info = cluster_populations[cluster_num]

                ccf = cluster_info["cellular_prevalence"][0]
                clusters[cluster_num] = str(ccf)

        # Next unzip the mutation assignments from the best iteration
        best_iterations_path = P.join(working_dir, best_iteration_filename)
        mut_assignments_zipfile = P.join(working_dir, "sample1_data.mutass.zip")
        unzip_single_file(mut_assignments_zipfile, best_iterations_path, best_iteration_filename)

        # Read the mutation assignments. Resolve their CCFs. Save CCF of each mutation to a dictionary.
        mutation_ccfs = {}
        with open(best_iterations_path, "r") as best_iteration_file:
            iterations_json = json.load(best_iteration_file)

            mut_assignments = iterations_json["mut_assignments"]
            for cluster_num in clusters:
                if cluster_num in mut_assignments:
                    cluster_ccf = clusters[cluster_num]
                    cluster_assignments = mut_assignments[cluster_num]["ssms"]

                    for ssm_id in cluster_assignments:
                        mutation_id = mutation_ssm_map[ssm_id]
                        mutation_ccfs[mutation_id] = cluster_ccf

        # Now loop through our MutationData, and assign a CCF to each mutation
        for segment in sample.chromosome_segments:
            for mutation in segment.mutations:
                mutation_name = self.mutation_name_to_string(mutation)
                if mutation_name not in mutation_ccfs:
                    print "Sample %s: PhyloWGS discarded mutation %s in segment %s (start %s end %s)" \
                                        % (sample.name, mutation_name, segment.chromosome, segment.start, segment.end)
                else:
                    mutation.cellular_prevalence = mutation_ccfs[mutation_name]

        return

    # Run PhyloWGS on given input sample. To make parallelization possible, each sample's CCF analysis is run in a
    # separate temp directory. Since PhyloWGS outputs hundreds of megabytes of data, each temp directory is cleaned
    # after running.
    def run_analysis(self, sample):
        temp_dir = DirectoryManager.get_temp_dir(sample.name)

        start = time.time()
        print "PhyloWGS Started at %s" % str(start)

        cnvs_file_path = P.join(temp_dir, "cnvs.txt")
        subprocess.call([
            "PhyloWGS_parse_cnvs",
            "-f",
            self.args['cnv_file_format'],
            "-c",
            sample.purity,
            "--cnv-output",
            cnvs_file_path,
            sample.bb_file_path
        ], shell=False, cwd=temp_dir)

        subprocess.call([
            "PhyloWGS_create_inputs",
            "--cnvs",
            "sample1=" + cnvs_file_path,
            "--vcf-type",
            "sample1=" + self.args['vcf_file_format'],
            "sample1=" + sample.vcf_file_path
        ], shell=False, cwd=temp_dir)

        cnv_data_path = P.join(temp_dir, "cnv_data.txt")
        ssm_data_path = P.join(temp_dir, "ssm_data.txt")

        pwgs_args = [
            "PhyloWGS",
            "-B",
            str(self.args['BURNIN_SAMPLES']),
            "-s",
            str(self.args['MCMC_SAMPLES']),
            "-i",
            str(self.args['MH_ITERATIONS'])
        ]

        if "TMP_DIR" in self.args:
            pwgs_args.append("-t")
            pwgs_args.append(self.args['TMP_DIR'])

        pwgs_args.append(ssm_data_path)
        pwgs_args.append(cnv_data_path)

        subprocess.call(pwgs_args, shell=False, cwd=temp_dir)

        subprocess.call([
            "PhyloWGS_write_results",
            "sample1_data",
            "trees.zip",
            "sample1_data.summ.json.gz",
            "sample1_data.muts.json.gz",
            "sample1_data.mutass.zip"
        ], shell=False, cwd=temp_dir)

        end = time.time()
        print "Ended at %s" % str(end)
        print "Elapsed: %s" % str(end - start)

        self.read_phylowgs_output(sample, temp_dir)

        DirectoryManager.clean_temp_dir(sample.name)

        return
