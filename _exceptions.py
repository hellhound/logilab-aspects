# -*- coding: ISO-8859-1 -*-
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
Aspect Exception Module
"""

__revision__ = '$Id: _exceptions.py,v 1.12 2005-12-30 16:29:02 adim Exp $'


class AspectFailure(Exception):
    """Raised when an aspect could not be ran correctly
    """

    def __init__(self, msg):
        """Initialises self.method_execption
        msg : the error message
        """
        Exception.__init__(self, msg)
        self.method_exception = None
        self.msg = msg

    def set_method_exception(self, excpt):
        """Memorizes which exception has been raised
        by the wrapped method
        """
        self.method_exception = excpt

    

class WrapException(Exception):
    """Raised when was unable to wrap a method
    """
    pass


class AlreadyAspectedError(Exception):
    """Raised when a class / method is already aspected
    by the same aspect.
    """
    pass


class ClassNotWeaved(Exception):
    """Raised when trying to access a method whose class is not
    aspected. (in weaver.__woven_dict)
    """
    pass


