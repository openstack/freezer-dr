#__author__ = 'saad'
from daemon import Daemon
import sys
import logging as log
import time
log.basicConfig(filename='osha.log')


class Osha(Daemon):

    def run(self):
        # @todo scheduling code goes here ! may be apscheduler or just cron !
        # just as a test ...
        while True:
            time.sleep(1)


if __name__ == '__main__':
    osha = Osha('/var/run/osha/osha.pid') # won't run unless the folder is
    # already created and have the correct permissions !
    if len(sys.argv) == 2:
        if sys.argv[1] == 'start':
            osha.start()
        elif sys.argv[1] == 'stop':
            osha.stop()
        elif sys.argv[1] == 'restart':
            osha.restart()
        elif sys.argv[1] == 'status':
            osha.status()
        else:
            print "Unknown command "
            print "Usage %s start|stop|restart" % sys.argv[0]
            sys.exit(2)
        sys.exit(0)
    else:
        print "Usage %s start|stop|restart" % sys.argv[0]
        sys.exit(0)
