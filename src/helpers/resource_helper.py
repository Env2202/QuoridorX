import os
import sys

def resource_path(relative_path):
    """ Get the absolute path to the resource"""
    if hasattr(sys, '_MEIPASS'):
        # If running from a PyInstaller bundle, the resources will be in _MEIPASS
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        # Otherwise, return the relative path for development
        # Get the directory of the current file (src/helpers)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.join(base_dir, relative_path)