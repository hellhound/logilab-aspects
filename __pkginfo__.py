# -*- coding: ISO-8859-1 -*-
# pylint: disable-msg=W0622
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

"""
Logilab - www.logilab.fr - www.logilab.org - www.logilab.com
"""

modname = "aspects"
distname = 'logilab-aspects'
debian_name = 'logilab-aspects'

numversion = (0, 1, 4)
version = '%s.%s.%s' % numversion

license = 'GPL'
copyright = '''Copyright © 2001-2006 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr'''


short_desc = "aspect Programming with Python"
long_desc = """aspects is a module that enables Aspect Oriented Programming
with Python.
It also provides an implementation of 'Design By Contract' programming using
aspects.
"""

author = "Adrien Di Mascio"
author_email = "Adrien.DiMascio@logilab.fr"

ftp = 'ftp://ftp.logilab.org/pub/aspects/'
web = "http://www.logilab.org/projects/aspects/"
mailinglist = 'mailto://python-projects@lists.logilab.org'

pyversions = ["2.3", "2.4"]

subpackage_of = 'logilab'
