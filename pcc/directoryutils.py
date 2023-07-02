import os

class DirectoryUtils:

    # The directory that you cloned the pcc repo into. E.g. "/home/<USER>/pcc".
    root_dir = None

    def __init__(self):
        self.root_dir = os.path.abspath(os.path.dirname(__file__) + '/..')
