import os
import csv
import copy
import math
import numpy as np
from sklearn.decomposition import NMF
import matplotlib.pyplot as plt
import seaborn as sns

P = os.path


# Class for Non-Negative Matrix Factorization of classified mutation data
class NMFModeler:

    def __init__(self, args):
        self.args = args
        self.W = None
        self.H = None

        self.class_names = []
        self.sample_names = []
        self.num_topics = 0
        self.topic_names = []

    # TODO: Verify args passed to NMF by user
    def verify_args(self):
        return

    def build_topic_names(self):
        self.topic_names = []
        for i in range(1, self.num_topics + 1):
            self.topic_names.append("Topic " + str(i))

    def extract_topics_from_classified_data(self, classifier):
        rows = []
        num_samples = 0
        self.class_names = classifier.get_class_names()
        self.sample_names = classifier.get_sample_names()

        for i in range(0, classifier.NUM_CLASSES):
            class_name = classifier.get_class_name(i)
            row = classifier.get_class_as_row(class_name)
            num_samples = len(row)
            rows.append(row)

        data_matrix = np.array(rows)

        self.num_topics = int(math.floor(math.sqrt(num_samples)))
        if self.num_topics < 2:
            self.num_topics = 2

        model = NMF(n_components=self.num_topics, init='random', random_state=0)
        self.W = model.fit_transform(data_matrix)
        self.H = model.components_

        self.build_topic_names()

        return

    @staticmethod
    def write_matrix_as_tsv(matrix, x_labels, y_labels, out_file_path):

        table = matrix.tolist()
        rows = matrix.shape[0]

        with open(out_file_path, "wb+") as out_file:
            writer = csv.writer(out_file, delimiter='\t')
            header = copy.copy(x_labels)
            header.insert(0, '')
            writer.writerow(header)

            for i in range(0, rows):
                row = table[i]
                row.insert(0, y_labels[i])
                writer.writerow(row)
        return

    #TODO: ValueError: Image size of 125000x2000 pixels is too large. It must be less than 2^16 in each direction.
    @staticmethod
    def write_matrix_as_heatmap(matrix, x_labels, y_labels, out_file_path):
        sns.set(font_scale=2.2)
        sns.set_style({"savefig.dpi": 100})

        figure_width_inches = int(math.floor(len(x_labels) / 2)) * 5
        figure_height_inches = int(math.floor(math.sqrt(len(y_labels)))) * 5

        ax = sns.heatmap(matrix,
                         xticklabels=x_labels,
                         yticklabels=y_labels,
                         annot=True,
                         fmt=".2f",
                         cmap="Reds")
        ax.xaxis.tick_top()

        figure = ax.get_figure()
        figure.set_size_inches(figure_width_inches, figure_height_inches)
        figure.savefig(out_file_path)
        return

    def write_output(self, out_dir_path):

        #plt.ion()
        self.write_matrix_as_tsv(self.W, self.topic_names, self.class_names, P.join(out_dir_path, "nmf_W.tsv"))
        self.write_matrix_as_heatmap(self.W, self.topic_names, self.class_names,
                                     P.join(out_dir_path, "nmf_W_heatmap.png"))

        self.write_matrix_as_tsv(self.H, self.sample_names, self.topic_names, P.join(out_dir_path, "nmf_H.tsv"))
        self.write_matrix_as_heatmap(self.H, self.sample_names, self.topic_names,
                                     P.join(out_dir_path, "nmf_H_heatmap.png"))

        #plt.ioff()

        return
