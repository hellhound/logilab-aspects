# -*- coding: ISO-8859-1 -*-
# pylint: disable-msg=C0103,W0232,R0904,R0801
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
Unit tests for prototypes
"""

__revision__ = '$Id: unittest_proto.py,v 1.13 2005-12-30 16:29:15 adim Exp $'


import unittest
import sys

from logilab.aspects.prototypes import reassign_function_arguments

class TestClass:
    """Class for prototype's tests
    """
    
    def f_noarg(self) :
        """
        function with no argument
        """
        pass
    
    def f_onearg(self, arg1) :
        """
        function with one argument
        """
        pass

    def f_twoargs(self, arg1, arg2) :
        """
        function with two arguments
        """
        pass

    def f_default(self, default = 1) :
        """
        function with one default argument
        """
        pass

    def f_onearg_and_default(self, arg1, default = 1) :
        """
        function with one argument and one default argument
        """
        pass



class ReassignTC(unittest.TestCase):
    """TestCase for prototypes
    """

    def setUp(self):
        """instantiates TestClass
        """
        self.foo = TestClass()

        
    def test_noarg(self):
        """Tests if reassign works correctly with no args 
        """
        varargs = ()
        kwargs = {}
        method = getattr(self.foo,'f_noarg')
        var_dict = reassign_function_arguments(method, varargs, kwargs)
        self.assert_(var_dict == {})

        
    def test_onearg(self):
        """Tests if reassign works correctly with one arg
        """
        varargs = (12,)
        kwargs = {}
        method = getattr(self.foo,'f_onearg')
        var_dict = reassign_function_arguments(method, varargs, kwargs)
        self.assert_(var_dict['arg1'] == 12)
        self.assert_(len(var_dict) == 1)
        

    def test_twoargs(self):
        """Tests if reassign works correctly with two args
        """
        varargs = (12, 13)
        kwargs = {}
        method = getattr(self.foo,'f_twoargs')
        var_dict = reassign_function_arguments(method, varargs, kwargs)
        self.assert_(var_dict['arg1'] == 12)
        self.assert_(var_dict['arg2'] == 13)
        self.assert_(len(var_dict) == 2)


    def test_default(self):
        """Tests if reassign works correctly with default arg
        """
        varargs = ()
        kwargs = {}
        method = getattr(self.foo,'f_default')
        var_dict = reassign_function_arguments(method, varargs, kwargs)
        self.assert_(var_dict['default'] == 1)
        self.assert_(len(var_dict) == 1)


    def test_onearg_and_default(self):
        """Tests if reassign works correctly with one arg and default 
        """
        varargs = (12,)
        kwargs = {}
        method = getattr(self.foo,'f_onearg_and_default')
        var_dict = reassign_function_arguments(method, varargs, kwargs)
        self.assert_(var_dict['arg1'] == 12)
        self.assert_(var_dict['default'] == 1)
        self.assert_(len(var_dict) == 2)
        var_dict = reassign_function_arguments(method, (12, 13), kwargs)
        self.assert_(var_dict['arg1'] == 12)
        self.assert_(var_dict['default'] == 13)
        self.assert_(len(var_dict) == 2)

    def test_keyword(self):
        """Tests if reassign works correctly with a keyword arg
        """
        varargs = ()
        kwargs = {'default' : 12}
        method = getattr(self.foo,'f_default')
        var_dict = reassign_function_arguments(method, varargs, kwargs)
        self.assert_(var_dict['default'] == 12)
        self.assert_(len(var_dict) == 1)
        

    def test_onearg_and_keyword(self):
        """Tests if reassign works correctly with one arg and keyword 
        """
        varargs = (12,)
        kwargs = {'default' : 13}
        method = getattr(self.foo,'f_onearg_and_default')
        var_dict = reassign_function_arguments(method, varargs, kwargs)
        self.assert_(var_dict['arg1'] == 12)
        self.assert_(var_dict['default'] == 13)
        self.assert_(len(var_dict) == 2)


    def test_named_params(self):
        """tests calling f by naming all arguments"""
        varargs = ()
        kwargs = {'arg1' : "arg1_val", 'default' : "default_val"}
        method = getattr(self.foo,'f_onearg_and_default')
        var_dict = reassign_function_arguments(method, varargs, kwargs)
        self.assertEquals(kwargs, var_dict)


    def test_too_many_parameters(self):
        method = getattr(self.foo, 'f_twoargs')
        self.assertRaises(TypeError, reassign_function_arguments, method,
                          (1, 2, 3, 4), {})
    
    

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
