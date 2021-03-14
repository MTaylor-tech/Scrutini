"""Scrutini Main."""
import argparse
import json
import os
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
parser.add_argument("-db", "--database", help="Use the specified database.")
# read arguments from the command line
args = parser.parse_args()
# check for Verbose
VERBOSE = bool(args.verbose)
# check for --interface0 or -i0
if args.interface0:
    INTERFACE = 0
    # import scruinterface0 as scruinterface
    if VERBOSE:
        print("Command-Line Interface (0)")
else:
    INTERFACE = 1
    import gui
    if VERBOSE:
        print("GUI (1)")
# check settings and database
if args.settings and os.path.exists(args.settings):
    SETTINGS_FILE = args.settings
else:
    SETTINGS_FILE = 'config.json'

if __name__ == "__main__":
    appctxt = ApplicationContext()
    import sys
    settings = Settings(SETTINGS_FILE, VERBOSE)
    if args.database and os.path.exists(args.database):
        settings.db_file = args.database
    if VERBOSE:
        print(settings)
    scrudb = SCDatabase(settings)
    if INTERFACE == 0:
        print("Command Line Interface not available in this version.")
        # scruinterface.print_settings()
        # scruinterface.menu_main()
    else:
        # import pdb
        # pdb.set_trace()
        g = gui.App(scrudb)
        g.start()
    rc = appctxt.app.exec_()
    # del appctxt.app
    settings.write()
    if VERBOSE:
        print(f"Exit main {rc}")
    sys.exit(rc)
