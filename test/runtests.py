# -*- coding: ISO-8859-1 -*-
# pylint: disable-msg=C0103,W0613,W0142,W0232,R0801
# Copyright (c) 2003-2006 LOGILAB S.A. (Paris, FRANCE).
# http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

"""Script used to fire all tests"""

__revision__ = '$Id: runtests.py,v 1.4 2005-12-30 16:29:12 adim Exp $'

from logilab.common.testlib import main

if __name__ == '__main__':
    import sys, os
    main(os.path.dirname(sys.argv[0]) or '.')
