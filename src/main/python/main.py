"""Scrutini Main"""
import argparse
from db import SCDatabase
from fbs_runtime.application_context.PyQt5 import ApplicationContext

# initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-i0", "--interface0",
                    help="Use command-line interface (0)", action="store_true")
parser.add_argument("-i1", "--interface1",
                    help="Use Graphical User Interface (1)",
                    action="store_true")
# read arguments from the command line
args = parser.parse_args()
# check for --interface0 or -i0
if args.interface0:
    interface = 0
    import scruinterface0 as scruinterface
    print("Command-Line Interface (0)")
else:
    interface = 1
    import gui
    print("GUI (1)")

if __name__ == "__main__":
    appctxt = ApplicationContext()
    import sys
    db_filename = 'scrutini.db'
    schema_filename = 'scrutinischema.sql'
    app_version = 0.2
    schema_version = 0.2
    scrudb = SCDatabase(db_filename, schema_filename, app_version,
                        schema_version, 'current')
    # scrudb.check()
    if interface == 0:
        scruinterface.print_settings()
        scruinterface.menu_main()
    else:
        g = gui.Interface(scrudb)
        g.start()
    rc = appctxt.app.exec_()
    # del appctxt.app
    print(f"Exit main {rc}")
    sys.exit(rc)
