# -*- coding: utf-8 -*-
from core.plugins import BasePlugin

import re

ISSUE_REGEX = re.compile(r'#(\d+)') 

PLUGINS = ['Issues']

class Issues(BasePlugin):
    def handle_message(self, message, user, channel):
        match = ISSUE_REGEX.search(message)
        if match:
            number = match.group(1)
            channel.msg('Issue #%s: https://github.com/divio/django-cms/issues/%s' % (number, number))
