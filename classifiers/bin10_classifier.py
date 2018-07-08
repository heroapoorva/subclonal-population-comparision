import os
import csv
import pickle

from input_utils.ccf_input import MutationData

P = os.path


# A simple classifier with sorts mutations into 10 bins given their CCF.
class Bin10Classifier:

    # By default have bins. Number of bins can be changed in pipeline_config.yml
    NUM_CLASSES = 10

    def __init__(self, args):
        self.args = args['classifier_params']
        self.verify_args()

        if 'num_classes' in self.args:
            self.NUM_CLASSES = self.args['num_classes']

        self.class_names = []
        for i in range(0, self.NUM_CLASSES):
            self.class_names.append("Class" + str(i))

        self.sample_names = []
        self.all_classifications = {}
        self.all_classifications_for_error_analysis = None

        return

    # TODO: Write code to verify args passed to this classifier written by user
    def verify_args(self):
        return

    # Have a dict for each sample keeping track of its bins.
    def init_sample_dict(self, sample_name):
        self.sample_names.append(sample_name)

        sample_classifications = {}
        for class_name in self.class_names:
            sample_classifications[class_name] = 0

        self.all_classifications[sample_name] = sample_classifications
        return
            
    def init_classes_for_error(self):

        sample_classifications = {}
        for class_name in self.class_names:
            sample_classifications[class_name] = []

        self.all_classifications_for_error_analysis = sample_classifications

    # Sort a mutation into a bin according to its CCF.
    def classify_mutation(self, sample_name, str_cellular_prevalence):

        # If we haven't seen this sample before, initialize a dict to hold the classified mutations
        if sample_name not in self.all_classifications:
            self.init_sample_dict(sample_name)

        class_name = "Class" + str(Bin10Classifier.classify_errors(str_cellular_prevalence))
        self.all_classifications[sample_name][class_name] += 1

        return

    @staticmethod
    def classify_errors(str_cellular_prevalence):
        cellular_prevalence = abs(float(str_cellular_prevalence))
        
        class_num = -1
        step = float(1.0) / float(Bin10Classifier.NUM_CLASSES)
        f_lo = float(0)
        for i in range(0, Bin10Classifier.NUM_CLASSES):
            f_hi = f_lo + step
            if f_lo <= cellular_prevalence < f_hi:
                class_num = i
                break
            f_lo += step
        
        if class_num == -1:
            raise "Error, was unable to classify cellular prevalence of (%s) for error analysis" \
                % (str(cellular_prevalence))
    
        return i

    # Derive sample name from mutation file name.
    @staticmethod
    def sample_name_from_mutfile_name(mutations_file_name):
        return mutations_file_name.replace(MutationData.OUT_FILE_EXT, "")

    # Classify all mutations in a directory of intermediate outputs from CCF analysis. Sample names can be derived
    # from file names.
    def classify_all_mutation_files(self, mutation_files_dir):
        self.init_classes_for_error()
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

    # Get a row of the output TSV, which will contain all counts for a bin across all samples.
    def get_class_as_row(self, class_name):
        row = []
        for sample_name in self.sample_names:
            row.append(self.all_classifications[sample_name][class_name])
        return row

    # Write out a TSV holding the classified data.
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

    # Read classified data from a TSV
    def read_classified_data_tsv(self, in_file_path):
        with open(in_file_path, "r") as in_file:
            reader = csv.reader(in_file, delimiter='\t')

            row_of_sample_names = reader.next()
            row_of_sample_names.pop(0)

            rows = []
            for row in reader:
                rows.append(row)

            sample_index = 0
            for sample_name in row_of_sample_names:
                sample_index += 1
                if sample_name not in self.all_classifications:
                    self.init_sample_dict(sample_name)

                for row in rows:
                    class_name = row[0]
                    class_contents = row[sample_index]
                    self.all_classifications[sample_name][class_name] = int(class_contents)
