#!/usr/bin/env python2
# -*- encoding: utf-8 -*-


from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log

import time
import sys
import logging
import random
import re
import config


SPAM_REG = re.compile(r'\.spam\s(\d+)\s(.*)')
JOIN_REG = re.compile(r'\.join\s(.*)')


class LogBot(irc.IRCClient):
    nickname = config.nick

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)

    def signedOn(self):
        for c in self.factory.channels:
            self.join(c)

    def joined(self, channel):
        logging.info('Joined '+channel)
        self.msg(channel, random.choice(config.JOIN_QUOTES))

    def privmsg(self, user, channel, msg):
        user = user.split('!', 1)[0]

        if channel == self.nickname:
            if re.match(config.admin, user):
                if msg.strip().lower() == '.reconfig':
                    reload(config)
                    self.msg(user, "Reloaded config.")

                reg = SPAM_REG.match(msg.strip().lower())
                if reg:
                    self.msg(user, "yes sir, spamming dat ass")
                    for i in xrange(int(reg.group(1))):
                        self.msg(reg.group(2), random.choice(config.QUOTES))
                    self.msg(user, "spam done")

                reg = JOIN_REG.match(msg.strip().lower())
                if reg:
                    self.msg(user, "Yes sir, joined that channel")
                    self.join(reg.group(1))
                return

            self.msg(user, "dhow mnay task u did")
            return

        if msg.startswith(self.nickname):
            self.msg(channel, random.choice(config.QUOTES))

    def action(self, user, channel, msg):
        user = user.split('!', 1)[0]

    def irc_NICK(self, prefix, params):
        old_nick = prefix.split('!')[0]
        new_nick = params[0]
        logging.info(params)

    def alterCollidedNick(self, nickname):
        return nickname + config.collision_append


class SvotBotFactory(protocol.ClientFactory):
    def __init__(self, channels):
        self.channels = channels

    def buildProtocol(self, addr):
        p = LogBot()
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        logging.error("connection failed:", reason)
        reactor.stop()


if __name__ == '__main__':
    log.startLogging(sys.stdout)
    logging.basicConfig(level=logging.INFO)

    try:
        import config
    except ImportError:
        logging.error('Don\'t ever play yourself - DJ Khaled')
        logging.error('Congratulations, you just played yourself')
    f = SvotBotFactory(config.channels)

    reactor.connectTCP("irc.freenode.net", 6667, f)
    reactor.run()


