import os
import csv
import vcf

from input_utils.ccf_input import CCFInputSample, ChromosomeSegment, MutationData

P = os.path

DATA_DIR = "data"
TRUTH_DIR = "truth"

PP_TABLE_FILENAME = "pp_table.txt"

SEGMENTS_FN_EXT = ".segments.txt"
SEGMENTS_DIR = "Segments"

VCF_EXT = ".vcf"
VCF_DIR = "VCF"

GROUND_TRUTH_MUTATIONS = "Mut_Assign"
GROUND_TRUTH_CLUSTERS = "Subclonal_Structure"
CANCER_TYPES = "cancer_type.txt"

BB_EXT = ".BB_file.txt"
BB_DIR = "BB"


# Class which will read the input data of 500 samples given to us by supervisor.
class RealData500InputReader:

    # Constructor must have a single argument: path to input directory.
    def __init__(self, input_dir):
        self.data_dir = P.join(input_dir, DATA_DIR)
        self.truth_dir = P.join(input_dir, TRUTH_DIR)
        self.sample_purities = {}
        self.ground_truth = {}
        self.cancer_type = {}
        self.loading_cancer_type()
        return

    # This input type has a truth directory which can be used for error analysis
    @staticmethod
    def has_truth_dir():
        return True

    # Find VCF file name based on sample name
    @staticmethod
    def find_vcf_file(vcfs_dir, sample_name):
        for filename in os.listdir(vcfs_dir):
            if filename.startswith(sample_name + ".") and filename.endswith(VCF_EXT):
                return P.abspath(P.join(vcfs_dir, filename))
        raise "Unable to find VCF file for sample %s in directory '%s'" % (sample_name, vcfs_dir)

    # Find VCF file path based on sample name
    def get_vcf_file_path(self, sample_name):
        vcfs_dir = P.join(self.data_dir, VCF_DIR)
        vcf_file_path = self.find_vcf_file(vcfs_dir, sample_name)
        return vcf_file_path

    # Get path to Battenberg file based on sample name.
    def get_bb_file_path(self, sample_name):
        bb_dir = P.join(self.data_dir, BB_DIR)
        bb_file_path = P.join(bb_dir, sample_name + BB_EXT)
        if not P.isfile(bb_file_path):
            raise "Unable to find BB file for sample %s in directory '%s'" % (sample_name, bb_dir)
        return bb_file_path

    # Read all mutation data from VCF of sample.
    def read_vcfs(self, sample):
        vcf_file_path = self.get_vcf_file_path(sample.name)
        with open(vcf_file_path, 'r') as vcf_file:
            vcf_reader = vcf.Reader(vcf_file)
            for record in vcf_reader:
                chromosome = record.CHROM
                position = record.POS
                var_count = record.INFO['t_alt_count']
                ref_count = record.INFO['t_ref_count']
                mut_data = MutationData(chromosome, position, var_count, ref_count)

                # Note: We might be able to make the below code faster by using a dictionary to hold chromosome segments
                segment_found = False
                for segment in sample.chromosome_segments:
                    if segment.chromosome == chromosome and int(segment.start) <= int(position) <= int(segment.end):
                        segment_found = True
                        # Only use mutations which come from a segment with a CCF of "1".
                        if segment.ccf == "1":
                            segment.add_mutation(mut_data)

                if not segment_found:
                    raise "Unable to find a segment for mutation @ CHR %s POS %s for sample %s" \
                          % (chromosome, position, sample.name)

    # Read all chromosome segments of the sample from the chromosome segments TSV file.
    def read_chrom_segments(self, sample):
        segments_dir = P.join(self.data_dir, SEGMENTS_DIR)
        seg_filename = sample.name + SEGMENTS_FN_EXT
        seg_file_path = P.join(segments_dir, seg_filename)
        if not P.isfile(seg_file_path):
            raise "Segment data for %s missing at '%s'" % (sample.name, seg_file_path)

        with open(seg_file_path, 'rb') as seg_file:
            seg_reader = csv.reader(seg_file, delimiter='\t')
            seg_reader.next()

            for row in seg_reader:
                chromosome = row[0]
                start = row[1]
                end = row[2]
                copy_number = row[3]
                minor_cn = row[4]
                major_cn = row[5]
                ccf = row[6]
                chrom_seg = ChromosomeSegment(chromosome=chromosome,
                                              start=start,
                                              end=end,
                                              copy_number=copy_number,
                                              minor_cn=minor_cn,
                                              major_cn=major_cn,
                                              cellular_prevalence=None,
                                              ccf=ccf)
                sample.add_segment(chrom_seg)

        # After supposedly reading chromosome segments, verify that sample has segments
        if len(sample.chromosome_segments) == 0:
            raise "Sample %s has no chromosome segments in '%s' directory!" % (sample.name, SEGMENTS_DIR)

    # Read a sample with given name, and return CCFInputSample object holding sample data.
    def read_sample_data(self, sample_name):
        sample_purity = self.sample_purities[sample_name]
        bb_file_path = self.get_bb_file_path(sample_name)
        vcf_file_path = self.get_vcf_file_path(sample_name)
        sample_object = CCFInputSample(sample_name, sample_purity, bb_file_path, vcf_file_path)

        self.read_chrom_segments(sample_object)
        self.read_vcfs(sample_object)

        return sample_object

    # Get names of all samples in the input directory.
    def get_sample_names(self):
        sample_names = []
        self.sample_purities = {}

        pp_table_path = P.join(self.data_dir, PP_TABLE_FILENAME)
        with open(pp_table_path, "r") as pp_table_file:
            reader = csv.reader(pp_table_file, delimiter='\t')
            reader.next()

            for row in reader:
                sample_name = row[0]
                sample_purity = row[1]
                sample_names.append(row[0])

                self.sample_purities[sample_name] = sample_purity

        return sample_names

    def loading_ground_truth(self, target):
        
        mutations_assignment_path = P.join(self.truth_dir, GROUND_TRUTH_MUTATIONS)
        mutations_assignment_list_path = os.listdir(mutations_assignment_path)
        mutations = []


        clusters_path = P.join(self.truth_dir, GROUND_TRUTH_CLUSTERS)
        clusters_list_path = os.listdir(clusters_path)
        clusters = {}
        
        
        
        for clusters_file in clusters_list_path:
            if "_".join(target.split("_", 3)[:3]) == clusters_file.split(".")[0]:
                with open(P.join(clusters_path, clusters_file), "r") as clu_file:
                    clu_file.next()
                    for line in clu_file:
                        elem = line.split()
                        clusters[elem[0]] = elem[2]
    
        for mutations_file in mutations_assignment_list_path:
            if "_".join(target.split("_", 3)[:3]) == mutations_file.split(".")[0]:
                with open(P.join(mutations_assignment_path, mutations_file), "r") as mut_file:
                    mut_file.next()
                    for line in mut_file:
                        elem = line.split()
                        temp = MutationData(chromosome = elem[0], position = elem[1], var_count = 0, ref_count = 0, cellular_prevalence = clusters[elem[2]])
                        mutations.append(temp)
        
        return mutations


    def loading_cancer_type(self):

        cancer = P.join(self.data_dir, CANCER_TYPES)
        #print(cancer)
        fileResults = open(cancer, "r")
        next(fileResults)
        for line in fileResults:
            self.cancer_type[line.split()[0]] = line.split()[1]





