import sys
import subprocess
import os
import csv
import math
import copy
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

P = os.path

# This file contains functions common to all topic modeling classes, to be used for writing their output.


# Write a matrix as a TSV, using given labels
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


# Run write_heatmap.py to convert a TSV file with labels to a heatmap. Note we need to do this to work around a
# bug in matplotlib, where you can only output one heatmap per process. Other heatmaps will be corrupted by data
# from previous heatmaps due to this bug. By running write_heatmap.py, we only write one heatmap per process, thus
# working around the bug.
def run_tsv_to_heatmap(tsv_path, out_file_path, colormap):
    python_exe = sys.executable

    script_path = P.join(__file__, os.pardir)
    script_path = P.abspath(P.join(script_path, "write_heatmap.py"))

    cmd_string = [
        python_exe,
        script_path,
        "-t",
        tsv_path,
        "-o",
        out_file_path,
        "-c",
        colormap
    ]

    subprocess.call(cmd_string, shell=False)
    return


# Write a TSV as a barplot. The TSV should be a specific format describing the exposure of each signature to each band.
def write_tsv_as_barplot(tsv_path, out_file_path):
    f = pd.read_table(tsv_path, sep='\t')
    nmf = np.array(f)
    x = nmf.transpose()
    new_data = pd.DataFrame(data=x[1:, 0:], columns=x[0, 0:])
    fig = new_data.plot(kind='bar', width=2).legend(loc='center left', bbox_to_anchor=(1.0, 0.6)).get_figure()
    fig.subplots_adjust(right=0.8)
    fig.savefig(out_file_path)
    return



