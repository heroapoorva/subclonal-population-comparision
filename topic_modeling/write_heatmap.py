import os
import csv
import argparse
import numpy as np
import math
import seaborn as sns


# This file will be run in a separate process from the main pipeline process. It will generate a heatmap image from
# a labeled TSV. This is necessary to run in a separate process to work around a matplotlib/seaborn bug which corrupts
# heatmaps if multiple heatmaps are saved from the same process. Only one heatmap can be saved during the runtime of a
# process, subsequent heatmaps will be corrupted by data from the previous heatmap.
def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-t", "--tsv-file", type=str,
                        help="Full path to TSV file with labeled data that we will make heatmap from", default=None)
    parser.add_argument("-o", "--out-file", type=str,
                        help="Full path to output image file (PNG)", default=None)
    parser.add_argument("-c", "--color-map", type=str,
                        help="Color map to use (default viridis)", default="viridis")

    args = parser.parse_args()

    if args.tsv_file is None or args.out_file is None:
        print "Please specify input and output files"
        return

    color_map = args.color_map

    with open(args.tsv_file, "r") as tsv_file:
        reader = csv.reader(tsv_file, delimiter='\t')
        x_labels = reader.next()
        x_labels.pop(0)

        y_labels = []
        rows = []
        for row in reader:
            lbl = row.pop(0)
            y_labels.append(lbl)
            for i in range(0, len(row)):
                x = float(row[i])
                row[i] = float(row[i])
            rows.append(row)

    matrix = np.array(rows)

    sns.set(font_scale=1.0)
    sns.set_style({"savefig.dpi": 100})

    figure_width_inches = int(math.floor(len(x_labels) / 2)) * 5
    figure_height_inches = int(math.floor(math.sqrt(len(y_labels)))) * 2

    # A fix for: ValueError: Image size of 125000x2000 pixels is too large. It must be less than 2^16 in each direction.
    if figure_width_inches > 360:
        figure_width_inches = 360
        sns.set(font_scale=0.59)

    ax = sns.heatmap(matrix,
                     xticklabels=x_labels,
                     yticklabels=y_labels,
                     annot=True,
                     fmt=".2f",
                     cbar_kws={"orientation": "horizontal"},
                     cmap=color_map)
    ax.xaxis.tick_top()

    figure = ax.get_figure()
    figure.set_size_inches(figure_width_inches, figure_height_inches)
    figure.savefig(args.out_file)

    return


if __name__ == "__main__":
    main()