# -*- coding: utf-8 -*-
from twisted.python import log
from twisted.words.protocols import irc

MODE_NORMAL = 0
MODE_VOICE = 1
MODE_OPERATOR = 2

class User(object):
    def __init__(self, client, nick, mode):
        self.client = client
        self.nick = nick
        self.mode = mode
    
    def msg(self, message):
        self.client.msg(self.nick, message)


class Channel(object):
    def __init__(self, client, name):
        self.client = client
        self.name = name
    
    def msg(self, message):
        self.client.msg(self.name, message)


class BaseBot(irc.IRCClient, object):
    def __init__(self):
        self.user_modes = {}

    def get_nickname(self):
        return self.factory.nickname
    
    def set_nickname(self, val):
        self.factory.nickname = val
    nickname = property(get_nickname, set_nickname)

    def signedOn(self):
        log.msg("BaseBot.signedOn")
        self.join(self.factory.channel)
        self.init_users()
        
    def msg(self, user, message, length=None):
        irc.IRCClient.msg(self, user, unicode(message).encode('ascii', 'ignore'), length)

    def init_users(self):
        self.sendLine('NAMES %s' % self.factory.channel)
        
    def joined(self, rawchannel):
        log.msg("BaseBot.joined: %s" % rawchannel)
        channel = Channel(self, rawchannel)
        self.handle_joined(channel)

    def privmsg(self, rawuser, rawchannel, message):
        channel = Channel(self, rawchannel)
        nick = rawuser.split('!')[0]
        mode = self.user_modes.get(nick, MODE_NORMAL)
        user = User(self, nick, mode)
        self.handle_message(user, channel, message)
        
    def handle_message(self, user, channel, message):
        pass
    
    def handle_joined(self, channel):
        pass

    def irc_unknown(self, prefix, command, params):
        if command == 'RPL_NAMREPLY':
            self.handle_namereply(*params)

    def handle_namereply(self, myname, channeltype, channelname, users):
        for user in users.split(' '):
            if user.startswith('@'):
                nick = user[1:]
                self.user_modes[nick] = MODE_OPERATOR
            elif user.startswith('+'):
                nick = user[1:]
                self.user_modes[nick] = MODE_VOICE
            else:
                self.user_modes[user] = MODE_NORMAL
                
    def userRenamed(self, old, new):
        self.user_modes[new] = self.user_modes.pop(old, MODE_NORMAL)
    
    def userLeft(self, user, channel):
        nick = user.split('!')[0]
        self.user_modes.pop(nick, None)
    
    def modeChanged(self, user, channel, set_mode, modes, args):
        nick = args[0] if len(args) == 1 else None
        if 'o' in modes:
            if set_mode:
                self.user_modes[nick] = MODE_OPERATOR
            elif not set_mode:
                self.user_modes[nick] = MODE_NORMAL
        elif 'v' in modes:
            if set_mode:
                self.user_modes[nick] = MODE_VOICE
            elif not set_mode:
                self.user_modes[nick] = MODE_NORMAL
