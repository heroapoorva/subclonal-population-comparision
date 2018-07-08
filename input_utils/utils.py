import os
import bz2
import gzip
import zipfile


# Util function to unzip a bz2 archive
def decompress_bz2(src, dest):
    bzfile = bz2.BZ2File(src)
    with open(dest, 'wb') as out_file:
        out_file.write(bzfile.read())


# Util function to unzip a file from a gzip archive
def decompress_gzip(src, dest):
    with gzip.open(src, 'rb') as zip_file:
        with open(dest, 'wb') as outfile:
            outfile.write(zip_file.read())


# Util function to unzip a single file from a zip archive
def unzip_single_file(zip_path, out_file_path, file_name):
    with zipfile.ZipFile(zip_path) as zip_file:
        with open(out_file_path, 'wb') as out_file:
            out_file.write(zip_file.read(file_name))
