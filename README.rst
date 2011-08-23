netgrowl.py
===========

This is a very simple script for sending Growl messages using Python to a Growl listener.

It has no dependancies except Python.  It has been tested with Python 2.6.*

The original authors are listed within the file.

Usage
-----

Usage: ./netgrowl.py [-hs] [-H hostname] [-t title] [-d description] [-p priority] [-x password]
    
Send Growl messages over UDP

 * -h help
 * -H specify host
 * -t title
 * -d description
 * -p priority [-2 to 2]
 * -s make sticky
 * -x password


This script is supplied as is.
