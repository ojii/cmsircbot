# -*- coding: utf-8 -*-
from ircbotframework.bot import MODE_OPERATOR
from ircbotframework.plugin import BasePlugin
import os


DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'faq.db'))

class FAQ(BasePlugin):
    def __init__(self, protocol, conf):
        super(FAQ, self).__init__(protocol, conf)
        if os.path.exists(DB_PATH):
            with open(DB_PATH, 'r') as fobj:
                data = fobj.read()
            self.faqs = dict([line.split(':', 1) for line in data.split('\n') if line.strip()])
        else:
            self.faqs = {}
    
    def write(self):
        with open(DB_PATH, 'w') as fobj:
            fobj.write('\n'.join([':'.join(x) for x in self.faqs.items()]))
        
    def command_addfaq(self, rest, channel, user):
        if user.mode < MODE_OPERATOR:
            channel.msg("You can't add FAQs")
        elif ' ' not in rest:
            channel.msg('Try !addfaq <identifier> <answer>')
        else:
            identifier, answer = rest.split(' ', 1)
            if ':' in identifier:
                channel.msg('Identifier cannot contain a colon')
            else:
                self.faqs[identifier] = answer
                self.write()
                channel.msg('Added FAQ entry for %r' % identifier)

    def command_listfaq(self, rest, channel, user):
        channel.msg('Available FAQs: %s' % ', '.join(self.faqs.keys()))
    
    def command_faq(self, rest, channel, user):
        answer = self.faqs.get(rest, None)
        if answer:
            channel.msg('%s: %s' % (rest, answer))
        else:
            channel.msg('No FAQ found for %r, try !listfaq to see available entries' % rest)
