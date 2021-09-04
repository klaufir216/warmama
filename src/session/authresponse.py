#!/usr/bin/env python3

'''
Created on 12.4.2011

@author: hc
'''
from __future__ import print_function
from __future__ import unicode_literals

###################
#
# Imports

from builtins import str
from builtins import object
import web
import datetime

import config


def safeint(s):
    try:
        return int(s)
    except BaseException:
        return 0

##########################


class authresponse(object):
    def POST(self):
        input = web.input()

        handle = safeint(input.get('handle', '-99999'))
        digest = input.get('digest', 'thisiswrongrighthere')
        valid = safeint(input.get('valid', '-9999'))

        print("handle: %d, digest: %s, valid: %d" % (handle, digest, valid))

        f = open('/home/toukkapoukka/shitass.txt', 'a')
        f.write('\
		%s authresponse: handle: %d, digest: %s, valid: %d\n\
		%s\n' % (datetime.datetime.now(), handle, digest, valid, str(web.input())))
        f.close()

        f = open('/home/toukkapoukka/web_ctx', 'w')
        f.write('\n' % str(web.ctx))
        f.close()

        return 'valid %d' % (valid)


##########################

urls = ('/authresponse', 'authresponse')

app = web.application(urls, globals(), autoreload=False)

if __name__ == "__main__":
    # this is for spawn-fcgi
    web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
    app.run()
elif config.cgi_mode == 'wsgi':
    # wsgi
    application = app.wsgifunc()
