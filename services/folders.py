import os


def make_filepath(folder_name, filename):
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    filepath = os.path.join(folder_name, filename)
    return filepath
