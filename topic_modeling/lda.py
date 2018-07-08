import os
import csv
import copy
import math
import numpy as np
from sklearn.decomposition import LatentDirichletAllocation
import matplotlib.pyplot as plt
import seaborn as sns

from common import *

P = os.path


# Class for Latent Dirichlet Allocation of classified mutation data
class LDAModeler:

    # Constructor takes dictionary of args, parsed from config file.
    def __init__(self, args):
        self.args = args['lda_params']

        self.class_names = []
        self.sample_names = []
        self.num_topics = 0
        self.topic_names = []

        self.topic_to_class = None
        self.sample_to_topic = None

    # TODO: Verify args passed to LDA by user
    def verify_args(self):
        return

    # Build a list of names of all topics, based on number of topics.
    def build_topic_names(self):
        self.topic_names = []
        for i in range(1, self.num_topics + 1):
            self.topic_names.append("Topic " + str(i))

    # Run topic modeling on classified data, and save the data in this object.
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

        model = LatentDirichletAllocation(n_components=self.num_topics, learning_method='online')
        self.topic_to_class = model.fit_transform(data_matrix)
        self.sample_to_topic = model.components_

        self.build_topic_names()
        return

    # Write output TSVs and charts of LDA topic modeling.
    def write_output(self, out_dir_path):

        sig_to_band_tsv = P.join(out_dir_path, "lda_signature_to_band_exposure.tsv")
        write_matrix_as_tsv(self.topic_to_class, self.topic_names, self.class_names, sig_to_band_tsv)

        sample_to_sig_tsv = P.join(out_dir_path, "lda_sample_to_signature_exposure.tsv")
        write_matrix_as_tsv(self.sample_to_topic, self.sample_names, self.topic_names, sample_to_sig_tsv)

        if 'write_charts' in self.args and self.args['write_charts']:

            print "Writing LDA charts..."

            color_map = "viridis"
            if 'heatmap_colormap' in self.args:
                color_map = self.args['heatmap_colormap']

            run_tsv_to_heatmap(sig_to_band_tsv, P.join(out_dir_path, "lda_signature_to_band_exposure_heatmap.png"), color_map)
            run_tsv_to_heatmap(sample_to_sig_tsv, P.join(out_dir_path, "lda_sample_to_signature_exposure_heatmap.png"), color_map)

            write_tsv_as_barplot(sig_to_band_tsv, P.join(out_dir_path, "lda_signature_to_band_exposure_barplot.png"))

        return
