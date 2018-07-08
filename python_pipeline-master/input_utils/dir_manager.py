import os
import shutil

P = os.path


class DirectoryManager:

    temporary_dir = P.abspath(P.join(os.getcwd(), "temp"))
    out_dir = P.abspath(P.join(os.getcwd(), "out"))
    intermediates_dir = P.join(out_dir, "intermediates")

    @staticmethod
    def clean_temp_dir():
        if P.isdir(DirectoryManager.temporary_dir):
            shutil.rmtree(DirectoryManager.temporary_dir)
        DirectoryManager.get_temp_dir()

    @staticmethod
    def get_temp_dir():
        if not P.isdir(DirectoryManager.temporary_dir):
            os.mkdir(DirectoryManager.temporary_dir)
        return DirectoryManager.temporary_dir

    @staticmethod
    def reset_out_dir(new_out_dir):
        DirectoryManager.out_dir = new_out_dir
        DirectoryManager.intermediates_dir = P.join(DirectoryManager.out_dir, "intermediates")
        if P.isdir(DirectoryManager.intermediates_dir):
            shutil.rmtree(DirectoryManager.intermediates_dir)
        os.makedirs(DirectoryManager.intermediates_dir)

    @staticmethod
    def get_intermediates_dir():
        return DirectoryManager.intermediates_dir
