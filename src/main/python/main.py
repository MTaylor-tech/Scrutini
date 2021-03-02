"""Scrutini Main."""
import argparse
import json
from db import SCDatabase
from classes import Settings
from fbs_runtime.application_context.PyQt5 import ApplicationContext

# initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-i0", "--interface0",
                    help="Use command-line interface (0)", action="store_true")
parser.add_argument("-i1", "--interface1",
                    help="Use Graphical User Interface (1)",
                    action="store_true")
parser.add_argument("-v", "--verbose", help="Prints extra information to the\
                     command line", action="store_true")
parser.add_argument("-s", "--settings", help="Use the specified config file.")
# read arguments from the command line
args = parser.parse_args()
# check for --interface0 or -i0
if args.interface0:
    INTERFACE = 0
    import scruinterface0 as scruinterface
    print("Command-Line Interface (0)")
else:
    INTERFACE = 1
    import gui
    print("GUI (1)")
# check for Verbose
VERBOSE = bool(args.verbose)
# check settings and database
if args.settings:
    SETTINGS_FILE = args.settings
else:
    SETTINGS_FILE = 'config.json'

if __name__ == "__main__":
    appctxt = ApplicationContext()
    import sys
    with open(SETTINGS_FILE) as f:
        s = json.load(f)
    SETTINGS = Settings(s['name'], s['version'], s['schema'], s['schema_file'],
                        s['db_file'], s['interface'], s['last_comp'],
                        s['placings_order'])

    APP_VERSION = 0.2
    SCHEMA_VERSION = 0.2
    scrudb = SCDatabase(SETTINGS)
    # scrudb.check()
    if INTERFACE == 0:
        scruinterface.print_settings()
        scruinterface.menu_main()
    else:
        g = gui.Interface(scrudb)
        g.start()
    rc = appctxt.app.exec_()
    # del appctxt.app
    if VERBOSE:
        print(f"Exit main {rc}")
    sys.exit(rc)
