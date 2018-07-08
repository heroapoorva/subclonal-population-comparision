import csv


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


class CCFInputSample:

    def __init__(self, name, purity):
        self.name = name
        self.purity = purity
        self.chromosome_segments = []
        return

    def add_segment(self, segment):
        self.chromosome_segments.append(segment)
