#!/usr/bin/env python3

"""
Created on 30.3.2011
@author: hc
"""
from __future__ import unicode_literals
import urllib.error
import urllib.parse
import urllib.request
import threading
import warmama
import database
import config

###################
#
# Imports

from future import standard_library
standard_library.install_aliases()


###################
#
# Constants

###################
#
# Globals

###################
#
# Helpers

###################
#
# Classes

'''
Here some thoughts about how servers login and what is needed

	- authkey
	- ip
	- cookie

check existing session (expiration, ip)
(uuid, ip) from user
'''


def ServerLogin(authkey, addr):

    # loadUser whatnot

    # session.GetExistingSession

    # overwrite attribs to Session
    # return Session

    # else
    # session.NewSession( user )

    return None


'''
ClientLogin

client logins are 2-step
	a) client requests a login and receives a handle to a login process
	b) client does requests with this new handle until it receives
		validation

MM after getting authrequest from client, creates a userlogin element to database,
initiates async POST request to the auth-server and returns a handle to this process
to the client.
When auth-server has (in)validated the request, it sends a POST request back to MM
which marks the userlogin element that the client has a handle to.
'''


class ClientLogin(threading.Thread):

    def __init__(self, mm, login, pw, handle):
        threading.Thread.__init__(self)

        self.mm = mm
        self.login = login
        self.pw = pw

        # TODO: add digest
        self.handle = handle

        self.start()

    ##############################

    def GetHandle(self):
        return self.handle

    ###############################

    def run(self):

        try:
            # create the url object
            data = urllib.parse.urlencode({'login': self.login,
                                           'passwd': self.pw,
                                           'handle': '%d' % self.handle,
                                           'digest': 'something',
                                           'url': config.auth_response_url
                                           })

            # TODO: dont write the password or anything for real!
            # print("**** CLIENTLOGIN CALLING %s %s" % ( config.getauth_url, data ) )
            # self.mm.log("**** CLIENTLOGIN CALLING %s %s" % ( config.getauth_url, data ) )

            opener = urllib.request.build_opener()
            opener.addheaders = [('User-agent', 'Warmama/1.0')]
            response = opener.open(config.getauth_url, data).read()

            # TODO: response will be MM_DATA_MISSING | MM_AUTH_SENT | MM_AUTH_SENDING_FAILED
            # print( "**** CLIENTLOGIN RESPONSE: %s" % response )
            self.mm.log("**** CLIENTLOGIN RESPONSE: %s" % response)
            opener.close()

        except urllib.error.HTTPError as e:
            # print( "ClientLogin: Failed to fetch %s" % config.getauth_url )
            self.mm.log(
                "ClientLogin: Failed to fetch %s, code: %i" %
                (config.getauth_url, e.code))
            pass  # this means no user credentials
        except urllib.error.URLError as e:
            # print( "ClientLogin: Failed to fetch %s" % config.getauth_url )
            self.mm.log(
                "ClientLogin: Failed to fetch %s, reason: %s" %
                (config.getauth_url, e.reason))
            pass  # this means no user credentials


class ClientLoginSteam(threading.Thread):

    def __init__(self, mm, id, ticket):
        threading.Thread.__init__(self)

        self.mm = mm
        self.id = id
        self.ticket = ticket
        self.login = mm.dbHandler.LoadUserLoginBySteamID(id)
        if self.login is None:
            self.login = mm.dbHandler.GetStubSteamLogin(id)

        # TODO: add digest
        self.handle = mm.dbHandler.SaveUserLogin(
            0, self.login, 0, 0, None, None, id, ticket)

        self.start()

    ##############################

    def GetHandle(self):
        return self.handle

    ###############################

    def run(self):

        try:
            # create the url object
            url = config.getauth_url
            data = urllib.parse.urlencode({'login': self.login,
                                           'steam_id': self.id,
                                           'steam_ticket': self.ticket,
                                           'handle': '%d' % self.handle,
                                           'digest': 'something',
                                           'url': config.auth_response_url
                                           })

            req = urllib.request.urlopen(url, data)
            response = req.read()

            # TODO: response will be MM_DATA_MISSING | MM_AUTH_SENT | MM_AUTH_SENDING_FAILED
            # print( "**** CLIENTLOGIN RESPONSE: %s" % response )
            self.mm.log("**** CLIENTLOGIN RESPONSE: %s" % response)
            req.close()

        except urllib.error.HTTPError as e:
            # print( "ClientLogin: Failed to fetch %s" % config.getauth_url )
            self.mm.log(
                "ClientLoginSteam: Failed to fetch %s, code: %i" %
                (url, e.code))
            pass  # this means no user credentials
        except urllib.error.URLError as e:
            # print( "ClientLogin: Failed to fetch %s" % config.getauth_url )
            self.mm.log(
                "ClientLoginSteam: Failed to fetch %s, reason: %s" %
                (url, e.reason))
            pass  # this means no user credentials
