import bz2
import gzip


def decompress_bz2(src, dest):
    zipfile = bz2.BZ2File(src)
    data = zipfile.read()
    open(dest, 'wb').write(data)


def decompress_gzip(src, dest):
    with gzip.open(src, 'rb') as zipfile:
        with open(dest, 'wb') as outfile:
            outfile.write(zipfile.read())