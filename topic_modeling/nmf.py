import os
import csv
import copy
import math
import numpy as np
from sklearn.decomposition import NMF
import matplotlib.pyplot as plt
import seaborn as sns

from common import *

P = os.path


# Class for Non-Negative Matrix Factorization of classified mutation data
class NMFModeler:

    # Constructor take a single argument, a dictionary of arguments parsed from config file.
    def __init__(self, args):
        self.args = args['nmf_params']
        self.W = None
        self.H = None

        self.class_names = []
        self.sample_names = []
        self.num_topics = 0
        self.topic_names = []

    # TODO: Verify args passed to NMF by user
    def verify_args(self):
        return

    # Build a list of topic names from number of topics.
    def build_topic_names(self):
        self.topic_names = []
        for i in range(1, self.num_topics + 1):
            self.topic_names.append("Topic " + str(i))

    # Run NMF to extract topics from classified data.
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

        if "num_topics" in self.args:
            self.num_topics = self.args['num_topics']
        else:
            self.num_topics = int(math.floor(math.sqrt(num_samples)))

        if self.num_topics < 2:
            self.num_topics = 2

        model = NMF(n_components=self.num_topics, init='random', random_state=0)
        self.W = model.fit_transform(data_matrix)
        self.H = model.components_

        self.build_topic_names()

        return

    # Write output TSVs, barplot, and heatmaps of NMF classified data.
    def write_output(self, out_dir_path):

        w_tsv_path = P.join(out_dir_path, "nmf_W.tsv")
        h_tsv_path = P.join(out_dir_path, "nmf_H.tsv")

        write_matrix_as_tsv(self.W, self.topic_names, self.class_names, w_tsv_path)
        write_matrix_as_tsv(self.H, self.sample_names, self.topic_names, h_tsv_path)

        if 'write_charts' in self.args and self.args['write_charts']:

            print "Writing NMF charts..."

            color_map = "viridis"
            if 'heatmap_colormap' in self.args:
                color_map = self.args['heatmap_colormap']

            write_tsv_as_barplot(w_tsv_path, P.join(out_dir_path, "nmf_W_barplot.png"))

            run_tsv_to_heatmap(w_tsv_path, P.join(out_dir_path, "nmf_W_heatmap.png"), color_map)
            run_tsv_to_heatmap(h_tsv_path, P.join(out_dir_path, "nmf_H_heatmap.png"), color_map)

        return
