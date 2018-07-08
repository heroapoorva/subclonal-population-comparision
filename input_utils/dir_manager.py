import os
import shutil

P = os.path


# Static class holding helper functions to clean and get temp and output directories.
class DirectoryManager:

    # Create a temp directory in the current working directory
    temporary_dir = P.abspath(P.join(os.getcwd(), "temp"))
    # This will be overwritten by user input set in config file.
    out_dir = P.abspath(P.join(os.getcwd(), "out"))
    # Intermediates dir is always a directory in output directory
    intermediates_dir = P.join(out_dir, "intermediates")

    # Clean all temp data in temp directory
    @staticmethod
    def clean_all_temp_data():
        if P.isdir(DirectoryManager.temporary_dir):
            shutil.rmtree(DirectoryManager.temporary_dir)

    # Clean a temp directory for an individual sample. These are subdirectories of 'temp'. This is necessary when
    # running multiple CCF analysis in parallel, with each of them in a separate working directory so they don't
    # interfere with one another.
    @staticmethod
    def clean_temp_dir(sample_name=None):
        if sample_name is not None:
            t = P.join(DirectoryManager.temporary_dir, sample_name)
            if P.isdir(t):
                shutil.rmtree(t)
        DirectoryManager.get_temp_dir(sample_name)

    # Get the path to a temp directory for a sample. This directory will be a subdirectory of 'temp'. This is necessary
    # when running multiple CCF analysis in parallel, with each of them in a separate working directory so they don't
    # interfere with one another.
    @staticmethod
    def get_temp_dir(sample_name=None):
        if not P.isdir(DirectoryManager.temporary_dir):
            os.mkdir(DirectoryManager.temporary_dir)
        if sample_name is None:
            return DirectoryManager.temporary_dir
        t = os.path.join(DirectoryManager.temporary_dir, sample_name)
        if not P.isdir(t):
            os.mkdir(t)
        return t

    # Clean the output directory, create it if it doesn't exist.
    @staticmethod
    def reset_out_dir(new_out_dir):
        DirectoryManager.out_dir = new_out_dir
        DirectoryManager.intermediates_dir = P.join(DirectoryManager.out_dir, "intermediates")
        if P.isdir(DirectoryManager.intermediates_dir):
            shutil.rmtree(DirectoryManager.intermediates_dir)
        os.makedirs(DirectoryManager.intermediates_dir)

    # Gets path to intermediates directory.
    @staticmethod
    def get_intermediates_dir():
        return DirectoryManager.intermediates_dir
