import os
import sys

# Remove current dir from sys.path so Python doesn't try to import the source dir
sys.path.remove(os.getcwd())

from .spectra import spectra
from.engines import search
