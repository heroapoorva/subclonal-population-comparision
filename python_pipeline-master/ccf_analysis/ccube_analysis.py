import os
import csv
import subprocess
import time
import shutil

from input_utils.dir_manager import DirectoryManager
from input_utils.utils import decompress_gzip

P = os.path

INPUT_TSV_HEADER = [
    "id",
    "gene",
    "ref_counts",
    "total_counts",
    "cn_frac",
    "major_cn",
    "minor_cn",
    "normal_cn",
    "var_counts",
    "mutation_id",
    "ccube_purity",
    "purity",
]

DEBUG = True
SAVE_OUTPUTS = False

CLUSTERS_FILE_NAME = "sample1_subclonal_structure.txt"
MUTATIONS_ASSIGNMENTS_FILE_NAME = "sample1_mutation_assignments.txt"


class CCubeAnalysis:

    def __init__(self, args):
        self.args = args
        self.verify_args()
        return

    # TODO: Write interface for CCube in R, then verify the args to CCube here.
    def verify_args(self):
        return

    @staticmethod
    def mutation_name_to_string(mutation):
        return "%s_%s" % (mutation.chromosome, mutation.position)

    @staticmethod
    def calc_vaf(var_count, ref_count):
        v_count = float(var_count)
        r_count = float(ref_count)
        if r_count > v_count:
            return str(v_count / r_count)
        else:
            return str(r_count / v_count)

    def create_input_tsv(self, sample, temp_dir):
        DirectoryManager.clean_temp_dir()
        input_tsv_name = "ccube_input.tsv"
        input_tsv_path = P.abspath(P.join(temp_dir, input_tsv_name))
        with open(input_tsv_path, "wb+") as tsv_file:
            writer = csv.writer(tsv_file, delimiter='\t')
            writer.writerow(INPUT_TSV_HEADER)

            row_num = 0
            for segment in sample.chromosome_segments:
                for mutation in segment.mutations:
                    row = [
                        "s%s" % row_num,
                        self.mutation_name_to_string(mutation),
                        mutation.ref_count,
                        str(int(mutation.var_count) + int(mutation.ref_count)),
                        "1",
                        segment.major_cn,
                        segment.minor_cn,
                        segment.copy_number,
                        mutation.var_count,
                        self.mutation_name_to_string(mutation),
                        "0",
                        sample.purity
                    ]
                    writer.writerow(row)
                    row_num += 1

        return input_tsv_path

    @staticmethod
    def get_output_dir_from_temp_dir(temp_dir):
        out_dir = P.join(temp_dir, "ccube_res/sample1")
        return P.realpath(out_dir)

    def run_ccube(self, working_dir):
        cmd_string = "Rscript run_ccube.r"
        subprocess.call(cmd_string, shell=True, cwd=working_dir)

        # automatically decompress CCube outputs.
        out_dir = self.get_output_dir_from_temp_dir(working_dir)
        for out_file in os.listdir(out_dir):
            if out_file.endswith(".gz"):
                extracted_path = P.join(out_dir, out_file[0:-3])
                compressed_path = P.join(out_dir, out_file)
                decompress_gzip(compressed_path, extracted_path)
                os.remove(compressed_path)
        return

    @staticmethod
    def get_test_dir(sample_name):
        # test_dir is used in debugging only. It just lets us cache the output somewhere where we can reuse it, instead
        # of rerunning CCube all the time, which is a lengthy process.
        test_dir = P.join(__file__, os.pardir)
        test_dir = P.join(test_dir, os.pardir)
        test_dir = P.join(test_dir, "sample_output/ccube/" + sample_name)
        test_dir = P.realpath(test_dir)
        return test_dir

    def save_output(self, sample_name, working_dir):
        out_dir = self.get_output_dir_from_temp_dir(working_dir)
        sample_test_dir = self.get_test_dir(sample_name)
        if P.exists(sample_test_dir):
            shutil.rmtree(sample_test_dir)
        shutil.copytree(out_dir, sample_test_dir)
        return

    def use_cached_output(self, sample_name, working_dir):
        out_dir = self.get_output_dir_from_temp_dir(working_dir)
        if not P.exists(out_dir):
            os.makedirs(out_dir)
        shutil.rmtree(out_dir)
        sample_test_dir = self.get_test_dir(sample_name)
        shutil.copytree(sample_test_dir, out_dir)
        return

    @staticmethod
    def get_r_script_path():
        r_script_path = P.abspath(__file__)
        r_script_path = P.join(P.abspath(__file__), os.pardir)
        r_script_path = P.join(r_script_path, "run_ccube.r")
        r_script_path = P.realpath(r_script_path)
        return r_script_path

    def get_r_script(self, sample_purity):
        r_script_path = self.get_r_script_path()
        with open(r_script_path, "r") as r_script_file:
            r_script = r_script_file.read()
            r_script = r_script.replace("SAMPLE_PURITY", sample_purity)
            return r_script

    def run_analysis(self, sample):
        temp_dir = DirectoryManager.get_temp_dir()
        input_tsv_path = self.create_input_tsv(sample, temp_dir)

        # copy over R script we will use
        r_script = self.get_r_script(sample.purity)
        with open(P.join(temp_dir, "run_ccube.r"), "w+") as r_script_file:
            r_script_file.write(r_script)

        start = time.time()
        print "CCube Started at %s" % str(start)

        if DEBUG:
            self.use_cached_output(sample.name, temp_dir)
        else:
            self.run_ccube(temp_dir)

        if SAVE_OUTPUTS:
            self.save_output(sample.name, temp_dir)

        self.read_ccube_output(sample, temp_dir)

        end = time.time()
        print "Ended at %s" % str(end)
        print "Elapsed: %s" % str(end - start)

        return

    @staticmethod
    def read_clusters(cluster_defs_path):
        clusters = {}
        highest_cluster_id = 0
        with open(cluster_defs_path, "r") as tsv_file:
            reader = csv.reader(tsv_file, delimiter='\t')
            reader.next()

            for row in reader:
                cluster_id = row[0]
                cluster_ccf = row[2]

                clusters[cluster_id] = cluster_ccf

                if int(cluster_id) > highest_cluster_id:
                    highest_cluster_id = int(cluster_id)

        return highest_cluster_id, clusters

    @staticmethod
    def read_cluster_assignments(cluster_assignments_path, clusters, highest_cluster_id):
        cluster_assignments = {}
        with open(cluster_assignments_path, "r") as tsv_file:
            reader = csv.reader(tsv_file, delimiter='\t')
            reader.next()

            for row in reader:
                chromosome = row[0]
                position = row[1]
                cluster_id = str(row[2])

                # this is a workaround for a bug where cluster assignments are sometimes assigned
                # to a random number instead of the real cluster.
                if cluster_id not in clusters:
                    cluster_id = str(highest_cluster_id)

                mutation_name = "%s_%s" % (chromosome, position)
                cluster_assignments[mutation_name] = cluster_id

        return cluster_assignments

    def read_ccube_output(self, sample, working_dir):
        out_dir = self.get_output_dir_from_temp_dir(working_dir)

        cluster_defs_path = P.join(out_dir, CLUSTERS_FILE_NAME)
        highest_cluster_id, clusters = self.read_clusters(cluster_defs_path)

        cluster_assignments_path = P.join(out_dir, MUTATIONS_ASSIGNMENTS_FILE_NAME)
        cluster_assignments = self.read_cluster_assignments(cluster_assignments_path, clusters, highest_cluster_id)

        for segment in sample.chromosome_segments:
            for mutation in segment.mutations:
                mutation_name = self.mutation_name_to_string(mutation)
                mutation.cellular_prevalence = clusters[cluster_assignments[mutation_name]]

        return
