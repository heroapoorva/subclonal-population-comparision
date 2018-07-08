import os
import csv

from input_utils.ccf_input import MutationData

P = os.path


class Bin10Classifier:

    NUM_CLASSES = 10

    def __init__(self, args):
        self.args = args
        self.verify_args()

        self.class_names = []
        for i in range(0, self.NUM_CLASSES):
            self.class_names.append("Class" + str(i))

        self.sample_names = []
        self.all_classifications = {}

        return

    # TODO: Write code to verify args passed to this classifier written by user
    def verify_args(self):
        return

    def init_sample_dict(self, sample_name):
        self.sample_names.append(sample_name)

        sample_classifications = {}
        for class_name in self.class_names:
            sample_classifications[class_name] = 0

        self.all_classifications[sample_name] = sample_classifications
        return

    def classify_mutation(self, sample_name, str_cellular_prevalence):

        cellular_prevalence = float(str_cellular_prevalence)

        # If we haven't seen this sample before, initialize a dict to hold the classified mutations
        if sample_name not in self.all_classifications:
            self.init_sample_dict(sample_name)

        class_num = -1
        step = float(1.0) / float(self.NUM_CLASSES)
        f_lo = float(0)
        for i in range(0, self.NUM_CLASSES):
            f_hi = f_lo + step
            if f_lo <= cellular_prevalence < f_hi:
                class_num = i
                break
            f_lo += step

        if class_num == -1:
            raise "Error, was unable to classify cellular prevalence of (%s) in sample '%s'" \
                  % (str(cellular_prevalence), sample_name)

        class_name = "Class" + str(i)
        self.all_classifications[sample_name][class_name] += 1
        return

    @staticmethod
    def sample_name_from_mutfile_name(mutations_file_name):
        return mutations_file_name.replace(MutationData.OUT_FILE_EXT, "")

    def classify_all_mutation_files(self, mutation_files_dir):
        for mutations_file in os.listdir(mutation_files_dir):
            mutations = MutationData.load_mutation_data(P.join(mutation_files_dir, mutations_file))
            sample_name = self.sample_name_from_mutfile_name(mutations_file)

            for mutation in mutations:
                self.classify_mutation(sample_name, mutation.cellular_prevalence)

    def get_sample_names(self):
        return self.sample_names

    def get_class_names(self):
        return self.class_names

    def get_class_name(self, i):
        return self.class_names[i]

    def get_class_as_row(self, class_name):
        row = []
        for sample_name in self.sample_names:
            row.append(self.all_classifications[sample_name][class_name])
        return row

    def write_classified_data_tsv(self, out_file_path):
        with open(out_file_path, "wb+") as out_file:
            writer = csv.writer(out_file, delimiter='\t')
            header = ['']
            for sample_name in self.sample_names:
                header.append(sample_name)
            writer.writerow(header)

            for i in range(0, self.NUM_CLASSES):
                class_name = self.get_class_name(i)
                row = self.get_class_as_row(class_name)
                row.insert(0, class_name)
                writer.writerow(row)