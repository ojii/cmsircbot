# -*- coding: utf-8 -*-
from ircbotframework.plugin import BasePlugin, RegistryDictionary
from twisted.python import log
from twisted.web.client import getPage
import cgi
import json
import os
import re


ISSUE_REGULAR_EXPRESSIONS = [
    re.compile(r'#(\d+)'),
    re.compile(r'issue (\d+)', re.I),
] 

ISSUES_URL_TPL = 'https://api.github.com/repos/%s/%s/issues/%s'

SECRET_KEY_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'secretkey'))

HANDLERS = RegistryDictionary()

@HANDLERS('error')
def errhandler(plugin, payload):
    log.msg("Unknown action to webhook: %s" % payload.get('action', None))

@HANDLERS('created')
def created(plugin, payload):
    message = '%s commented on issue #%s "%s": %s' % (
        payload['sender']['login'],
        payload['issue']['number'],
        payload['issue']['title'],
        payload['issue']['html_url']
    )
    plugin.message_channel(message)

@HANDLERS('closed')
def closed(plugin, payload):
    message = '%s closed issue #%s "%s": %s' % (
        payload['sender']['login'],
        payload['issue']['number'],
        payload['issue']['title'],
        payload['issue']['html_url']
    )
    plugin.message_channel(message)

@HANDLERS('opened')
def opened(plugin, payload):
    message = '%s reported issue #%s "%s": %s' % (
        payload['sender']['login'],
        payload['issue']['number'],
        payload['issue']['title'],
        payload['issue']['html_url']
    )
    plugin.message_channel(message)

@HANDLERS('reopened')
def reopened(plugin, payload):
    message = '%s reopened issue #%s "%s": %s' % (
        payload['sender']['login'],
        payload['issue']['number'],
        payload['issue']['title'],
        payload['issue']['html_url']
    )
    plugin.message_channel(message)


class Issues(BasePlugin):
    routes = RegistryDictionary()
    
    def post_init(self):
        self.secretkey = None
        if os.path.exists(SECRET_KEY_FILE):
            with open(SECRET_KEY_FILE, 'r') as fobj:
                self.secretkey = fobj.read().strip()

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

    @routes(re.compile('/issues/(?P<secretkey>\w{32})/'))
    def webhook(self, request, secretkey):
        if secretkey != self.secretkey:
            log.msg("Invalid secret key")
            return
        rawdata = cgi.escape(request.args["payload"][0])
        payload = json.loads(rawdata)
        handler = HANDLERS.get(payload.get('action', 'error'), errhandler)
        try:
            handler(self, payload)
        except Exception, e:
            log.err(e)
