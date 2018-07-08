import csv


# Data class holding data for each mutation
class MutationData:

    OUT_FILE_EXT = "_mutations.tsv"

    OUT_FILE_TSV_HEADER = [
        "chromosome",
        "position",
        "var_count",
        "ref_count",
        "cellular_prevalence"
    ]

    def __init__(self, chromosome, position, var_count, ref_count, cellular_prevalence=None):
        self.chromosome = chromosome
        self.position = position
        self.var_count = var_count
        self.ref_count = ref_count
        self.cellular_prevalence = cellular_prevalence or 0.0

    # Save mutation from CCFInputSample to a file
    @staticmethod
    def save_mutation_data(sample, out_file_path):
        with open(out_file_path, "wb+") as out_file:
            writer = csv.writer(out_file, delimiter='\t')
            writer.writerow(MutationData.OUT_FILE_TSV_HEADER)

            for segment in sample.chromosome_segments:
                for mutation in segment.mutations:
                    row = [
                        mutation.chromosome,
                        mutation.position,
                        mutation.var_count,
                        mutation.ref_count,
                        mutation.cellular_prevalence
                    ]
                    writer.writerow(row)
        return

    # Load a list of mutations from an intermediate data file.
    @staticmethod
    def load_mutation_data(in_file_path):
        mutations = []
        with open(in_file_path, "r") as in_file:
            reader = csv.reader(in_file, delimiter='\t')
            reader.next()

            for row in reader:
                chromosome = row[0]
                position = row[1]
                var_count = row[2]
                ref_count = row[3]
                cellular_prevalence = row[4]
                mutation = MutationData(chromosome, position, var_count, ref_count, cellular_prevalence)
                mutations.append(mutation)

        return mutations


# Describes the Chromosome Segments of an input sample. Each segment holds a list of mutations that belong in that
# mutation
class ChromosomeSegment:

    def __init__(self, chromosome, start, end, copy_number, minor_cn, major_cn, cellular_prevalence, ccf):
        self.chromosome = chromosome
        self.start = start
        self.end = end
        self.copy_number = copy_number
        self.minor_cn = minor_cn
        self.major_cn = major_cn
        self.cellular_prevalence = cellular_prevalence
        self.ccf = ccf
        self.mutations = []

    def add_mutation(self, mutation):
        self.mutations.append(mutation)


# Object which will hold all data for each sample, including segment data, mutation data, path to Battenberg file, and
# path to VCF file.
class CCFInputSample:

    def __init__(self, name, purity, bb_file_path, vcf_file_path):
        self.name = name
        self.purity = purity
        self.chromosome_segments = []
        self.bb_file_path = bb_file_path
        self.vcf_file_path = vcf_file_path
        return

    def find_segment_index(self, segment):
        found_index = -1
        for current_index in range(len(self.chromosome_segments) - 1, -1, -1):
            current_segment = self.chromosome_segments[current_index]
            if current_segment.chromosome == segment.chromosome and \
                    current_segment.start == segment.start and \
                    current_segment.end == segment.end:
                found_index = current_index
        return found_index

    # When adding segments, overwrite an existing segment if it has same chromosome #, start, and end. This will work
    # around glitches in the input data where we are given identical segments with different CCF's.
    def add_segment(self, segment):
        idx = self.find_segment_index(segment)
        if idx == -1:
            self.chromosome_segments.append(segment)
        else:
            self.chromosome_segments[idx] = segment
