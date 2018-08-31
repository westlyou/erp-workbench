#!/usr/bin/env python

import sys, time
from ooin_server.daemon import Daemon

class OODaemon(Daemon):
    def run(self):
        while True:
            time.sleep(1)

if __name__ == "__main__":
    daemon = OODaemon('/tmp/daemon-ooin.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print("Unknown command")
            sys.exit(2)
        sys.exit(0)
    else:
        print("usage: %s start|stop|restart" % sys.argv[0])
        sys.exit(2)