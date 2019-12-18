# Write your code here :-)
from PyQt5 import QtWidgets, QtGui, QtCore
import os
import sqlite3
import argparse
import scrudb
from scruclasses import *
from fbs_runtime.application_context.PyQt5 import ApplicationContext


conn = None

# initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-i0", "--interface0",
                    help="Use command-line interface (0)", action="store_true")
parser.add_argument("-i1", "--interface1",
                    help="Use Graphical User Interface (1)", action="store_true")

# read arguments from the command line
args = parser.parse_args()

# check for --interface0 or -i0
if args.interface0:
    interface = 0
    import scruinterface0 as scruinterface
    print("Command-Line Interface (0)")
else:
    interface = 1
    import scruinterface1 as scruinterface
    print("GUI (1)")


if __name__ == "__main__":
    appctxt = ApplicationContext()
    import sys
    scrudb.check_db()

    scruinterface.print_settings()
    scruinterface.menu_main()
    scrudb.close_connection()
    sys.exit(appctxt.app.exec_())