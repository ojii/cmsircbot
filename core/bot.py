# -*- coding: utf-8 -*-
from core.base import BaseBot
from twisted.internet import protocol
import os


PLUGIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'plugins'))


class CMSBot(BaseBot):
    def __init__(self):
        BaseBot.__init__(self)
        self.plugins = []
        self.load_plugins()
        
    def load_plugins(self):
        for fname in os.listdir(PLUGIN_DIR):
            if fname.endswith('.py'):
                modname = os.path.splitext(fname)[0]
                mod = __import__('core.plugins.%s' % modname, fromlist=['core', 'plugins'])
                for klass_name in getattr(mod, 'PLUGINS', []):
                    klass = getattr(mod, klass_name)
                    plugin = klass(self)
                    self.plugins.append(plugin)
                    
    def handle_message(self, channel, user, message):
        for plugin in self.plugins:
            plugin.handle_message(message, channel, user)
            if message.startswith(self.factory.command_prefix):
                msg = message[len(self.factory.command_prefix):]
                if ' ' in msg:
                    command, rest = msg.split(' ', 1)
                else:
                    command, rest = msg, ''
                plugin.handle_command(command, rest, channel, user)
    
    def handle_joined(self, channel):
        for plugin in self.plugins:
            plugin.handle_joined(channel)


class CMSBotFactory(protocol.ClientFactory):
    protocol = CMSBot

    def __init__(self, channel, nickname, command_prefix):
        self.channel = channel
        self.nickname = nickname
        self.command_prefix = command_prefix

    def clientConnectionLost(self, connector, reason):
        connector.connect()
