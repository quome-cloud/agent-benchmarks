from os.path import dirname, basename, isfile, join
import glob

# Dynamically import all modules
modules = glob.glob(join(dirname(__file__), "*.py"))

# Enables from <this_module> import *
# See https://stackoverflow.com/questions/44834/what-does-all-mean-in-python
__all__ = [basename(f)[:-3] for f in modules if isfile(f) and not f.startswith('_')]
