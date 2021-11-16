import warnings
import sys
import os
import json
from pathlib import Path
import argparse
import asyncio
import websockets
from datetime import datetime

warnings.filterwarnings("ignore")

# Source: https://stackoverflow.com/questions/15411967/how-can-i-check-if-code-is-executed-in-the-ipython-notebook/24937408
# Source: https://stackoverflow.com/questions/47211324/check-if-module-is-running-in-jupyter-or-not
# This function checks if you are running the library from jupyter or not


def _type_of_script():
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


def _valid_json(myjson):
    try:
        json_object = json.loads(myjson)
        if (not json_object):
            return False
    except ValueError:
        return False
    return True


_datafile = ""
_outfile = ""
_port = None
_is_gai = False
_is_debug = False


def _run_command(args):
    global _datafile
    global _outfile
    _datafile = Path(args.input_path)
    # Validate that input file exists
    if (not _datafile.is_file()):
        sys.stderr.write("Input file not found. Please create an input file.")
        sys.exit(2)

    # Validate that json input file contains valid data format, if the input was json
    if str(_datafile).endswith(".json"):
        with open(str(_datafile), 'r') as file:
            json_text = file.read().replace('\n', '')
            if not _valid_json(json_text):
                sys.stderr.write(
                    "JSON input is not in a valid format. Please check the format of the input file.")
                sys.exit(2)

    # Validate that output file was specified
    if (len(args.output_path) <= 2):
        sys.stderr.write(
            "No output file specified on command line. Please specify a file.")
        sys.exit(2)
    _outfile = Path(args.output_path)


def _serve_command(args):
    global _port
    global _is_gai
    global _is_debug
    _port = args.port
    _is_gai = args.gai
    _is_debug = args.debug

    if (_port is None or _port < 1 or _port > 65535):
        sys.stderr.write(
            "Invalid port number specified. Please select a port number in the range 0-65535")
        sys.exit(2)
    if(not _is_gai):
        print("Serving on port " + str(_port))


if _type_of_script() == 'terminal':

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        title='subcommands', help='commands to choose from', required=True, dest='subcommand')
    parser_run = subparsers.add_parser(
        'run', help='run this model once from the command line')
    parser_run.add_argument("input_path", help='Path to input data file')
    parser_run.add_argument("output_path", help='Path to output result file')
    parser_run.set_defaults(func=_run_command)

    parser_serve = subparsers.add_parser(
        'serve', help='run this model as a websocket service')
    parser_serve.add_argument("-p", '--port',  nargs='?',
                              default=49200, help='tcp port to serve on', type=int)
    parser_serve.add_argument('--gai', action="store_true",
                              help='Enable gravity AI specific status messages and idle timeout')
    parser_serve.add_argument('--debug', action="store_true",
                              help='Enable debugging to log file "gai_debug.log"')
    parser_serve.set_defaults(func=_serve_command)

    if (len(sys.argv) <= 1):
        parser.parse_args(['--help'])
        sys.exit(2)

    args = parser.parse_args()
    args.func(args)


def getInputCSV():
    # Emulate system arguments if not running the library from the terminal
    if _type_of_script() != 'terminal':
        print("Emulating input filename as dataset.csv")
        return "dataset.csv"
    return str(_datafile.resolve())


def getInputJSON():
    # Emulate system arguments if not running the library from the terminal
    if _type_of_script() != 'terminal':
        print("Emulating input filename as data.json")
        return "data.json"
    return str(_datafile.resolve())


def getInputFile():
    return getInputCSV()


def getOutputCSV():
    # Emulate system arguments if not running the library from the terminal
    if _type_of_script() != 'terminal':
        print("Emulating output filename as output.csv")
        return "output.csv"
    return str(_outfile.absolute())


def getOutputJSON():
    # Emulate system arguments if not running the library from the terminal
    if _type_of_script() != 'terminal':
        print("Emulating output filename as output.json")
        return "output.json"
    return str(_outfile.absolute())


def getOutputFile():
    return getOutputCSV()

# This helper function splits an iterable list into chunks of a constant size (until the last chunk). It is used for batching.
# from: https://stackoverflow.com/questions/8290397/how-to-split-an-iterable-in-constant-size-chunks


def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]


def _tryParseJsonRequest(jsonMessage):
    try:
        json_object = json.loads(jsonMessage)
        return True, json_object
    except Exception:
        return False, {}
    return True


_request_handler = None


def _check_request_handler():
    global _request_handler
    if (_request_handler is None):
        return False

    if (not callable(_request_handler) and not asyncio.iscoroutinefunction(_request_handler)):
        return False
    return True


def _print_gravity_message(message):
    global _is_gai
    if _is_gai:
        print("[gravityAI]: " + message, flush=True)
    _print_debug_message(message)


def _print_debug_message(message):
    global _is_debug
    if _is_debug:
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        with open("gai_debug.log", "a") as file_object:
            file_object.write(f"[debug {timestamp}]: {message}\n")


async def _send_error_message(websocket, reqId, message):
    await websocket.send(json.dumps({"status": "error", "error": message, "requestId": reqId}))


async def _send_error_bad_message(websocket, error, message):
    await websocket.send(json.dumps({"status": "error", "error": error, "request": message}))


async def _send_accepted_message(websocket, reqId):
    await websocket.send(json.dumps({"status": "pending", "requestId": reqId}))


async def _send_finished_message(websocket, reqId):
    await websocket.send(json.dumps({"status": "complete", "requestId": reqId}))


