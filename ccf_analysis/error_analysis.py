import os
import csv
import pickle
import numpy as np
import matplotlib.pyplot as plt
import hashlib
import matplotlib
from matplotlib.font_manager import FontProperties
from classifiers.bin10_classifier import Bin10Classifier
import time
import sys


from input_utils.ccf_input import MutationData

P = os.path


class ErrorAnalysis:

    def __init__(self):
        return

    @staticmethod
    def run_error_analysis(intermediates_dir, input_reader, out_dir):
        error = ComputingErrors(intermediates_dir, input_reader, out_dir)
        ComputingErrors.boxplot_classes(error.bins_errors, out_dir, error.name)

        return

    # inputs should be instances of ComputingErrors class
    @staticmethod
    def compare_all_ccfs(ccube, pyclone, phylowgs, out_dir):
        plt.clf()
        cc_errors = [x[0] for x in ccube.errors.values()]
        pyc_errors = [x[0] for x in pyclone.errors.values()]
        phw_errors = [x[0] for x in phylowgs.errors.values()]
        plt.boxplot([cc_errors, pyc_errors, phw_errors], 0, 'gD')
        my_xticks = ['Ccube', 'Pyclone', 'Phylowgs']
        plt.xticks([1, 2, 3], my_xticks)
        plt.xlabel('CCF Algorithms')
        plt.ylabel('Error')
        plt.title("Final comparison between CCFs analysis")
        plt.savefig(P.join(out_dir, "Final comparison between CCFs analysis"))


class ComputingErrors:

    def __init__(self, intermediates_dir, input_reader, out_dir):
        
        self.errors = {}
        self.intermediates_dir = intermediates_dir
        self.input_reader = input_reader
        self.out_dir = out_dir
        self.bins_errors = []
        for i in range(10):
            self.bins_errors.append([])

        try:
            self.name = intermediates_dir.rsplit('/', 1)[1].split("_")[0]
            if len(self.name) < 2:
                self.name = "ccf"
        except:
            self.name = "ccf"
        
        self.compute_ccube_error()
        self.scatter_plot_cancer_types()
        
        return

    def compute_ccube_error(self):

        print("Computing {0} error...".format(self.name))
        toolbar_width = len(os.listdir(self.intermediates_dir))/10
        sys.stdout.write("[%s]" % (" " * toolbar_width))
        sys.stdout.flush()
        sys.stdout.write("\b" * (toolbar_width+1))
        counter = 1

        for mutations_file in os.listdir(self.intermediates_dir):
            ground_truth_mutations = self.input_reader.loading_ground_truth(mutations_file)
            mutations = MutationData.load_mutation_data(P.join(self.intermediates_dir, mutations_file))
            error = []

            mutations_dict = {}
            for mutation in mutations:
                mutation_name = "%s_%s" % (str(mutation.chromosome), str(mutation.position))
                mutations_dict[mutation_name] = mutation

            for ground_truth_mutation in ground_truth_mutations:
                mutation_name = "%s_%s" % (str(ground_truth_mutation.chromosome), str(ground_truth_mutation.position))

                if mutation_name in mutations_dict:
                    mutation = mutations_dict[mutation_name]

                    temp_error = float(ground_truth_mutation.cellular_prevalence) - float(mutation.cellular_prevalence)
                    temp_error = np.power(temp_error, 2)
                    error.append(temp_error)
                    self.bins_errors[Bin10Classifier.classify_errors(mutation.cellular_prevalence)].append(temp_error)

            self.errors["_".join(mutations_file.split("_", 3)[:3])] = [np.sqrt(sum(error)/len(ground_truth_mutations)), np.std(error)]
            if counter == 10:
                sys.stdout.write("-")
                sys.stdout.flush()
                counter = 1
            else:
                counter = counter + 1

        sys.stdout.write("\n")

        return

    @staticmethod
    def boxplot_classes(bins_errors, out_dir, name):
        plt.clf()
        plt.boxplot(bins_errors, 'gD')
        plt.xlabel('Classes')
        plt.ylabel('Mean Error')
        plt.title("{0} 10 bins error".format(name))
        plt.savefig(P.join(out_dir, "{0} 10 bins error".format(name)))




    def scatter_plot_cancer_types(self):
        plt.clf()
        clustered_data = {}
        
        for file_name in self.input_reader.cancer_type.keys():
            cancer_name = self.input_reader.cancer_type[file_name]
            if cancer_name in clustered_data.keys():
                clustered_data[cancer_name][0].append(self.errors[file_name][0])
                clustered_data[cancer_name][1].append(self.errors[file_name][1])
            else:
                clustered_data[cancer_name] = [[self.errors[file_name][0]], [self.errors[file_name][1]]]
          
        colors = matplotlib.cm.rainbow(np.linspace(0, 1, len(clustered_data.keys())))
        
        fig = plt.figure(figsize=(10, 6))
        ax = plt.subplot(111)
        for dat, color in zip(clustered_data.keys(), colors):
            ax.scatter(clustered_data[dat][0], clustered_data[dat][1], label=dat, c=color)


        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), prop={'size': 8}, ncol=1)
        plt.xlabel('Mean Error', fontsize=18)
        plt.ylabel('Standard Deviation', fontsize=16)
        plt.title("{0} scatter plot".format(self.name))

        fig.savefig(P.join(self.out_dir, "{0} scatter plot".format(self.name)))







