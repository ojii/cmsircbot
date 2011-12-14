# -*- coding: utf-8 -*-
from core.plugins import BasePlugin
from twisted.python import log
from twisted.web.client import getPage
import json
import re


ISSUE_REGULAR_EXPRESSIONS = [
    re.compile(r'#(\d+)'),
    re.compile(r'issue (\d+)', re.I),
] 

PLUGINS = ['Issues']

ISSUES_URL_TPL = 'https://api.github.com/repos/divio/django-cms/issues/%s'


def get_issue_status(issue_id, channel):
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
    getPage(ISSUES_URL_TPL % issue_id).addCallback(callback).addErrback(errback)

class Issues(BasePlugin):
    def handle_message(self, message, user, channel):
        numbers = []
        for pattern in ISSUE_REGULAR_EXPRESSIONS:
            for number in pattern.findall(message):
                if number not in numbers:
                    numbers.append(number)
                    get_issue_status(number, channel)