def _normalize_path_string(path):
    f = Path(path)
    if (f.is_file()):
        return f.resolve()
    return f.absolute()


async def _on_request(inputFile, outputFile):
    global _request_handler
    if (not _check_request_handler()):
        return False, "Request Handler is not callable"

    try:
        # Validate that input file exists
        inFile = Path(inputFile)
        if (not inFile.is_file()):
            return False, "Input file not found"
        _print_debug_message("Handling Request")
        err = None
        if(asyncio.iscoroutinefunction(_request_handler)):
            err = await _request_handler(str(inputFile), str(outputFile))
        else:
            err = _request_handler(str(_normalize_path_string(
                inputFile)), str(_normalize_path_string(outputFile)))

        if (not err is None and err):
            _print_debug_message(f"Request Error: {err}")
            return False, f"Error returned during processing: {err}"

        _print_debug_message(f"Request Finished")
        outFile = Path(outputFile)

        # Validate that output file exists
        if (not outFile.is_file()):
            return False, "Output file not generated during processing"

    except Exception as e:
        return False, "Exception generated during processing: " + str(e)
    except BaseException as e:
        return False, "Exception generated during processing: " + str(e)
    except:
        return False, "Unknown Exception generated during processing"
    return True, None


def _is_dictionary_string_valid(data, key):
    return (key in data and data[key] and isinstance(data[key], str))


_connections = set()


async def _remove_when_closed(websocket):
    _print_debug_message("Awaiting Close")
    await websocket.wait_closed()
    _print_debug_message("Awaiting Close Complete")
    if(websocket in _connections):
        _connections.remove(websocket)


async def _wsHandler(websocket, path):
    global _connections
    _print_gravity_message("Websocket Connection")
    _connections.add(websocket)
    asyncio.ensure_future(_remove_when_closed(websocket))
    try:
        async for message in websocket:
            isOk, data = _tryParseJsonRequest(message)
            _print_debug_message(f"Message Received: {message}")
            if (not isOk):
                await _send_error_bad_message(websocket, "Invalid Request: Json parse error", message)
                continue

            if (not isinstance(data, dict)):
                await _send_error_bad_message(websocket, "Invalid Request: root json object is not a dictionary", message)
                continue

            if (not _is_dictionary_string_valid(data, 'requestId')):
                await _send_error_bad_message(websocket, "Request does not contain a valid requestId", message)
                continue

            reqId = data['requestId']
            if (not _is_dictionary_string_valid(data, 'inputFile')):
                await _send_error_message(websocket, reqId, "Request does not contain inputFile")
                continue

            if (not _is_dictionary_string_valid(data, 'outputFile')):
                await _send_error_message(websocket, reqId, "Request does not contain outputFile")
                continue

            await _send_accepted_message(websocket, reqId)

            try:
                isOk, error = await _on_request(data['inputFile'], data['outputFile'])
            except:
                await _send_error_message(websocket, reqId, "Unhandle exception during processing")
                continue

            if (not isOk):
                await _send_error_message(websocket, reqId, error)
                continue

            await _send_finished_message(websocket, reqId)
    except Exception as e:
        _print_gravity_message(f"Exception in Websocket: {e}")
    finally:
        _print_gravity_message("Websocket Disconnected")
        if(websocket in _connections):
            _connections.remove(websocket)


async def _idle_timer():
    global _is_gai
    global _connections
    if (not _is_gai):
        return

    idle_count = 0
    _print_gravity_message("Idle Timer: started")
    while(True):
        await asyncio.sleep(5)
        idle_count += 1

        if (_connections):
            count = sum(1 for c in _connections if c.open)
            if (count > 0):
                idle_count = 0
                _print_debug_message(
                    f"Idle Timer: Server has open connections: {count}")
                continue

        _print_debug_message("Idle Timer: tick " + str(idle_count))

        if (idle_count >= 6):  # 30 seconds or so.
            _print_debug_message("Idle Timer: Timeout ")
            sys.stderr.write(
                "Idle Timeout")
            sys.exit(2)


def handle_loop_exception(loop, context):
    # context["message"] will always be there; but context["exception"] may not
    msg = context.get("exception", context["message"])
    _print_gravity_message(f"Unhandled Loop exception: {msg}")
    sys.stderr.write(f"Unhandled Loop Exception: {msg}")
    sys.exit(2)


def wait_for_requests(handler):
    global _request_handler
    global _port
    _request_handler = handler

    if (not _check_request_handler):
        sys.stderr.write(
            "Handler is invalid. Expected a function that accepts two arguments (inputpath, outputPath).")
        sys.exit(2)
        return

    if (not _port is None):
        _print_gravity_message("Starting server")
        loop = asyncio.get_event_loop()
        loop.set_exception_handler(handle_loop_exception)
        try:
            loop.run_until_complete(websockets.serve(
                _wsHandler, '127.0.0.1', _port))
        except Exception as e:
            sys.stderr.write("Failed to start server: " + str(e))
            _print_gravity_message("Bad Port")
            sys.exit(2)

        _print_gravity_message("Running on port " + str(_port))

        loop.run_until_complete(_idle_timer())
        loop.run_forever()

    else:
        isOk, error = asyncio.get_event_loop().run_until_complete(
            _on_request(getInputFile(), getOutputFile()))

        if (not isOk):
            sys.stderr.write(error)
            sys.exit(2)
