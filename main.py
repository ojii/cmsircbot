#!/usr/bin/env python
from core.bot import CMSBotFactory
from twisted.internet import reactor
from twisted.python import log
import sys

def run(network, port, channel, username, commandprefix):
    factory = CMSBotFactory('#%s' % channel, username, commandprefix)
    reactor.connectTCP(network, port, factory)
    reactor.run()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--network', required=True)
    parser.add_argument('-p', '--port', type=int, default=6667)
    parser.add_argument('-c', '--channel', required=True)
    parser.add_argument('-u', '--username', required=True)
    parser.add_argument('--commandprefix', default='!')
    args = parser.parse_args()
    log.startLogging(sys.stdout)
    run(args.network, args.port, args.channel, args.username, args.commandprefix)

