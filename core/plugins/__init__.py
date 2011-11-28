
class BasePlugin(object):
    def __init__(self, client):
        self.client = client
        
    def handle_command(self, command, rest, channel, user):
        print self
        handler = getattr(self, 'command_%s' % command, None)
        if callable(handler):
            handler(rest, channel, user)
    
    def handle_message(self, message, channel, user):
        pass
    
    def handle_joined(self, channel):
        pass
