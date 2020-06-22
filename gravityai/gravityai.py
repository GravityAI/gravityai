import warnings,sys,os
from pathlib import Path

# Source: https://stackoverflow.com/questions/15411967/how-can-i-check-if-code-is-executed-in-the-ipython-notebook/24937408
# Source: https://stackoverflow.com/questions/47211324/check-if-module-is-running-in-jupyter-or-not
# This function checks if you are running the library from jupyter or not
def type_of_script():
    try:
        ipy_str = str(type(get_ipython()))
        if 'zmqshell' in ipy_str:
            return 'jupyter'
        if 'terminal' in ipy_str:
            return 'ipython'
    except:
        return 'terminal'

# Emulate system arguments if not running the library from the terminal
if type_of_script() != 'terminal':
    sys.argv=["programName.py","dataset.csv","output.csv"]
    print("Input file is dataset.csv and output file is output.csv")

warnings.filterwarnings("ignore")
if (len(sys.argv) <= 1):
    sys.stderr.write("No input file specified on command line. Please specify a file.")
    sys.exit(2)

datafile = Path(sys.argv[1])

if (not datafile.is_file()):
    sys.stderr.write("Input file not found. Please create an input file.")
    sys.exit(2)
if (len(sys.argv) <= 2):
    sys.stderr.write("No output file specified on command line. Please specify a file.")
    sys.exit(3)

outfile = Path(sys.argv[2])
    
def getInputFile():
    return str(datafile.resolve()) 
    
def getOutputFile():
    return str(outfile.absolute()) 

# This helper function splits an iterable list into chunks of a constant size (until the last chunk). It is used for batching.
#from: https://stackoverflow.com/questions/8290397/how-to-split-an-iterable-in-constant-size-chunks
def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]
