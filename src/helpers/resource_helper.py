import os
import sys

def resource_path(relative_path):
    """ Get the absolute path to the resource"""
    if hasattr(sys, '_MEIPASS'):
        # If running from a PyInstaller bundle, the resources will be in _MEIPASS
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        # Otherwise, return the relative path for development
        return os.path.join(os.path.abspath("../"), relative_path)