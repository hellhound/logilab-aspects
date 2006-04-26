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

"""
Unit tests for aspects
"""

__revision__ = '$Id: unittest_aspects.py,v 1.24 2005-12-30 16:29:12 adim Exp $'


import unittest
import sys

from logilab.aspects.weaver import weaver

from logilab.aspects.core import AbstractAspect


class EmptyAspect(AbstractAspect):
    """An empty aspect class to test if method wrapping
    is well done.
    """

    before_flag = 1
    around_flag = 2
    after_flag = 4
    proceed_flag = 8
    
    def __init__(self, pointcut, arg1, arg2):
        """arg1 and arg2 are here to test that the aspect can
        be be built with additional args
        """
        AbstractAspect.__init__(self, pointcut)
        self.arg1 = arg1
        self.arg2 = arg2
        # A flag to test if wrapping methods are called
        self.trace_flag = 0
        

    def before(self, wobj, context, *args, **kwargs):
        """Before method
        """
        self.trace_flag |= EmptyAspect.before_flag


    def after(self, wobj, context, *args, **kwargs):
        """After method
        """
        self.trace_flag |= EmptyAspect.after_flag


    def around(self, wobj, context, *args, **kwargs):
        """Around method
        """
        self.trace_flag |= EmptyAspect.around_flag
        method_name = context['method_name']
        wclass = context['__class__']
        self._proceed(wobj, wclass, method_name, *args, **kwargs)
        
        

class Foo:
    """A simple class to tests aspects
    """

    def silly_method(self):
        """Just for tests, does nothing
        """
        pass


    def raise_exception(self):
        """Just for tests, does nothing
        """
        raise ValueError('Yop')



class AspectTC(unittest.TestCase):
    """TestCase for aspects
    """

    def setUp(self):
        """setUp method for tests
        """
        self.foo = Foo()
        weaver.weave_methods(self.foo, EmptyAspect, 10, 20)
        self.aspect = weaver.get_aspects(self.foo, 'silly_method')[0]
        

    def test_aspect_init(self):
        """Tests if aspect's init is well done with additional args
        """
        self.assert_(self.aspect.arg1 == 10)
        self.assert_(self.aspect.arg2 == 20)
        

    def test_method_wrapping(self):
        """Tests if methods are well wrapped
        """
        ok_val = EmptyAspect.before_flag | EmptyAspect.after_flag | \
                 EmptyAspect.around_flag
        self.foo.silly_method()
        self.assert_(self.aspect.trace_flag == ok_val)
        

    def test_exception_management(self):
        """Tests if exception are re-raised
        """
        self.assertRaises(ValueError, self.foo.raise_exception)
        


def suite():
    """return the unitest suite"""
    loader = unittest.TestLoader()
    testsuite = loader.loadTestsFromModule(sys.modules[__name__])
    return testsuite
    
    
def Run(runner=None):
    """run tests"""
    testsuite = suite()
    if runner is None:
        runner = unittest.TextTestRunner()
    return runner.run(testsuite)
    
if __name__ == '__main__':
    Run()

