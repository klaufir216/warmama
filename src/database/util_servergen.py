#!/usr/bin/env python3

"""
Created on 30.3.2011
@author: hc
"""
from __future__ import print_function
import random
import string
import socket
import sys
import MySQLdb
from __future__ import absolute_import
from __future__ import unicode_literals

###################
#
# Imports

from builtins import range
import config
from database import models
import warmama

import pymysql
pymysql.install_as_MySQLdb()

###################
#
# Constants

###################
#
# Globals

###################
#
# Helpers


def safeint(s):
    try:
        return int(s)
    except ValueError:
        return 0


def is_ipv4(s):
    try:
        socket.inet_pton(socket.AF_INET, s)
        return True
    except socket.error:
        return False


def is_ipv6(s):
    try:
        socket.inet_pton(socket.AF_INET6, s)
        return True
    except socket.error:
        return False

###################
#
# Classes


if __name__ == '__main__':

    # we need servergen IP <count>
    if(len(sys.argv) < 2):
        print("Usage: servergen IP [count]")
        exit()

    count = 1
    ip = sys.argv[1]
    if(len(sys.argv) > 2):
        count = safeint(sys.argv[2])

    ipv4, ipv6 = warmama.ipv4_ipv6(ip)
    if(ipv4 is None or ipv6 is None):
        print("%s is not valid ip" % ip)
        exit()

    if(count <= 0):
        print("Invalid count")
        exit()

    connection = MySQLdb.connect(host=config.db_host,
                                 port=config.db_port,
                                 user=config.db_user,
                                 passwd=config.db_passwd,
                                 db=config.db_name)

    cursor = connection.cursor()

    # authkey's are random character-strings, 64-bit length

    # URL encoding characters
    my_printable = string.ascii_letters + string.digits + '_-'
    table_servers = models.table_Servers()
    table_servers.cursor = cursor

    while(count > 0):

        digest = [my_printable[random.randint(
            0, len(my_printable) - 1)] for x in range(64)]
        digest = ''.join(digest)

        # now lets see if we have this in database
        # SELECT count(*) FROM servers where login = digest
        r = table_servers.select2('id', 'login=%s', (digest, ))
        #cursor.execute( ( 'SELECT count(*) FROM %s WHERE login=%%s' % table_servers.tablename), (digest,) )
        #r = cursor.fetchone()
        # if( not r or (r != None and r[0] == 0) ) :
        if(not r):
            # create new
            query = """
			(created, updated, login, regip, regipv6, hostname, ip, ipv6, location, banned, demos_baseurl)
			VALUES( NOW(), NOW(), %s, %s, %s, '', %s, %s, 'ZZ', 0, '' )
			"""
            values = (digest, ipv4, ipv6, ipv4, ipv6)

            table_servers.insert(query, values)

            connection.commit()

            print("Created authkey: %s" % digest)

            count -= 1
