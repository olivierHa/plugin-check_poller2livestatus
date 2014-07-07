#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
#  Copyright (C) 2012 Savoir-Faire Linux Inc.
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
#  Projects :
#            Shinken plugins
#
#  File :
#            check_poller2livestatus.py Check Shinken from poller to livestatus module
#
#
#  Author: Thibault Cohen <thibault.cohen@savoirfairelinux.com>
#
#

import unittest
import sys
import os
import time
import re
from StringIO import StringIO

sys.path.append("..")

import check_poller2livestatus


class TestPlugin(unittest.TestCase):
    def setUp(self):
        pass

    def test_help(self):
        """Test help output :
           -h
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('-h')
        self.do_tst(3, """^check_poller2livestatus""")

    def test_version(self):
        """Test version output :
           -V
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('-V')
        self.do_tst(3, "^check_poller2livestatus.py v%s" % check_poller2livestatus.PLUGIN_VERSION)

    def do_tst(self, return_val, pattern_to_search):
        try:
            out = StringIO()
            sys.stdout = out
            check_poller2livestatus.main()
        except SystemExit, e:
            self.assertEquals(type(e), type(SystemExit()))
            self.assertEquals(e.code, return_val)
            output = out.getvalue().strip()
            matches = re.search(pattern_to_search, output)
            assert matches is not None

    def test_connection(self):
        """Test connection :
        -B 127.0.0.1 -H myhost -p mypoller -v
        """
        time.sleep(1)
        sys.argv = [sys.argv[0]]
        sys.argv.append('-B')
        sys.argv.append('127.0.0.1')
        sys.argv.append('-H')
        sys.argv.append('myhost')
        sys.argv.append('-p')
        sys.argv.append('mypoller')
        sys.argv.append('-v')
        self.do_tst(1, "Error while connecting to livestatus")

    def test_bad_arguments_1(self):
        """Test Bad arguments 1 :
        -B 127.0.0.1 -p mypoller -v
        """
        # First launch the netcat "web server"
        now = int(time.time())
        os.system("nc.traditional -l -p 50001 -c 'echo myhost\;myservice\;%d\;5' &" % now)

        time.sleep(1)
        sys.argv = [sys.argv[0]]
        sys.argv.append('-B')
        sys.argv.append('127.0.0.1')
        sys.argv.append('-P')
        sys.argv.append('50001')
        sys.argv.append('-S')
        sys.argv.append('myservice')
        sys.argv.append('-p')
        sys.argv.append('mypoller')
        self.do_tst(3, "Argument 'hostname'")

    def test_connection_ok(self):
        """Test connection ok :
        -B 127.0.0.1 -H myhost -p mypoller -v
        """
        # First launch the netcat "web server"
        now = int(time.time())
        os.system("nc.traditional -l -p 50001 -c 'echo myhost\;myservice\;%d\;5' &" % now)

        time.sleep(1)
        sys.argv = [sys.argv[0]]
        sys.argv.append('-B')
        sys.argv.append('127.0.0.1')
        sys.argv.append('-P')
        sys.argv.append('50001')
        sys.argv.append('-H')
        sys.argv.append('myhost')
        sys.argv.append('-S')
        sys.argv.append('myservice')
        sys.argv.append('-p')
        sys.argv.append('mypoller')
        self.do_tst(0, "")

    def test_connection_ok_check(self):
        """Test connection ok check :
        -B 127.0.0.1 -H myhost -p mypoller -C -v
        """
        # First launch the netcat "web server"
        now = int(time.time())
        os.system("nc.traditional -l -p 50001 -c 'echo myhost\;myservice\;%d\;5' &" % now)

        time.sleep(1)
        sys.argv = [sys.argv[0]]
        sys.argv.append('-B')
        sys.argv.append('127.0.0.1')
        sys.argv.append('-P')
        sys.argv.append('50001')
        sys.argv.append('-H')
        sys.argv.append('myhost')
        sys.argv.append('-S')
        sys.argv.append('myservice')
        sys.argv.append('-p')
        sys.argv.append('mypoller')
        sys.argv.append('-C')
        sys.argv.append('-v')
        self.do_tst(0, "| delta=")

    def test_connection_warning(self):
        """Test connection warning
        -B 127.0.0.1 -H myhost -S myservice -p mypoller -w 60 -c 120 -v
        """
        # First launch the netcat "web server"
        now = int(time.time()) - 65
        os.system("nc.traditional -l -p 50000 -c 'echo myhost\;myservice\;%d\;5' &" % now)

        time.sleep(1)
        sys.argv = [sys.argv[0]]
        sys.argv.append('-B')
        sys.argv.append('127.0.0.1')
        sys.argv.append('-H')
        sys.argv.append('myhost')
        sys.argv.append('-S')
        sys.argv.append('myservice')
        sys.argv.append('-p')
        sys.argv.append('mypoller')
        sys.argv.append('-w')
        sys.argv.append('60')
        sys.argv.append('-c')
        sys.argv.append('120')
        sys.argv.append('-v')
        self.do_tst(1, "# delta:6[0-9]")

    def test_connection_critical(self):
        """Test connection critical
        -B 127.0.0.1 -H myhost -p mypoller -w 60 -c 120
        """
        # First launch the netcat "web server"
        now = int(time.time()) - 155
        os.system("nc.traditional -l -p 50000 -c 'echo myhost\;%d\;5' &" % now)

        time.sleep(1)
        sys.argv = [sys.argv[0]]
        sys.argv.append('-B')
        sys.argv.append('127.0.0.1')
        sys.argv.append('-H')
        sys.argv.append('myhost')
        sys.argv.append('-p')
        sys.argv.append('mypoller')
        sys.argv.append('-w')
        sys.argv.append('60')
        sys.argv.append('-c')
        sys.argv.append('120')
        self.do_tst(2, "# delta:15[0-9]")

    def test_bad_arguments_2(self):
        """Test Bad arguments 2 :
        -B 127.0.0.1 -H myhost -p mypoller -v -P mybadport
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('-B')
        sys.argv.append('127.0.0.1')
        sys.argv.append('-H')
        sys.argv.append('myhost')
        sys.argv.append('-p')
        sys.argv.append('mypoller')
        sys.argv.append('-v')
        sys.argv.append('-P')
        sys.argv.append('mybadport')
        self.do_tst(3, "Argument `broker-port'")

    def test_bad_arguments_3(self):
        """Test test_bad_arguments_3 :
        -B 127.0.0.1 -H myhost -p mypoller -w 60 -c 55
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('-B')
        sys.argv.append('127.0.0.1')
        sys.argv.append('-H')
        sys.argv.append('myhost')
        sys.argv.append('-p')
        sys.argv.append('mypoller')
        sys.argv.append('-w')
        sys.argv.append('60')
        sys.argv.append('-c')
        sys.argv.append('55')
        self.do_tst(3, "Warning threshold must be less than CRITICAL threshold")

    def test_bad_arguments_4(self):
        """Test test_bad_arguments_4 :
        -B 127.0.0.1 -H myhost -w 60 -c bad_critical
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('-B')
        sys.argv.append('127.0.0.1')
        sys.argv.append('-H')
        sys.argv.append('myhost')
        sys.argv.append('-w')
        sys.argv.append('60')
        sys.argv.append('-c')
        sys.argv.append('bad_critical')
        self.do_tst(3, "Argument `critical': Bad format !")

if __name__ == '__main__':
    unittest.main()
