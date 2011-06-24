from logging import Handler
import os

class PipeMailHandler(Handler):
    def __init__(self, toaddrs, subject, sendmail = 'sendmail'):
        Handler.__init__(self)
        self.sendmail = '%s -t' % sendmail
        self.msg = """To: %s
Subject: %s

""" % (', '.join(toaddrs), subject)

    def emit(self, record):
        msg = self.msg + record.getMessage()
        p = os.popen(self.sendmail, 'w')
        p.write(msg)
        if p.close():
            pass # failure
