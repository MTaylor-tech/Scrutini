"""Scrutini Main."""
import argparse
import os
import sys
import gui
from db import SCDatabase
from classes import Settings
from fbs_runtime.application_context.PyQt5 import ApplicationContext


class AppContext(ApplicationContext):
    def run(self, db):
        window = gui.SMainWindow(self, db)
        # version = self.build_settings['version']
        window.show()
        return self.app.exec_()

# initiate the parser
parser = argparse.ArgumentParser()
# parser.add_argument("-i0", "--interface0",
#                     help="Use command-line interface (0)", action="store_true")
# parser.add_argument("-i1", "--interface1",
#                     help="Use Graphical User Interface (1)",
#                     action="store_true")
parser.add_argument("-v", "--verbose", help="Prints extra information to the\
                     command line", action="store_true")
parser.add_argument("-s", "--settings", help="Use the specified config file.")
parser.add_argument("-db", "--database", help="Use the specified database.")
parser.add_argument("-o", "--open", help="Open the chosen Competition file.")
# read arguments from the command line
args = parser.parse_args()
# check for Verbose
VERBOSE = bool(args.verbose)
# check for --interface0 or -i0
# if args.interface0:
#     INTERFACE = 0
#     # import scruinterface0 as scruinterface
#     if VERBOSE:
#         print("Command-Line Interface (0)")
# else:
#     INTERFACE = 1
#     import gui
#     if VERBOSE:
#         print("GUI (1)")
# check settings and database
if args.settings and os.path.exists(args.settings):
    SETTINGS_FILE = args.settings
else:
    SETTINGS_FILE = 'config.json'

if __name__ == "__main__":
    # appctxt = ApplicationContext()
    settings = Settings(SETTINGS_FILE, VERBOSE)
    if args.database and os.path.exists(args.database):
        settings.db_file = args.database
    if VERBOSE:
        print(settings)
    scrudb = SCDatabase(settings)
    appctxt = AppContext()
    rc = appctxt.run(scrudb)
    # if INTERFACE == 0:
    #     print("Command Line Interface not available in this version.")
    #     # scruinterface.print_settings()
    #     # scruinterface.menu_main()
    # else:
    # import pdb
    # pdb.set_trace()
    # g = gui.App(scrudb)
    # g.start()
    # window = gui.SMainWindow(None, scrudb)
    # window.show()
    # rc = 0
    # rc = appctxt.app.exec_()
    # rc = appctxt.app.exec()
    # del appctxt.app
    settings.write()
    if VERBOSE:
        print(f"Exit main {rc}")
    sys.exit(rc)
