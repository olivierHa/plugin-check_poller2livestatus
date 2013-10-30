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
#import os
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
        sys.argv = [sys.argv[0]]
        sys.argv.append('-B')
        sys.argv.append('127.0.0.1')
        sys.argv.append('-H')
        sys.argv.append('myhost')
        sys.argv.append('-p')
        sys.argv.append('mypoller')
        sys.argv.append('-v')
        self.do_tst(2, "Error while connecting to livestatus")

if __name__ == '__main__':
    unittest.main()
