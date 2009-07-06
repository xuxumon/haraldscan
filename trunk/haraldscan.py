#!/usr/bin/env python
#
# haraldscan.py
# June 2009
# Terence Stenvold <tstenvold@gmail.com>
#
#Main script for the running of harald scan

import deviceclass
import discovery
import haraldsql
import haraldcli
import haraldusage
import time,sys,os
import getopt


def cleanup(connection, cursor):
    haraldcli.clear()
    haraldcli.move(0,0)
    haraldsql.drop_dev_table(cursor)
    haraldsql.close_database(connection)


try:
    opts, args = getopt.getopt(sys.argv[1:], "hw:b", ["help", "write=", "build"])
except getopt.GetoptError, err:
    print str("Unknown Command use --help for information")
    haraldusage.usage()

write_file = False
filename = None
buildb = False

for o, a in opts:
    if o in ("-b", "--build"):
        buildb = True
    elif o in ("-w", "--write"):
        write_file = True
        filename = a
    elif o in ("-h", "--help"):
        haraldusage.usage()
    else:
        assert False, "unhandled option"


#Calls to initialize the program
connection = haraldsql.open_database()
cursor = haraldsql.get_cursor(connection)

if buildb:
    status = haraldsql.refresh_maclist(connection)
    for k, v in status.iteritems():
       print k, ': ', v
    print "Database Built"

else:
    haraldsql.setup_dev_table(connection)
    d = discovery.harald_discoverer()
    d.set_cursor(cursor)
    haraldcli.init_screen()

    try:
        while True:
            d.find_devices(lookup_names=True)

            while True:
                d.process_event()
                if d.done == True:
                    break

            haraldcli.write_screen(cursor)

            if write_file:
                haraldsql.write_dev_table(cursor, filename)

    except (KeyboardInterrupt, SystemExit):
        cleanup(connection, cursor)