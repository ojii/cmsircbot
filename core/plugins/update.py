# -*- coding: utf-8 -*-
from core.base import MODE_OPERATOR
from core.plugins import BasePlugin
import os
import subprocess


PLUGINS = ['Update']

PROJECT_DIR = os.path.join(os.path.dirname(__file__), '..', '..')

def get_revision():
    gitdir = os.path.join(PROJECT_DIR, '.git')
    headfile = os.path.join(gitdir, 'HEAD')
    with open(headfile) as fobj:
        head = fobj.read().strip()
    if head.startswith('ref: '):
        headref = head[5:]
        reffile = os.path.join(gitdir, headref)
        with open(reffile) as fobj:
            head = fobj.read().strip()
    return head

class Update(BasePlugin):
    def handle_joined(self, channel):
        channel.msg("%s running at %s" % (self.client.nickname, get_revision()))
        
    def command_update(self, rest, user, channel):
        if user.mode >= MODE_OPERATOR:
            subprocess.check_call(['git', 'pull', 'origin', 'master'], cwd=PROJECT_DIR)
            subprocess.check_call(['sudo', 'supervisorctl', 'restart', 'cmsbot'])
