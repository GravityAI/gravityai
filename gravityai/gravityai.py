import warnings
import sys
import os
import json
from pathlib import Path
import asyncio
import websockets

warnings.filterwarnings("ignore")

# Source: https://stackoverflow.com/questions/15411967/how-can-i-check-if-code-is-executed-in-the-ipython-notebook/24937408
# Source: https://stackoverflow.com/questions/47211324/check-if-module-is-running-in-jupyter-or-not
# This function checks if you are running the library from jupyter or not


def type_of_script():
    try:
        # pylint: disable=undefined-variable
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
        if (not json_object):
            return False
    except ValueError:
        return False
    return True


datafile = ""
outfile = ""
if type_of_script() == 'terminal':
    # Validate that input file was specified
    if (len(sys.argv) <= 1):
        sys.stderr.write(
            "No input file specified on command line. Please specify a file.")
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
                sys.stderr.write(
                    "JSON input is not in a valid format. Please check the format of the input file.")
                sys.exit(2)

    # Validate that output file was specified
    if (len(sys.argv) <= 2):
        sys.stderr.write(
            "No output file specified on command line. Please specify a file.")
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
# from: https://stackoverflow.com/questions/8290397/how-to-split-an-iterable-in-constant-size-chunks


def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]


def tryParseJsonRequest(jsonMessage):
    try:
        json_object = json.loads(jsonMessage)
        return True, json_object
    except ValueError:
        return False, {}
    return True


request_handler = None


def register_request_handler(handler):
    global request_handler
    request_handler = handler


async def on_request(websocket, data):
    global request_handler
    if (request_handler is None):
        websocket.send(json.dumps(
            {"error": "Inference Handler is not set", "requestId": data.requestId}))
        return

    if (not callable(request_handler)):
        websocket.send(json.dumps(
            {"error": "Inference Handler is not callable", "requestId": data.requestId}))
        return

    try:
        err = request_handler(data.inputFile, data.outputFile)
        if (not err is None and err):
            websocket.send(json.dumps(
                {"error": "error returned during processing", "requestId": data.requestId, "errorData": err}))
            return

        datafile = Path(data.outputFile)

        # Validate that output file exists
        if (not datafile.is_file()):
            websocket.send(json.dumps(
                {"error": "Output file not generated during processing", "requestId": data.requestId, "errorData": data.outputFile}))

    except ValueError as e:
        websocket.send(json.dumps(
            {"error": "Exception generated during processing", "requestId": data.requestId, "errorData": e}))

    return


async def wsHandler(websocket, path):
    async for message in websocket:
        isOk, data = tryParseJsonRequest(message)
        if (not isOk):
            websocket.send(json.dumps(
                {"error": "Invalid Request", "errorData": message}))
            continue
        if (not hasattr(data, "requestId") or not isinstance(data.requestId, str) or not data.requestId):
            websocket.send(json.dumps(
                {"error": "Request does not contain requestId", "errorData": message}))
            continue
        if (not hasattr(data, "inputFile") or not isinstance(data.inputFile, str) or not data.inputFile):
            websocket.send(json.dumps(
                {"error": "Request does not contain inputFile", "requestId": data.requestId, "errorData": message}))
            continue
        if (not hasattr(data, "outputFile") or not isinstance(data.outputFile, str) or not data.outputFile):
            websocket.send(json.dumps(
                {"error": "Request does not contain outputFile", "requestId": data.requestId, "errorData": message}))
            continue
        datafile = Path(data.inputFile)

        # Validate that input file exists
        if (not datafile.is_file()):
            websocket.send(json.dumps(
                {"error": "Input file not found", "requestId": data.requestId, "errorData": data.inputFile}))
            continue

        await on_request(websocket, data)


def wait_for_requests():
    global request_handler
    if (request_handler is None):
        sys.stderr.write(
            "Request handler has not been registered.  Please call register_request_handler with a function that accepts two arguments (inputpath, outputPath).")
        sys.exit(2)
        return

    if (not callable(request_handler)):
        sys.stderr.write(
            "Request handler has been registered, but is not callable.  Please call register_request_handler with a function that accepts two arguments (inputpath, outputPath).")
        sys.exit(2)
        return
    asyncio.get_event_loop().run_until_complete(
        websockets.serve(wsHandler, 'localhost', 4500))
    asyncio.get_event_loop().run_forever()
