import os
import csv
import vcf

from input_utils.ccf_input import CCFInputSample, ChromosomeSegment, MutationData

P = os.path

PP_TABLE_FILENAME = "pp_table.txt"

SEGMENTS_FN_EXT = ".segments.txt"
SEGMENTS_DIR = "Segments"

VCF_EXT = ".vcf"
VCF_DIR = "VCF"


class RealData500InputReader:

    def __init__(self, input_dir):
        self.input_dir = input_dir
        self.sample_purities = {}
        return

    @staticmethod
    def find_vcf_file(vcfs_dir, sample_name):
        for filename in os.listdir(vcfs_dir):
            if filename.startswith(sample_name + ".") and filename.endswith(VCF_EXT):
                return P.abspath(P.join(vcfs_dir, filename))
        raise "Unable to find VCF file for sample %s in directory '%s'" % (sample_name, vcfs_dir)

    def read_vcfs(self, sample):
        vcfs_dir = P.join(self.input_dir, VCF_DIR)
        vcf_file_path = self.find_vcf_file(vcfs_dir, sample.name)
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
                        segment.add_mutation(mut_data)

                if not segment_found:
                    raise "Unable to find a segment for mutation @ CHR %s POS %s for sample %s" \
                          % (chromosome, position, sample.name)

    def read_chrom_segments(self, sample):
        segments_dir = P.join(self.input_dir, SEGMENTS_DIR)
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

    def read_sample_data(self, sample_name):
        sample_purity = self.sample_purities[sample_name]
        sample_object = CCFInputSample(sample_name, sample_purity)

        self.read_chrom_segments(sample_object)
        self.read_vcfs(sample_object)

        return sample_object

    def get_sample_names(self):
        sample_names = []
        self.sample_purities = {}

        pp_table_path = P.join(self.input_dir, PP_TABLE_FILENAME)
        with open(pp_table_path, "r") as pp_table_file:
            reader = csv.reader(pp_table_file, delimiter='\t')
            reader.next()

            for row in reader:
                sample_name = row[0]
                sample_purity = row[1]
                sample_names.append(row[0])

                self.sample_purities[sample_name] = sample_purity

        return sample_names
