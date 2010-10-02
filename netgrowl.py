#!/usr/bin/env python

# Altered 1st October 2010 - Tim Child.
# Have added the ability for the command line arguments to take a password.

# Altered 1-17-2010 - Tanner Stokes - www.tannr.com
# Added support for command line arguments

# ORIGINAL CREDITS
# """Growl 0.6 Network Protocol Client for Python"""
# __version__ = "0.6.3"
# __author__ = "Rui Carmo (http://the.taoofmac.com)"
# __copyright__ = "(C) 2004 Rui Carmo. Code under BSD License."
# __contributors__ = "Ingmar J Stein (Growl Team), John Morrissey (hashlib patch)"

try:
  import hashlib
  md5_constructor = hashlib.md5
except ImportError:
  import md5
  md5_constructor = md5.new

import struct
# needed for command line arguments
import sys
import getopt

from socket import AF_INET, SOCK_DGRAM, socket

GROWL_UDP_PORT=9887
GROWL_PROTOCOL_VERSION=1
GROWL_TYPE_REGISTRATION=0
GROWL_TYPE_NOTIFICATION=1

def main(argv):

    # default to sending to localhost
    host = "localhost"
    # default title
    title = "Title"
    # default description
    description = "Description"
    # default priority
    priority = 0
    # default stickiness
    sticky = False

    try:
        opts, args = getopt.getopt(argv, "hH:t:d:p:s:x:")
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h"):
            usage()
            sys.exit()
        elif opt in ("-H"):
            host = arg
        elif opt in ("-t"):
            title = arg
        elif opt in ("-d"):
            description = arg
        elif opt in ("-x"):
            password = arg
        elif opt in ("-p"):
            # acceptable values: -2 to 2
            priority = int(arg)
        elif opt in ("-s"):
            sticky = True
    # connect up to Growl server machine
    addr = (host, GROWL_UDP_PORT)

    s = socket(AF_INET,SOCK_DGRAM)
    # register application with remote Growl
    p = GrowlRegistrationPacket(password=password)
    p.addNotification()
    # send registration packet
    s.sendto(p.payload(), addr)

    # assemble notification packet
    p = GrowlNotificationPacket(title=title, description=description, priority=priority, sticky=sticky,password=password)

    # send notification packet
    s.sendto(p.payload(), addr)
    s.close()

def usage():
    print """Usage: ./netgrowl.py [-hs] [-H hostname] [-t title] [-d description] [-p priority] [-x password]
Send Growl messages over UDP
  -h help
  -H specify host
  -t title
  -d description
  -p priority [-2 to 2]
  -s make sticky
  -x password
  """

class GrowlRegistrationPacket:
  """Builds a Growl Network Registration packet.
     Defaults to emulating the command-line growlnotify utility."""

  def __init__(self, application="NetGrowl", password = None ):
    self.notifications = []
    self.defaults = [] # array of indexes into notifications
    self.application = application.encode("utf-8")
    self.password = password
    print password
  # end def

  def addNotification(self, notification="Command-Line Growl Notification", enabled=True):
    """Adds a notification type and sets whether it is enabled on the GUI"""
    self.notifications.append(notification)
    if enabled:
      self.defaults.append(len(self.notifications)-1)
  # end def

  def payload(self):
    """Returns the packet payload."""
    self.data = struct.pack( "!BBH",
                             GROWL_PROTOCOL_VERSION,
                             GROWL_TYPE_REGISTRATION,
                             len(self.application) )
    self.data += struct.pack( "BB",
                              len(self.notifications),
                              len(self.defaults) )
    self.data += self.application
    for notification in self.notifications:
      encoded = notification.encode("utf-8")
      self.data += struct.pack("!H", len(encoded))
      self.data += encoded
    for default in self.defaults:
      self.data += struct.pack("B", default)
    self.checksum = md5_constructor()
    self.checksum.update(self.data)
    if self.password:
       self.checksum.update(self.password)
    self.data += self.checksum.digest()
    return self.data
  # end def
# end class

class GrowlNotificationPacket:
  """Builds a Growl Network Notification packet.
     Defaults to emulating the command-line growlnotify utility."""

  def __init__(self, application="NetGrowl",
               notification="Command-Line Growl Notification", title="Title",
               description="Description", priority = 0, sticky = False, password = None ):

    self.application  = application.encode("utf-8")
    self.notification = notification.encode("utf-8")
    self.title        = title.encode("utf-8")
    self.description  = description.encode("utf-8")
    flags = (priority & 0x07) * 2
    if priority < 0:
      flags |= 0x08
    if sticky:
      flags = flags | 0x0100
    self.data = struct.pack( "!BBHHHHH",
                             GROWL_PROTOCOL_VERSION,
                             GROWL_TYPE_NOTIFICATION,
                             flags,
                             len(self.notification),
                             len(self.title),
                             len(self.description),
                             len(self.application) )
    self.data += self.notification
    self.data += self.title
    self.data += self.description
    self.data += self.application
    self.checksum = md5_constructor()
    self.checksum.update(self.data)
    if password:
       self.checksum.update(password)
    self.data += self.checksum.digest()
  # end def

  def payload(self):
    """Returns the packet payload."""
    return self.data
  # end def
# end class

if __name__ == '__main__':

    # send command line arguments to main() function
    main(sys.argv[1:])