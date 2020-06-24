import warnings,sys,os
import json
from pathlib import Path

warnings.filterwarnings("ignore")

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

# Source: https://stackoverflow.com/questions/5508509/how-do-i-check-if-a-string-is-valid-json-in-python 
def valid_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError as e:
        return False
    return True

datafile=""
outfile=""
if type_of_script() == 'terminal':
    # Validate that input file was specified
    if (len(sys.argv) <= 1):
        sys.stderr.write("No input file specified on command line. Please specify a file.")
        sys.exit(2)
    datafile = Path(sys.argv[1])
    
    # Validate that input file exists 
    if (not datafile.is_file()):
        sys.stderr.write("Input file not found. Please create an input file.")
        sys.exit(2)
    
    # Validate that json input file contains valid data format, if the input was json
    if str(datafile).endswith(".json"):
        with open(str(datafile), 'r') as file:
            json_text = file.read().replace('\n', '')
            if not valid_json(json_text):
                sys.stderr.write("JSON input is not in a valid format. Please check the format of the input file.")
                sys.exit(2)
        
    # Validate that output file was specified
    if (len(sys.argv) <= 2):
        sys.stderr.write("No output file specified on command line. Please specify a file.")
        sys.exit(3)
    outfile = Path(sys.argv[2])

def getInputCSV():
    # Emulate system arguments if not running the library from the terminal
    if type_of_script() != 'terminal':
        print("Emulating input filename as dataset.csv")
        return "dataset.csv"
    return str(datafile.resolve()) 

def getInputJSON():
    # Emulate system arguments if not running the library from the terminal
    if type_of_script() != 'terminal':
        print("Emulating input filename as data.json")
        return "data.json"
    return str(datafile.resolve()) 

def getInputFile():
    return getInputCSV()

def getOutputCSV():
    # Emulate system arguments if not running the library from the terminal
    if type_of_script() != 'terminal':
        print("Emulating output filename as output.csv")
        return "output.csv"
    return str(outfile.absolute()) 

def getOutputJSON():
    # Emulate system arguments if not running the library from the terminal
    if type_of_script() != 'terminal':
        print("Emulating output filename as output.json")
        return "output.json"
    return str(outfile.absolute()) 

def getOutputFile():
    return getOutputCSV()

# This helper function splits an iterable list into chunks of a constant size (until the last chunk). It is used for batching.
#from: https://stackoverflow.com/questions/8290397/how-to-split-an-iterable-in-constant-size-chunks
def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]
