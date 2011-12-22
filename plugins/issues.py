# -*- coding: utf-8 -*-
from ircbotframework.plugin import BasePlugin
from twisted.python import log
from twisted.web.client import getPage
import json
import re


ISSUE_REGULAR_EXPRESSIONS = [
    re.compile(r'#(\d+)'),
    re.compile(r'issue (\d+)', re.I),
] 

ISSUES_URL_TPL = 'https://api.github.com/repos/%s/%s/issues/%s'

class Issues(BasePlugin):
    def handle_message(self, message, channel, user):
        numbers = []
        if user.nick in ['django-cibot']:
            return
        for pattern in ISSUE_REGULAR_EXPRESSIONS:
            for number in pattern.findall(message):
                if number not in numbers:
                    numbers.append(number)
                    self.get_issue_status(number, channel)

    def get_issue_status(self, issue_id, channel):
        def callback(data):
            try:
                issue = json.loads(data)
            except ValueError:
                log.msg("Could not load JSON data: %r" % data)
                log.err()
                channel.msg("Error looking up issue #%s" % issue_id)
                return
            channel.msg("Issue #%(number)s: %(title)s (%(state)s): %(html_url)s" % issue)
            
        def errback(failure):
            try:
                failure.raiseException()
            except:
                log.err()
            channel.msg("Error looking up issue #%s" % issue_id)
        defered = getPage(ISSUES_URL_TPL % (self.conf['GITHUB_USER'], self.conf['GITHUB_PROJECT'], issue_id))
        defered.addCallback(callback).addErrback(errback)
