#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Check Shinken from poller to livestatus module
"""
#
#
#     Copyright (C) 2012 Savoir-Faire Linux Inc.
#
#     This program is free software; you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation; either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program; if not, write to the Free Software
#     Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
#     Projects :
#               SFL Shinken plugins
#
#     File :
#               check_poller2livestatus.py Check Shinken from poller to livestatus module
#
#
#     Author: Thibault Cohen <thibault.cohen@savoirfairelinux.com>
#
#

from datetime import datetime
import subprocess
import getopt
import socket
import sys
import time


PLUGIN_NAME = "check_poller2livestatus"
PLUGIN_VERSION = "0.1"
STATE_OK = 0
STATE_WARNING = 1
STATE_CRITICAL = 2
STATE_UNKNOWN = 3
STATE_DEPENDENT = 4


def print_version():
    """Show plugin version
    """
    version_msg = """
%s.py v%s (sfl-shinken-plugins)

The SFL Shinken Plugins come with ABSOLUTELY NO WARRANTY. You may redistribute
copies of the plugins under the terms of the GNU General Public License.
For more information about these matters, see the file named COPYING.
""" % (PLUGIN_NAME, PLUGIN_VERSION)
    print version_msg


def print_support():
    """Show plugin support
    """
    support_msg = """
Send email to <thibault.cohen@savoirfairelinux.com> if you have questions
regarding use of this software. To submit patches or suggest improvements,
send email to <thibault.cohen@savoirfairelinux.com>
Please include version information with all correspondence (when
possible, use output from the --version option of the plugin itself).
"""
    print support_msg


def print_usage():
    """Show how to use this plugin
    """
    usage_msg = """
%s.py -B <broker_address> [-P <broker_port>] -H <hostname> [-S <servicename>] [-t <last_check>] [-p <poller_name>] [-e <email>]

Usage:
 -h, --help
    Print detailed help screen
 -B, --broker-address
    Broker address
 -P, --broker-port
    Broker port
    default: 50000
 -H, --hostname=ADDRESS
    Hostname to check from shinken comfiguration
 -S, --servicename=ADDRESS
    Service to check from shinken comfiguration
    default: don't check a service, check a host
 -t, --last-check=INT
    max seconds accepted since the last check
    default: this plugin will get it from livestatus and add 30 %%
 -p, --poller-name
    Use only to show it in email notification.
    Doesn't have any impact on the check
 -e, --email
    email to send the notification
    default: don't send email, just print error and exit code = 1
 -v, --verbose
    Verbose mode
 -V, --version
    Print version information
