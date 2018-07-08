import os
import csv
import vcf

from input_utils.ccf_input import CCFInputSample, ChromosomeSegment, MutationData

P = os.path

SAMPLE_FN_IDENTIFIER = "_purity_ploidy_table.txt"
TRUTH_VALUES_DIR = "Truth_Values"

SEGMENTS_FN_EXT = "_segments.txt"
SEGMENTS_DIR = "Segments"

VCF_EXT = ".vcf"
VCF_DIR = "VCFs"


class SimulationInputReader:

    def __init__(self, input_dir):
        self.input_dir = input_dir
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
                        if segment.cellular_prevalence == sample.purity:
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
                cellular_prevalence = row[6]
                chrom_seg = ChromosomeSegment(chromosome=chromosome,
                                              start=start,
                                              end=end,
                                              copy_number=copy_number,
                                              minor_cn=minor_cn,
                                              major_cn=major_cn,
                                              cellular_prevalence=cellular_prevalence,
                                              ccf=None)
                sample.add_segment(chrom_seg)

        # After supposedly reading chromosome segments, verify that sample has segments
        if len(sample.chromosome_segments) == 0:
            raise "Sample %s has no chromosome segments in '%s' directory!" % (sample.name, SEGMENTS_DIR)

    def read_sample_data(self, sample_name):
        truth_values_dir = P.join(self.input_dir, TRUTH_VALUES_DIR)
        filename = P.join(truth_values_dir, sample_name + SAMPLE_FN_IDENTIFIER)
        if not P.isfile(filename):
            raise "Couldn't find truth values file for sample %s in '%s'" % (sample_name, truth_values_dir)
        with open(filename, 'r') as tv_file:
            tvf_data = tv_file.read()
            lines = tvf_data.split('\n')

            if len(lines) < 2:
                raise "Truth value file '%s' is in unexpected format." % filename
            data_line_split = lines[1].split('\t')
            if len(data_line_split) < 3:
                raise "Truth value file '%s' has unexpected columns." % filename

            sample_name = data_line_split[0]
            sample_purity = data_line_split[1]
            sample_object = CCFInputSample(sample_name, sample_purity)

            self.read_chrom_segments(sample_object)
            self.read_vcfs(sample_object)

            return sample_object

        raise "Unable to find sample data for %s" % sample_name

    def get_sample_names(self):
        sample_names = []

        truth_values_dir = P.join(self.input_dir, TRUTH_VALUES_DIR)
        for filename in os.listdir(truth_values_dir):
            if filename.find(SAMPLE_FN_IDENTIFIER) != -1:
                with open(P.join(truth_values_dir, filename), 'r') as tv_file:
                    tvf_data = tv_file.read()
                    lines = tvf_data.split('\n')

                    if len(lines) < 2:
                        raise "Truth value file '%s' is in unexpected format." % filename
                    data_line_split = lines[1].split('\t')
                    if len(data_line_split) < 3:
                        raise "Truth value file '%s' has unexpected columns." % filename

                    sample_name = data_line_split[0]
                    sample_names.append(sample_name)
        return sample_names