""" % PLUGIN_NAME
    print usage_msg


def send_email(email_to, message):
    command = "echo '%s' | mail -s 'Monitoring system problem detection' %s" % (message, email_to)
    subprocess.call(command, shell=True)


def get_data(args):
    """Fetch data
    """
    verbose = args['verbose']
    ls_con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connection
    try:
        ls_con.connect((args['broker-address'], args['broker-port']))
    except:
        if args['email']:
            message = ("Monitoring system problem detection\n "
                       "Error while connecting to livestatus")
            send_email(args['email'], message)
        print "Error while connecting to livestatus"
        sys.exit(STATE_CRITICAL)

    if args['servicename']:
        command = 'GET services\nColumns: host_name description last_check check_interval\nFilter: host_name = %s\nFilter: description = %s\n' % (args['hostname'], args['servicename'])
    else:
        command = 'GET hosts\nColumns: host_name last_check check_interval\nFilter: host_name = %s\n' % args['hostname']
    if verbose:
        print "Livestatus query:", command
    # send command
    try:
        ls_con.send(command + 'Limit: 1\n\n')
    except:
        if args['email']:
            message = ("Monitoring system problem detection\n "
                       "Error while sending livestatus query")
            send_email(args['email'], message)
        print "Error while sending livestatus query"
        sys.exit(STATE_CRITICAL)
    # Receive response
    try:
        output = ls_con.recv(1024)
    except:
        if args['email']:
            message = ("Monitoring system problem detection\n "
                       "Error while reading livestatus query")
            send_email(args['email'], message)
        print "Error while reading livestatus query"
        sys.exit(STATE_CRITICAL)
    # Parse response
    if verbose:
        print "Livestatus output:", output
    try:
        hostname, last_check, check_interval = [x.strip() for x in output.rsplit(";", 2)]
        last_check = int(last_check)
        check_interval = int(check_interval) * 60
    except:
        if args['email']:
            message = ("Monitoring system problem detection\n "
                       "Bad response from thr broker: \n"
                       "`%s' " % output)
                      
            send_email(args['email'], message)
        print "Bad response from livestatus"
        sys.exit(STATE_CRITICAL)

    # Processing
    now = int(time.time())
    #check_interval = 5
    data = {}
    if args['last-check'] is None:
        data['threshold'] = int(check_interval * 0.2 + check_interval)
    else:
        data['threshold'] = args['last-check']
    data['hostname'] = args['hostname']
    data['now'] = datetime.fromtimestamp(now)
    data['last_check'] = datetime.fromtimestamp(last_check)
    data['delta'] = now - last_check
    data['poller_name'] = args['poller_name']
    if now - data['threshold'] > last_check:
        message = ("Monitoring system problem detection\nThe host: "
                   "'%(hostname)s' was not checked for %(threshold)s "
                   "seconds by the poller: %(poller_name)s\nThe poller "
                   "and/or the scheduler could be in error." % data)
        if args['email']:
            send_email(args['email'], message)
        else:
            print message
            if verbose:
                message = ("now: %(now)s\n"
                           "last_check: %(last_check)s\n"
                           "delta: %(delta)s seconds\n"
                           "threshold: %(threshold)s seconds" % data)
                if data['poller_name']:
                    message = message + "\nPoller: %(poller_name)s" % data
                print message
            sys.exit(STATE_CRITICAL)
    else:
        if verbose:
            message = ("Poller seems good !!!\n"
                       "now: %(now)s\n"
                       "last_check: %(last_check)s\n"
                       "delta: %(delta)s seconds\n"
                       "threshold: %(threshold)s seconds" % data)
            if data['poller_name']:
                message = message + "\nPoller: %(poller_name)s" % data
            print message
        sys.exit(STATE_OK)


def check_arguments(args):
    """Check mandatory fields
    """
    mandatory_arguments = ['broker-address',
                           'hostname']
    for argument_name in mandatory_arguments:
        if not argument_name in args.keys():
            print "Argument '%s' is missing !" % argument_name
            print_usage()
            print_support()
            sys.exit(STATE_UNKNOWN)

    if not 'broker-port' in args.keys():
        args['broker-port'] = 50000
    else:
        try:
            args['broker-port'] = int(args['broker-port'])
        except:
            print "Argument `broker-port': Bad format !"
            print_usage()
            print_support()
            sys.exit(STATE_UNKNOWN)

    if not 'servicename' in args.keys():
        args['servicename'] = None

    if not 'verbose' in args.keys():
        args['verbose'] = False

    if not 'poller_name' in args.keys():
        args['poller_name'] = False

    if not 'email' in args.keys():
        args['email'] = False

    if not 'last-check' in args.keys():
        args['last-check'] = None
    else:
        try:
            args['last-check'] = int(args['last-check'])
        except:
            print "Argument `last-check': Bad format !"
            print_usage()
            print_support()
            sys.exit(STATE_UNKNOWN)

def main():
    """Main fonction
    """
    try:
        options, args = getopt.getopt(sys.argv[1:],
                        'B:P:H:S:t:e:p:hVv',
                        ['broker-address=', 'broker-port=', 'email=',
                         'hostname=', 'help', 'version', 'verbose',
                         'last-check=', 'servicename=', 'poller-name='])
    except getopt.GetoptError, err:
        print str(err)
        print_usage()
        sys.exit(STATE_UNKNOWN)

    args = {}

    for option_name, value in options:
        if option_name in ("-B", "--broker-address"):
            args['broker-address'] = value
        elif option_name in ("-P", "--broker-port"):
            args['broker-port'] = value
        elif option_name in ("-H", "--hostname"):
            args['hostname'] = value
        elif option_name in ("-S", "--servicename"):
            args['servicename'] = value
        elif option_name in ("-t", "--last-check"):
            args['last-check'] = value
        elif option_name in ("-p", "--poller-name"):
            args['poller_name'] = value
        elif option_name in ("-e", "--email"):
            args['email'] = value
        elif option_name in ("-v", "--verbose"):
            args['verbose'] = True
        elif option_name in ("-h", "--help"):
            print_version()
            print_usage()
            print_support()
            sys.exit(STATE_UNKNOWN)
        elif option_name in ("-V", "--version"):
            print_version()
            print_support()
            sys.exit(STATE_UNKNOWN)

    check_arguments(args)

    get_data(args)


if __name__ == "__main__":
    main()
